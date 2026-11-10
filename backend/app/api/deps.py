from typing import Generator, Optional, List
from datetime import datetime, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.core.database import get_db
from app.core.security import decode_token
from app.models.user import User, Learner, AuditLog
from app.middleware.correlation import get_current_correlation_id

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_token(token)
    if payload is None:
        raise credentials_exception
    
    user_id: str = payload.get("sub")
    token_type: str = payload.get("type")
    if user_id is None or token_type != "access":
        raise credentials_exception
        
    user = db.scalar(select(User).where(User.id == user_id))
    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user account")
    return user

def require_roles(allowed_roles: List[str]):
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access forbidden: requires one of roles {allowed_roles}"
            )
        return current_user
    return role_checker

def get_current_admin(current_user: User = Depends(require_roles(["admin"]))) -> User:
    return current_user

def get_current_learner(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Learner:
    learner = db.scalar(select(Learner).where(Learner.user_id == current_user.id))
    if not learner and current_user.role == "learner":
        # Create profile automatically if missing
        learner = Learner(user_id=current_user.id)
        db.add(learner)
        db.commit()
        db.refresh(learner)
    elif not learner:
        # For admin/mentor accessing learner endpoint without profile
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Learner profile not associated with this account"
        )
    return learner

def create_audit_log(
    db: Session,
    user_id: Optional[str],
    action: str,
    entity_name: str,
    entity_id: Optional[str] = None,
    ip_address: Optional[str] = None,
    details: Optional[dict] = None
):
    """Save an immutable audit record."""
    audit = AuditLog(
        user_id=user_id,
        action=action,
        entity_name=entity_name,
        entity_id=entity_id,
        correlation_id=get_current_correlation_id(),
        ip_address=ip_address,
        details=details or {},
        created_at=datetime.now(timezone.utc).isoformat()
    )
    db.add(audit)
    db.commit()
