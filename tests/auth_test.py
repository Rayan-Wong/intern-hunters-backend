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
    def __init__(self, sub, sid, iat, exp):
        self.sub = sub
        self.sid = sid
        self.iat = iat
        self.exp = exp
        self.__secret_key = get_jwt_secrets()
        self.__algorithm = "HS256"
    def generate_token(self):
        payload = {"sub": self.sub,
            "sid": self.sid,
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
    def _create(user_id: str, user_session: str):
        return BadJWTConstructor(
            sub=user_id,
            sid=user_session,
            exp=datetime.now(timezone.utc),
            iat=datetime.now(timezone.utc) - timedelta(minutes=45)
        ).generate_token()
    return _create

@pytest.fixture
def bad_session_token():
    def _create(user_id: str):
        return BadJWTConstructor(
            sub=user_id,
            sid=str(uuid.uuid4()),
            exp=datetime.now(timezone.utc) + timedelta(minutes=30),
            iat=datetime.now(timezone.utc)
        ).generate_token()
    return _create

@pytest.fixture
def bad_account_token():
    def _create(session_id: str):
        return BadJWTConstructor(
            sub=str(uuid.uuid4()),
            sid=session_id,
            exp=datetime.now(timezone.utc) + timedelta(minutes=30),
            iat=datetime.now(timezone.utc)
        ).generate_token()
    return _create

@pytest.fixture
def malformed_token():
    return BadJWTConstructor(
        sub=str(uuid.uuid4()),
        sid=str(uuid.uuid4()),
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
    result = client.post("/api/token", json={
        "token": token
    })
    assert result.status_code == status.HTTP_200_OK

def test_bad_token():
    response = client.post("/api/token", json={
        "token": "hi"
    })
    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_expired_token(good_user, expired_token):
    res1 = client.post("/api/login",
        json={"email": good_user.email,
            "password": good_user.encrypted_password
        }
    )
    token = res1.json()["access_token"]
    res2 = client.post("/api/token", json={
            "token": token
        }
    )
    id = res2.json()["id"]
    session_id = res2.json()["session_id"]
    old_token = expired_token(id, session_id)
    result = client.post("/api/token", json={
        "token": old_token
    })
    assert result.status_code == status.HTTP_401_UNAUTHORIZED

def test_bad_session_token(good_user, bad_session_token):
    res1 = client.post("/api/login",
        json={"email": good_user.email,
            "password": good_user.encrypted_password
        }
    )
    token = res1.json()["access_token"]
    res2 = client.post("/api/token", json={
            "token": token
        }
    )
    id = res2.json()["id"]
    bad_token = bad_session_token(id)
    result = client.post("/api/token", json={
        "token": bad_token
    })
    assert result.status_code == status.HTTP_429_TOO_MANY_REQUESTS

def test_bad_account_token(good_user, bad_account_token):
    res1 = client.post("/api/login",
        json={"email": good_user.email,
            "password": good_user.encrypted_password
        }
    )
    token = res1.json()["access_token"]
    res2 = client.post("/api/token", json={
            "token": token
        }
    )
    session_id = res2.json()["session_id"]
    bad_token = bad_account_token(session_id)
    result = client.post("/api/token", json={
        "token": bad_token
    })
    assert result.status_code == status.HTTP_401_UNAUTHORIZED

def test_malformed_token(malformed_token):
    bad_token = malformed_token
    result = client.post("/api/token", json={
        "token": bad_token
    })
    assert result.status_code == status.HTTP_401_UNAUTHORIZED