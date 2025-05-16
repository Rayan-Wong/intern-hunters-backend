"""Modules relevent for FastAPI testing and constructing mocks"""
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import status
from fastapi.testclient import TestClient
import pytest
import jwt

from tests.conftest import client, get_jwt_secrets, UserTest, good_user

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

@pytest.fixture
def no_account_user():
    """Returns JWT with email not in mock db"""
    return UserTest(
        name="admin",
        email="urdad@gmail.com",
        encrypted_password="password"
    )

@pytest.fixture
def wrong_password_user():
    """Returns JWT with correct email but wrong password"""
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
    assert response.status_code == status.HTTP_201_CREATED

def test_register_duplicate(client: TestClient, good_user: UserTest):
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
    result = client.post("/api/token", headers={
        "Authorization": f"Bearer {token}"
    })
    assert result.status_code == status.HTTP_200_OK

def test_bad_token(client: TestClient):
    """Checks if server rejects empty token"""
    response = client.post("/api/token", headers={
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
    res2 = client.post("/api/token", headers={
        "Authorization": f"Bearer {token}"
    })
    user_id = res2.json()
    old_token = expired_token(user_id)
    result = client.post("/api/token", headers={
        "Authorization": f"Bearer {old_token}"
    })
    assert result.status_code == status.HTTP_401_UNAUTHORIZED
    assert result.json()["detail"] == "Expired token"

def test_no_account_token(client: TestClient, no_account_token: str):
    """Checks if server rejects JWT with wrong email"""
    bad_token = no_account_token
    result = client.post("/api/token", headers={
        "Authorization": f"Bearer {bad_token}"
    })
    assert result.status_code == status.HTTP_401_UNAUTHORIZED
    assert result.json()["detail"] == "No account"
