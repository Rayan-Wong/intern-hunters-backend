from fastapi import APIRouter, Depends, HTTPException, Response, status
from app.services.auth_service import UserAuth
from app.schemas.user import UserCreate, UserLogin, UserToken
from app.core.jwt import TokenPayload