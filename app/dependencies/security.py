from app.db.db import get_session
from app.core.jwt import UserJWT
from app.models.user import User

from sqlalchemy.exc import NoResultFound
from sqlalchemy import select

from app.exceptions.auth_exceptions import NoAccountError, ExpiredJWTError, BadJWTError
from jwt import ExpiredSignatureError, InvalidTokenError

from sqlalchemy.orm import Session

from fastapi import Header, Depends, status
from fastapi.exceptions import HTTPException

def verify_jwt(authorization: str = Header(...), db: Session = Depends(get_session), user_jwt: UserJWT = Depends(UserJWT)):
    try:
        if not authorization.startswith("Bearer "):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No JWT")
        token = authorization.removeprefix("Bearer ").strip()
        id = user_jwt.decode_jwt(token)
        stmt = select(User).where(id == User.id)
        user = db.execute(statement=stmt).scalar_one()
        return user.id
    except NoResultFound:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No account")
    except ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Expired token")
    except InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid JWT")
    except Exception as e:
        print(e)
        raise e 