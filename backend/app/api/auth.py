from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import create_access_token, get_current_user, get_password_hash, verify_password
from app.models.audit_log import AuditLog
from app.models.user import User
from app.schemas.auth import TokenResponse, UserCreate, UserLogin

router = APIRouter(prefix="/auth", tags=["auth"])


def log_audit(db: Session, user_id: int | None, action: str, resource: str, resource_id: str | None = None, ip_address: str = "127.0.0.1", metadata: dict | None = None):
    db.add(AuditLog(user_id=user_id, action=action, resource=resource, resource_id=resource_id, ip_address=ip_address, metadata_json=metadata or {}))
    db.commit()


@router.post("/register", response_model=TokenResponse)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")
    user = User(
        name=payload.name,
        email=str(payload.email),
        password_hash=get_password_hash(payload.password),
        role="USER",
        is_active=True,
    )
    db.add(user)
    db.commit(); db.refresh(user)
    token = create_access_token(user.email)
    log_audit(db, user.id, "user_creation", "users", str(user.id), metadata={"role": user.role})
    return TokenResponse(access_token=token, user={"id": user.id, "name": user.name, "email": user.email, "role": user.role, "is_active": user.is_active})


@router.post("/login", response_model=TokenResponse)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == str(payload.email)).first()
    if not user or not verify_password(payload.password, user.password_hash):
        log_audit(db, None, "failed_login", "auth", payload.email, metadata={"reason": "invalid_credentials"})
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    user.last_login = datetime.utcnow()
    db.add(user)
    db.commit()
    token = create_access_token(user.email)
    log_audit(db, user.id, "login", "auth", str(user.id), metadata={"status": "success"})
    return TokenResponse(access_token=token, user={"id": user.id, "name": user.name, "email": user.email, "role": user.role, "is_active": user.is_active})


@router.post("/logout")
def logout(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    log_audit(db, current_user.id, "logout", "auth", str(current_user.id), metadata={"status": "success"})
    return {"success": True, "message": "Logged out successfully"}
