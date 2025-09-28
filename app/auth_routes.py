from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException, status

from .auth import create_jwt, hash_password, verify_jwt, verify_password
from .users import LoginRequest, TokenResponse, UserCreate, UserPublic, users_store


router = APIRouter(prefix="/auth", tags=["auth"])


# In a real deployment, inject via config/secret manager
JWT_SECRET = "dev-secret-change-me"


def get_current_user(authorization: Optional[str] = Header(default=None)) -> UserPublic:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")
    token = authorization.split(" ", 1)[1]
    payload = verify_jwt(token, JWT_SECRET)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    username = payload.get("sub")
    if not username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user_db = users_store.get_by_username(username)
    if not user_db:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return UserPublic(username=user_db.username, email=user_db.email)


@router.post("/signup", response_model=UserPublic)
def signup(req: UserCreate) -> UserPublic:
    pwd_hash = hash_password(req.password)
    try:
        user = users_store.create_user(req.username, req.email, pwd_hash)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return UserPublic(username=user.username, email=user.email)


@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest) -> TokenResponse:
    user_db = users_store.get_by_username(req.username)
    if not user_db or not verify_password(req.password, user_db.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_jwt({"sub": user_db.username}, JWT_SECRET, expires_in_seconds=3600 * 24)
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserPublic)
def me(current_user: UserPublic = Depends(get_current_user)) -> UserPublic:
    return current_user

