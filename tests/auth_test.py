from fastapi import status
from tests.conftest import make_client
from app.models.user import User
import pytest

class UserTest:
    def __init__(self, name, email, encrypted_password):
        self.name = name
        self.email = email
        self.encrypted_password = encrypted_password

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
