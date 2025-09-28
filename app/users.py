from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    username: str
    email: str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


class UserPublic(BaseModel):
    username: str
    email: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = Field(default="bearer")


@dataclass
class UserInDB:
    username: str
    email: str
    password_hash: str


class UsersStore:
    def __init__(self) -> None:
        self._by_username: Dict[str, UserInDB] = {}
        self._by_email: Dict[str, UserInDB] = {}

    def get_by_username(self, username: str) -> Optional[UserInDB]:
        return self._by_username.get(username.lower())

    def get_by_email(self, email: str) -> Optional[UserInDB]:
        return self._by_email.get(email.lower())

    def create_user(self, username: str, email: str, password_hash: str) -> UserInDB:
        key_u = username.lower()
        key_e = email.lower()
        if key_u in self._by_username:
            raise ValueError("Username already exists")
        if key_e in self._by_email:
            raise ValueError("Email already exists")
        user = UserInDB(username=username, email=email, password_hash=password_hash)
        self._by_username[key_u] = user
        self._by_email[key_e] = user
        return user


# Global in-memory store (replace with DB in production)
users_store = UsersStore()

