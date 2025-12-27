from fastapi import APIRouter, HTTPException, status, Request, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session
from typing import Optional

from ...models.database import get_db
from ...models.user import User
from ...services.auth import hash_password, verify_password, create_session, verify_session
from ...api.middleware.logging import structured_logger
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded


limiter = Limiter(key_func=get_remote_address)
router = APIRouter(prefix="/api/auth", tags=["Authentication"])


class RegisterRequest(BaseModel):
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="Password (min 8 characters)")


class SignInRequest(BaseModel):
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class UserResponse(BaseModel):
    user_id: str
    email: str
    message: str


@router.post("/register", status_code=status.HTTP_201_CREATED)
@limiter.limit("10/hour")
async def register(
    request: Request,
    user_data: RegisterRequest,
    db: Session = next(get_db())
):
    """
    Register a new user account.

    Creates a new user with email and password. Email must be unique.
    Password is hashed using bcrypt with work factor 12.
    """
    try:
        # Check if email already exists
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            structured_logger.log_auth_event(
                "registration_failed",
                email=user_data.email,
                reason="email_already_exists"
            )
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already in use"
            )

        # Hash password
        password_hash = hash_password(user_data.password)

        # Create new user
        new_user = User(
            email=user_data.email,
            password_hash=password_hash
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        structured_logger.log_auth_event(
            "registration_success",
            email=user_data.email,
            user_id=new_user.id
        )

        return UserResponse(
            user_id=new_user.id,
            email=new_user.email,
            message="Account created successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        structured_logger.log_error(
            "registration_error",
            email=user_data.email,
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create account. Please try again."
        )


@router.post("/sign-in")
@limiter.limit("10/5minutes")
async def sign_in(
    request: Request,
    credentials: SignInRequest,
    response: Response,
    db: Session = next(get_db())
):
    """
    Sign in with email and password.

    Verifies credentials and creates a session cookie (httpOnly, secure, SameSite=lax).
    Session expires after 7 days.
    """
    try:
        # Find user by email
        user = db.query(User).filter(User.email == credentials.email).first()

        if not user:
            structured_logger.log_auth_event(
                "signin_failed",
                email=credentials.email,
                reason="user_not_found"
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        # Verify password
        if not verify_password(credentials.password, user.password_hash):
            structured_logger.log_auth_event(
                "signin_failed",
                email=credentials.email,
                user_id=user.id,
                reason="invalid_password"
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        # Create session
        session_data = create_session(
            db=db,
            user_id=user.id,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent")
        )

        structured_logger.log_auth_event(
            "signin_success",
            email=credentials.email,
            user_id=user.id,
            session_id=session_data["id"]
        )

        # Set httpOnly, secure, SameSite=lax cookie
        response = JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "user_id": user.id,
                "email": user.email,
                "message": "Signed in successfully"
            }
        )

        # Set session cookie with proper attributes
        max_age = 60 * 60 * 24 * 7  # 7 days in seconds
        response.set_cookie(
            key="session_token",
            value=session_data["session_token"],
            max_age=max_age,
            expires=session_data["expires_at"],
            path="/",
            domain=None,  # Let browser use current domain
            secure=True,  # Only send over HTTPS
            httponly=True,  # Not accessible via JavaScript
            samesite="lax"  # Protects against CSRF
        )

        return response

    except HTTPException:
        raise
    except RateLimitExceeded as e:
        structured_logger.log_auth_event(
            "signin_rate_limited",
            email=credentials.email,
            limit=str(e.detail)
        )
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many sign-in attempts. Please try again later.",
            headers={"Retry-After": "300"}  # 5 minutes
        )
    except Exception as e:
        structured_logger.log_error(
            "signin_error",
            email=credentials.email,
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Sign in failed. Please try again."
        )


@router.post("/sign-out")
async def sign_out(
    request: Request,
    response: Response,
    db: Session = next(get_db())
):
    """
    Sign out and terminate session.

    Invalidates session and clears session cookie.
    Requires valid session token in cookie.
    """
    try:
        # Extract session token from cookie
        session_token = request.cookies.get("session_token")

        if not session_token:
            structured_logger.log_auth_event(
                "signout_failed",
                reason="no_session_token"
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated"
            )

        # Verify session and get user
        user = verify_session(db, session_token)

        if not user:
            structured_logger.log_auth_event(
                "signout_failed",
                reason="invalid_session_token"
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated"
            )

        # Delete session from database
        from ...models.session import Session as SessionModel
        db.query(SessionModel).filter(
            SessionModel.session_token == session_token
        ).delete()
        db.commit()

        structured_logger.log_auth_event(
            "signout_success",
            user_id=user.id,
            session_token=session_token[:10] + "..."  # Log only prefix for security
        )

        # Clear session cookie
        response = JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Signed out successfully"}
        )

        # Clear cookie by setting Max-Age=0
        response.delete_cookie(
            key="session_token",
            path="/",
            secure=True,
            httponly=True,
            samesite="lax"
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        structured_logger.log_error(
            "signout_error",
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Sign out failed. Please try again."
        )
