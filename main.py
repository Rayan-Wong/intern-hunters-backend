from typing import Union, Annotated
from functools import lru_cache

from fastapi import FastAPI, Depends, APIRouter
from fastapi.security import OAuth2PasswordBearer

import jwt
from pydantic import BaseModel

router = APIRouter(prefix="/api")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.get("/")
def read_root():
    return {"Hello": "World"}


@router.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

@router.get("/token/")
async def read_item(token: Annotated[str, Depends(oauth2_scheme)]):
    return {"token": token}

app = FastAPI()
app.include_router(router)