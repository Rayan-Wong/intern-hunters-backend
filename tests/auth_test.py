"""Modules relevent for FastAPI testing and constructing mocks"""
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import status
from httpx import AsyncClient
import pytest
import jwt

from tests.conftest import client, get_jwt_secrets, UserTest, good_user, get_session_token_secrets

class BadJWTConstructor:
    """Bad JWT Constructor"""
    def __init__(self, sub, iat, exp):
        self.sub = sub
        self.iat = iat
        self.exp = exp
        self.__secret_key = get_jwt_secrets()
        self.__algorithm = "HS256"
    def generate_token(self):
        """Generates bad JWT token"""
        payload = {"sub": self.sub,
            "iat": self.iat,
            "exp": self.exp
        }
        return jwt.encode(payload, key=self.__secret_key, algorithm=self.__algorithm)

class BadSessionTokenConstructor:
    """Bad Session Token Constructor"""
    def __init__(self, sub, iat, exp):
        self.sub = sub
        self.iat = iat
        self.exp = exp
        self.__secret_key = get_session_token_secrets()
        self.__algorithm = "HS256"
    def generate_token(self):
        """Generates bad session token"""
        payload = {"sub": self.sub,
            "iat": self.iat,
            "exp": self.exp
        }
        return jwt.encode(payload, key=self.__secret_key, algorithm=self.__algorithm)

@pytest.fixture
def no_account_user():
    """Returns user with email not in mock db"""
    return UserTest(
        name="admin",
        email="urdad@gmail.com",
        encrypted_password="password"
    )

@pytest.fixture
def wrong_password_user():
    """Returns user with correct email but wrong password"""
    return UserTest(
        name="admin",
        email="urmum@gmail.com",
        encrypted_password="pasword"
    )

@pytest.fixture
def expired_token():
    """Returns JWT with valid credentials but expired"""
    def _create(user_id: str):
        return BadJWTConstructor(
            sub=user_id,
            exp=datetime.now(timezone.utc),
            iat=datetime.now(timezone.utc) - timedelta(minutes=45)
        ).generate_token()
    return _create

@pytest.fixture
def no_account_token():
    """Returns JWT with invalid user ID"""
    return BadJWTConstructor(
        sub=str(uuid.uuid4()),
        exp=datetime.now(timezone.utc) + timedelta(minutes=30),
        iat=datetime.now(timezone.utc)
    ).generate_token()

@pytest.fixture
def expired_session_token():
    """Returns session token with valid credentials but expired"""
    def _create(session_id: str):
        return BadSessionTokenConstructor(
            sub=session_id,
            exp=datetime.now(timezone.utc),
            iat=datetime.now(timezone.utc) - timedelta(minutes=45)
        ).generate_token()
    return _create

@pytest.fixture
def no_account_session_token():
    """Returns JWT with invalid user ID"""
    return BadSessionTokenConstructor(
        sub=str(uuid.uuid4()),
        exp=datetime.now(timezone.utc) + timedelta(minutes=30),
        iat=datetime.now(timezone.utc)
    ).generate_token()

# these tests are done on a mock db, so no cybersecurity flaws here

@pytest.mark.asyncio
async def test_read_main(client: AsyncClient):
    """Checks if server is alive"""
    response = await client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "ur mum"}

@pytest.mark.asyncio
async def test_register(client: AsyncClient, good_user: UserTest):
    """Checks if valid user registration is successful"""
    response = await client.post("/api/register",
        json={"name": good_user.name,
            "email": good_user.email,
            "password": good_user.encrypted_password
        }
    )
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()
    assert response.cookies.get("refresh_token") is not None

@pytest.mark.asyncio
async def test_register_duplicate(client: AsyncClient, good_user: UserTest):
    """Checks if duplicate registrations fail"""
    await client.post("/api/register",
        json={"name": good_user.name,
            "email": good_user.email,
            "password": good_user.encrypted_password
        }
    )
    response = await client.post("/api/register",
        json={"name": good_user.name,
            "email": good_user.email,
            "password": good_user.encrypted_password
        }
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.asyncio
async def test_login(client: AsyncClient, good_user: UserTest):
    """Checks if user with valid credentials can log in"""
    response = await client.post("/api/login",
        json={"email": good_user.email,
            "password": good_user.encrypted_password
        }
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.cookies.get("refresh_token") is not None

@pytest.mark.asyncio
async def test_no_account_login(client: AsyncClient, no_account_user: UserTest):
    """Checks if user with wrong email fail to log in"""
    response = await client.post("/api/login",
        json={"email": no_account_user.email,
            "password": no_account_user.encrypted_password
        }
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST

@pytest.mark.asyncio
async def test_wrong_password_login(client: AsyncClient, wrong_password_user: UserTest):
    """Checks if user with correct email but wrong password fail to log in"""
    response = await client.post("/api/login",
        json={"email": wrong_password_user.email,
            "password": wrong_password_user.encrypted_password
        }
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.asyncio
async def test_good_token(client: AsyncClient, good_user: UserTest):
    """Checks if server accepts a JWT with good credentials"""
    response = await client.post("/api/login",
        json={"email": good_user.email,
            "password": good_user.encrypted_password
        }
    )
    assert "access_token" in response.json()
    token = response.json()["access_token"]
    result = await client.post("/api/test_login", headers={
        "Authorization": f"Bearer {token}"
    })
    assert result.status_code == status.HTTP_200_OK

@pytest.mark.asyncio
async def test_no_token(client: AsyncClient):
    """Checks if server rejects no token on protected routes"""
    response = await client.post("/api/test_login")
    assert response.status_code == status.HTTP_403_FORBIDDEN

@pytest.mark.asyncio
async def test_bad_token(client: AsyncClient):
    """Checks if server rejects empty token"""
    response = await client.post("/api/test_login", headers={
        "Authorization": "hi"
    })
    assert response.status_code == status.HTTP_403_FORBIDDEN

@pytest.mark.asyncio
async def test_expired_token(client: AsyncClient, good_user: UserTest, expired_token):
    """Checks if server rejects expired JWT with valid credentials"""
    res1 = await client.post("/api/login",
        json={"email": good_user.email,
            "password": good_user.encrypted_password
        }
    )
    token = res1.json()["access_token"]
    res2 = await client.post("/api/test_login", headers={
        "Authorization": f"Bearer {token}"
    })
    user_id = res2.json()
    old_token = expired_token(user_id)
    result = await client.post("/api/test_login", headers={
        "Authorization": f"Bearer {old_token}"
    })
    assert result.status_code == status.HTTP_407_PROXY_AUTHENTICATION_REQUIRED
    assert result.json()["detail"] == "Expired token"

@pytest.mark.asyncio
async def test_no_account_token(client: AsyncClient, no_account_token: str):
    """Checks if server rejects JWT with wrong email"""
    bad_token = no_account_token
    result = await client.post("/api/test_login", headers={
        "Authorization": f"Bearer {bad_token}"
    })
    assert result.status_code == status.HTTP_401_UNAUTHORIZED
    assert result.json()["detail"] == "No account"

@pytest.mark.asyncio
async def test_session_token(client: AsyncClient, good_user: UserTest, expired_token: str):
    """Checks if server successfully sends refresh JWT and rotates session token"""
    res1 = await client.post("/api/login",
        json={"email": good_user.email,
            "password": good_user.encrypted_password
        }
    )
    token = res1.json()["access_token"]
    res2 = await client.post("/api/test_login", headers={
        "Authorization": f"Bearer {token}"
    })
    user_id = res2.json()
    old_token = expired_token(user_id)
    result = await client.post("/api/token", headers={
        "Authorization": f"Bearer {old_token}"
    }, cookies={
        "refresh_token": res1.cookies.get("refresh_token")
    })
    assert result.status_code == status.HTTP_200_OK
    assert result.cookies.get("refresh_token") is not None

@pytest.mark.asyncio
async def test_no_session_token(client: AsyncClient, good_user: UserTest, expired_token: str):
    """Tests if no session token returns error 401"""
    # first login to get jwt and session tokn
    res1 = await client.post("/api/login",
        json={"email": good_user.email,
            "password": good_user.encrypted_password
        }
    )
    assert "access_token" in res1.json()
    token = res1.json()["access_token"]
    # get user id
    res2 = await client.post("/api/test_login", headers={
        "Authorization": f"Bearer {token}"
    })
    user_id = res2.json()
    old_token = expired_token(user_id)
    result = await client.post("/api/test_session_token", headers={
        "Authorization": f"Bearer {old_token}"
    })
    assert result.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

@pytest.mark.asyncio
async def test_invalid_session_token(client: AsyncClient, good_user: UserTest, expired_token: str):
    """Tests if invalid session token returns error 422"""
    # first login to get jwt and session tokn
    res1 = await client.post("/api/login",
        json={"email": good_user.email,
            "password": good_user.encrypted_password
        }
    )
    assert "access_token" in res1.json()
    token = res1.json()["access_token"]
    # get user id
    res2 = await client.post("/api/test_login", headers={
        "Authorization": f"Bearer {token}"
    })
    user_id = res2.json()
    old_token = expired_token(user_id)
    result = await client.post("/api/test_session_token", headers={
        "Authorization": f"Bearer {old_token}"
    }, cookies={
        "refresh_token": "hi"
    })
    assert result.status_code == status.HTTP_400_BAD_REQUEST
    assert result.json()["detail"] == "Invalid session token"

@pytest.mark.asyncio
async def test_expired_session_token(client: AsyncClient, good_user: UserTest, expired_token: str, expired_session_token: str):
    """Tests if expired session token returns error 401"""
    # first login to get jwt and session tokn
    res1 = await client.post("/api/login",
        json={"email": good_user.email,
            "password": good_user.encrypted_password
        }
    )
    assert "access_token" in res1.json()
    token = res1.json()["access_token"]
    # get user id
    res2 = await client.post("/api/test_login", headers={
        "Authorization": f"Bearer {token}"
    })
    user_id = res2.json()
    # get session id
    res3 = await client.post("/api/test_session_token", headers={
        "Authorization": f"Bearer {token}"
    }, cookies={
        "refresh_token": res1.cookies.get("refresh_token")
    })
    session_id = res3.json()
    # make expired jwt and session token
    old_token = expired_token(user_id)
    expired_refresh_token = expired_session_token(session_id)
    result = await client.post("/api/test_session_token", headers={
        "Authorization": f"Bearer {old_token}"
    }, cookies={
        "refresh_token": expired_refresh_token
    })
    assert result.status_code == status.HTTP_401_UNAUTHORIZED
    assert result.json()["detail"] == "Expired token"

@pytest.mark.asyncio
async def test_wrong_account_session_token(client: AsyncClient, good_user: UserTest, expired_token: str, no_account_session_token: str):
    """Tests if wrong session token returns error 401"""
    # first login to get jwt and session tokn
    res1 = await client.post("/api/login",
        json={"email": good_user.email,
            "password": good_user.encrypted_password
        }
    )
    assert "access_token" in res1.json()
    token = res1.json()["access_token"]
    # get user id
    res2 = await client.post("/api/test_login", headers={
        "Authorization": f"Bearer {token}"
    })
    user_id = res2.json()
    old_token = expired_token(user_id)
    result = await client.post("/api/test_session_token", headers={
        "Authorization": f"Bearer {old_token}"
    }, cookies={
        "refresh_token": no_account_session_token
    })
    assert result.status_code == status.HTTP_401_UNAUTHORIZED
    assert result.json()["detail"] == "No account"

@pytest.mark.asyncio
async def test_logout(client: AsyncClient, good_user: UserTest):
    """Tests if logout is successful"""
    res1 = await client.post("/api/login",
        json={"email": good_user.email,
            "password": good_user.encrypted_password
        }
    )
    assert res1.status_code == status.HTTP_200_OK
    token = res1.json()["access_token"]
    response = await client.post("/api/logout", headers={
        "Authorization": f"Bearer {token}"  
    })
    assert response.status_code == status.HTTP_200_OK
    result = await client.post("/api/token", headers={
        "Authorization": f"Bearer {token}"
    }, cookies={
        "refresh_token": res1.cookies.get("refresh_token")
    })
    assert result.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.asyncio
async def test_invalid_logout(client: AsyncClient, no_account_token: str):
    response = await client.post("/api/logout", headers={
        "Authorization": f"Bearer {no_account_token}"  
    })
    assert response.status_code == status.HTTP_401_UNAUTHORIZED