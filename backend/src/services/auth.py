import secrets
from datetime import datetime, timedelta
from passlib.context import CryptContext
from sqlalchemy.orm import Session

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)

def create_session(db: Session, user_id: str, ip_address: str = None, user_agent: str = None) -> dict:
    session_token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(days=7)

    from ..models.session import Session as SessionModel
    session = SessionModel(
        user_id=user_id,
        session_token=session_token,
        expires_at=expires_at,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    return {
        "id": session.id,
        "session_token": session_token,
        "expires_at": expires_at.isoformat()
    }

def verify_session(db: Session, session_token: str):
    from ..models.session import Session as SessionModel
    from ..models.user import User

    session = db.query(SessionModel).filter(
        SessionModel.session_token == session_token,
        SessionModel.expires_at > datetime.utcnow()
    ).first()

    if not session:
        return None

    user = db.query(User).filter(User.id == session.user_id).first()
    return user
