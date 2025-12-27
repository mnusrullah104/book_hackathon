import pytest
from fastapi import Request
from ...api.middleware.auth import AuthMiddleware
from unittest.mock import Mock, patch

def test_missing_token_returns_401():
    request = Mock(spec=Request)
    request.cookies = {}
    request.url = Mock(path="/api/chat/message")

    middleware = AuthMiddleware(app)

    with patch.object(middleware, 'call_next') as mock_call_next:
        mock_call_next.return_value = Mock()
        result = middleware.dispatch(request, mock_call_next)

        assert result.status_code == 401

def test_invalid_token_returns_401():
    request = Mock(spec=Request)
    request.cookies = {"session_token": "invalid_token"}
    request.url = Mock(path="/api/chat/message")

    middleware = AuthMiddleware(app)

    with patch.object(middleware, 'call_next') as mock_call_next:
        with patch('...services.auth.verify_session', return_value=None):
            mock_call_next.return_value = Mock()
            result = middleware.dispatch(request, mock_call_next)

            assert result.status_code == 401
