"""Modules relevent for FastAPI testing and constructing mocks"""
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import status
from fastapi.testclient import TestClient
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

def test_read_main(client: TestClient):
    """Checks if server is alive"""
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "ur mum"}

def test_register(client: TestClient, good_user: UserTest):
    """Checks if valid user registration is successful"""
    response = client.post("/api/register",
        json={"name": good_user.name,
            "email": good_user.email,
            "password": good_user.encrypted_password
        }
    )
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()
    assert response.cookies.get("refresh_token") is not None

def test_register_duplicate(client: TestClient, good_user: UserTest):
    """Checks if duplicate registrations fail"""
    client.post("/api/register",
        json={"name": good_user.name,
            "email": good_user.email,
            "password": good_user.encrypted_password
        }
    )
    response = client.post("/api/register",
        json={"name": good_user.name,
            "email": good_user.email,
            "password": good_user.encrypted_password
        }
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_login(client: TestClient, good_user: UserTest):
    """Checks if user with valid credentials can log in"""
    response = client.post("/api/login",
        json={"email": good_user.email,
            "password": good_user.encrypted_password
        }
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.cookies.get("refresh_token") is not None

def test_no_account_login(client: TestClient, no_account_user: UserTest):
    """Checks if user with wrong email fail to log in"""
    response = client.post("/api/login",
        json={"email": no_account_user.email,
            "password": no_account_user.encrypted_password
        }
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_wrong_password_login(client: TestClient, wrong_password_user: UserTest):
    """Checks if user with correct email but wrong password fail to log in"""
    response = client.post("/api/login",
        json={"email": wrong_password_user.email,
            "password": wrong_password_user.encrypted_password
        }
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_good_token(client: TestClient, good_user: UserTest):
    """Checks if server accepts a JWT with good credentials"""
    response = client.post("/api/login",
        json={"email": good_user.email,
            "password": good_user.encrypted_password
        }
    )
    assert "access_token" in response.json()
    token = response.json()["access_token"]
    result = client.post("/api/test_login", headers={
        "Authorization": f"Bearer {token}"
    })
    assert result.status_code == status.HTTP_200_OK

def test_no_token(client: TestClient):
    """Checks if server rejects no token on protected routes"""
    response = client.post("/api/test_login")
    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_bad_token(client: TestClient):
    """Checks if server rejects empty token"""
    response = client.post("/api/test_login", headers={
        "Authorization": "hi"
    })
    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_expired_token(client: TestClient, good_user: UserTest, expired_token):
    """Checks if server rejects expired JWT with valid credentials"""
    res1 = client.post("/api/login",
        json={"email": good_user.email,
            "password": good_user.encrypted_password
        }
    )
    token = res1.json()["access_token"]
    res2 = client.post("/api/test_login", headers={
        "Authorization": f"Bearer {token}"
    })
    user_id = res2.json()
    old_token = expired_token(user_id)
    result = client.post("/api/test_login", headers={
        "Authorization": f"Bearer {old_token}"
    })
    assert result.status_code == status.HTTP_407_PROXY_AUTHENTICATION_REQUIRED
    assert result.json()["detail"] == "Expired token"

def test_no_account_token(client: TestClient, no_account_token: str):
    """Checks if server rejects JWT with wrong email"""
    bad_token = no_account_token
    result = client.post("/api/test_login", headers={
        "Authorization": f"Bearer {bad_token}"
    })
    assert result.status_code == status.HTTP_401_UNAUTHORIZED
    assert result.json()["detail"] == "No account"

def test_session_token(client: TestClient, good_user: UserTest, expired_token: str):
    """Checks if server successfully sends refresh JWT and rotates session token"""
    res1 = client.post("/api/login",
        json={"email": good_user.email,
            "password": good_user.encrypted_password
        }
    )
    token = res1.json()["access_token"]
    res2 = client.post("/api/test_login", headers={
        "Authorization": f"Bearer {token}"
    })
    user_id = res2.json()
    old_token = expired_token(user_id)
    result = client.post("/api/token", headers={
        "Authorization": f"Bearer {old_token}"
    }, cookies={
        "refresh_token": res1.cookies.get("refresh_token")
    })
    assert result.status_code == status.HTTP_200_OK
    assert result.cookies.get("refresh_token") is not None

def test_no_session_token(client: TestClient, good_user: UserTest, expired_token: str):
    """Tests if no session token returns error 401"""
    # first login to get jwt and session tokn
    res1 = client.post("/api/login",
        json={"email": good_user.email,
            "password": good_user.encrypted_password
        }
    )
    assert "access_token" in res1.json()
    token = res1.json()["access_token"]
    # get user id
    res2 = client.post("/api/test_login", headers={
        "Authorization": f"Bearer {token}"
    })
    user_id = res2.json()
    old_token = expired_token(user_id)
    result = client.post("/api/test_session_token", headers={
        "Authorization": f"Bearer {old_token}"
    })
    assert result.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_invalid_session_token(client: TestClient, good_user: UserTest, expired_token: str):
    """Tests if invalid session token returns error 422"""
    # first login to get jwt and session tokn
    res1 = client.post("/api/login",
        json={"email": good_user.email,
            "password": good_user.encrypted_password
        }
    )
    assert "access_token" in res1.json()
    token = res1.json()["access_token"]
    # get user id
    res2 = client.post("/api/test_login", headers={
        "Authorization": f"Bearer {token}"
    })
    user_id = res2.json()
    old_token = expired_token(user_id)
    result = client.post("/api/test_session_token", headers={
        "Authorization": f"Bearer {old_token}"
    }, cookies={
        "refresh_token": "hi"
    })
    assert result.status_code == status.HTTP_400_BAD_REQUEST
    assert result.json()["detail"] == "Invalid session token"

def test_expired_session_token(client: TestClient, good_user: UserTest, expired_token: str, expired_session_token: str):
    """Tests if expired session token returns error 401"""
    # first login to get jwt and session tokn
    res1 = client.post("/api/login",
        json={"email": good_user.email,
            "password": good_user.encrypted_password
        }
    )
    assert "access_token" in res1.json()
    token = res1.json()["access_token"]
    # get user id
    res2 = client.post("/api/test_login", headers={
        "Authorization": f"Bearer {token}"
    })
    user_id = res2.json()
    # get session id
    res3 = client.post("/api/test_session_token", headers={
        "Authorization": f"Bearer {token}"
    }, cookies={
        "refresh_token": res1.cookies.get("refresh_token")
    })
    session_id = res3.json()
    # make expired jwt and session token
    old_token = expired_token(user_id)
    expired_refresh_token = expired_session_token(session_id)
    result = client.post("/api/test_session_token", headers={
        "Authorization": f"Bearer {old_token}"
    }, cookies={
        "refresh_token": expired_refresh_token
    })
    assert result.status_code == status.HTTP_401_UNAUTHORIZED
    assert result.json()["detail"] == "Expired token"

def test_wrong_account_session_token(client: TestClient, good_user: UserTest, expired_token: str, no_account_session_token: str):
    """Tests if wrong session token returns error 401"""
    # first login to get jwt and session tokn
    res1 = client.post("/api/login",
        json={"email": good_user.email,
            "password": good_user.encrypted_password
        }
    )
    assert "access_token" in res1.json()
    token = res1.json()["access_token"]
    # get user id
    res2 = client.post("/api/test_login", headers={
        "Authorization": f"Bearer {token}"
    })
    user_id = res2.json()
    old_token = expired_token(user_id)
    result = client.post("/api/test_session_token", headers={
        "Authorization": f"Bearer {old_token}"
    }, cookies={
        "refresh_token": no_account_session_token
    })
    assert result.status_code == status.HTTP_401_UNAUTHORIZED
    assert result.json()["detail"] == "No account"