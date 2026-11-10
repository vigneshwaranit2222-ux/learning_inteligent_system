from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.core.database import get_db
from app.core.security import (
    hash_password, verify_password,
    create_access_token, create_refresh_token, decode_token
)
from app.models.user import User, Learner
from app.schemas.auth import (
    Token, LoginRequest, RegisterRequest, RefreshTokenRequest,
    ForgotPasswordRequest, ResetPasswordRequest
)
from app.schemas.user import UserResponse
from app.api.deps import get_current_user, create_audit_log

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    # Check if user already exists
    existing = db.scalar(select(User).where(User.email == req.email))
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email address already exists."
        )

    user = User(
        email=req.email,
        hashed_password=hash_password(req.password),
        full_name=req.full_name,
        role=req.role if req.role in ["learner", "mentor", "admin"] else "learner",
        is_active=True
    )
    db.add(user)
    db.flush()

    learner_id = None
    if user.role == "learner":
        learner = Learner(
            user_id=user.id,
            headline=req.headline or "Lifelong Learner",
            target_role=req.target_role or "Software Engineer"
        )
        db.add(learner)
        db.flush()
        learner_id = learner.id

    db.commit()

    create_audit_log(db, user.id, "USER_REGISTERED", "users", user.id, details={"email": user.email, "role": user.role})

    access_token = create_access_token(user.id, user.role)
    refresh_token = create_refresh_token(user.id, user.role)

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        role=user.role,
        user_id=user.id,
        learner_id=learner_id,
        full_name=user.full_name
    )

@router.post("/login", response_model=Token)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == req.email))
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Account is deactivated")

    learner_id = None
    if user.role == "learner":
        learner = db.scalar(select(Learner).where(Learner.user_id == user.id))
        if learner:
            learner_id = learner.id

    create_audit_log(db, user.id, "USER_LOGGED_IN", "users", user.id)

    access_token = create_access_token(user.id, user.role)
    refresh_token = create_refresh_token(user.id, user.role)

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        role=user.role,
        user_id=user.id,
        learner_id=learner_id,
        full_name=user.full_name
    )

@router.post("/refresh", response_model=Token)
def refresh_token(req: RefreshTokenRequest, db: Session = Depends(get_db)):
    payload = decode_token(req.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    user_id = payload.get("sub")
    user = db.scalar(select(User).where(User.id == user_id))
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User account inactive or missing")

    learner_id = None
    if user.role == "learner":
        learner = db.scalar(select(Learner).where(Learner.user_id == user.id))
        if learner:
            learner_id = learner.id

    new_access_token = create_access_token(user.id, user.role)
    new_refresh_token = create_refresh_token(user.id, user.role)

    return Token(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        role=user.role,
        user_id=user.id,
        learner_id=learner_id,
        full_name=user.full_name
    )

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.post("/forgot-password")
def forgot_password(req: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == req.email))
    # Return generic success to avoid email enumeration
    return {"message": "If this email is registered, password reset instructions have been dispatched."}

@router.post("/reset-password")
def reset_password(req: ResetPasswordRequest, db: Session = Depends(get_db)):
    payload = decode_token(req.token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired reset token")
    user_id = payload.get("sub")
    user = db.scalar(select(User).where(User.id == user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user.hashed_password = hash_password(req.new_password)
    db.commit()
    create_audit_log(db, user.id, "PASSWORD_RESET", "users", user.id)
    return {"message": "Password updated successfully"}
