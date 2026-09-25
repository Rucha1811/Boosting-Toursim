from typing import Optional

from fastapi import Depends, Header, HTTPException, WebSocket
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..core.destinations import DEFAULT_DESTINATION_ID, normalized_dest_id
from ..core.security import decode_token
from ..models import User

bearer_scheme = HTTPBearer(auto_error=False)


def get_header_destination_id(
    x_destination_id: Optional[int] = Header(default=None, alias="X-Destination-Id"),
    db: Session = Depends(get_db),
) -> int:
    """Resolve the active destination for write endpoints.

    Honors the `X-Destination-Id` header, defaulting to the canonical demo
    destination (Vadodara) so existing clients keep working unchanged.
    """
    if x_destination_id is None:
        return DEFAULT_DESTINATION_ID
    return normalized_dest_id(db, x_destination_id)


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise HTTPException(status_code=401, detail="Authentication required")
    payload = decode_token(credentials.credentials)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user = db.query(User).filter(User.id == int(payload["sub"])).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user


def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """Like get_current_user but returns None for anonymous requests."""
    if credentials is None:
        return None
    payload = decode_token(credentials.credentials)
    if payload is None:
        return None
    return db.query(User).filter(User.id == int(payload["sub"])).first()


def require_roles(*roles: str):
    def _checker(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise HTTPException(status_code=403, detail=f"Role '{user.role}' not permitted")
        return user

    return _checker


def is_authority(user: User) -> bool:
    return user.role in ("authority_admin", "authority_officer")


async def authenticate_ws(websocket: WebSocket) -> Optional[dict]:
    token = websocket.query_params.get("token")
    if not token:
        return None
    return decode_token(token)