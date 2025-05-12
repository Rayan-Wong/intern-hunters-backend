from fastapi import status
from tests.conftest import make_client, get_jwt_secrets
import pytest
import jwt
import uuid
from datetime import datetime, timedelta, timezone

class UserTest:
    def __init__(self, name, email, encrypted_password):
        self.name: str = name
        self.email: str = email
        self.encrypted_password: str = encrypted_password

class BadJWTConstructor:
    def __init__(self, sub, iat, exp):
        self.sub = sub
        self.iat = iat
        self.exp = exp
        self.__secret_key = get_jwt_secrets()
        self.__algorithm = "HS256"
    def generate_token(self):
        payload = {"sub": self.sub,
            "iat": self.iat,
            "exp": self.exp
        }
        return jwt.encode(payload, key=self.__secret_key, algorithm=self.__algorithm)

@pytest.fixture
def good_user():
    return UserTest(
        name="admin",
        email="urmum@gmail.com",
        encrypted_password="password"
    )

@pytest.fixture
def no_account_user():
    return UserTest(
        name="admin",
        email="urdad@gmail.com",
        encrypted_password="password"
    )

@pytest.fixture
def wrong_password_user():
    return UserTest(
        name="admin",
        email="urmum@gmail.com",
        encrypted_password="pasword"
    )

@pytest.fixture
def expired_token():
    def _create(uuid: str):
        return BadJWTConstructor(
            sub=uuid,
            exp=datetime.now(timezone.utc),
            iat=datetime.now(timezone.utc) - timedelta(minutes=45)
        ).generate_token()
    return _create

@pytest.fixture
def no_account_token():
    return BadJWTConstructor(
        sub=str(uuid.uuid4()),
        exp=datetime.now(timezone.utc) + timedelta(minutes=30),
        iat=datetime.now(timezone.utc)
    ).generate_token()

client = make_client()

# these tests are done on a mock db, so no cybersecurity flaws here

def test_read_main():
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "ur mum"}

def test_register(good_user):
    response = client.post("/api/register",
        json={"name": good_user.name, 
            "email": good_user.email,
            "password": good_user.encrypted_password
        }
    )
    assert response.status_code == status.HTTP_201_CREATED

def test_register_duplicate(good_user):
    response = client.post("/api/register",
        json={"name": good_user.name, 
            "email": good_user.email,
            "password": good_user.encrypted_password
        }
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_login(good_user):
    response = client.post("/api/login",
        json={"email": good_user.email,
            "password": good_user.encrypted_password
        }
    )
    assert response.status_code == status.HTTP_200_OK

def test_no_account_login(no_account_user):
    response = client.post("/api/login",
        json={"email": no_account_user.email,
            "password": no_account_user.encrypted_password
        }
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_wrong_password_login(wrong_password_user):
    response = client.post("/api/login",
        json={"email": wrong_password_user.email,
            "password": wrong_password_user.encrypted_password
        }
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_good_token(good_user):
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

def test_bad_token():
    response = client.post("/api/token", headers={
        "Authorization": "hi"
    })
    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_expired_token(good_user, expired_token):
    res1 = client.post("/api/login",
        json={"email": good_user.email,
            "password": good_user.encrypted_password
        }
    )
    token = res1.json()["access_token"]
    res2 = client.post("/api/token", headers={
        "Authorization": f"Bearer {token}"
    })
    id = res2.json()["id"]
    old_token = expired_token(id)
    result = client.post("/api/token", headers={
        "Authorization": f"Bearer {old_token}"
    })
    assert result.status_code == status.HTTP_401_UNAUTHORIZED

def test_no_account_token(no_account_token):
    bad_token = no_account_token
    result = client.post("/api/token", headers={
        "Authorization": f"Bearer {bad_token}"
    })
    assert result.status_code == status.HTTP_401_UNAUTHORIZED