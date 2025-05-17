"""Modules relevant for FastAPI testing"""
from datetime import datetime
from typing import Optional

from fastapi import status
from fastapi.testclient import TestClient
import pytest
from pydantic import BaseModel

from tests.conftest import UserTest, client, good_user

class UserApplication(BaseModel):
    """User Application constructor for tests"""
    company_name: str
    role_name: str
    location: str
    status: str
    action_deadline: Optional[datetime] = None
    notes: Optional[str] = None

class UserApplicationModify(UserApplication):
    """"Constructor for user application modify requests"""
    id: int

@pytest.fixture
def get_user_token(client: TestClient, good_user: UserTest):
    """generates good user token to use"""
    client.post("/api/register",
        json={"name": good_user.name,
            "email": good_user.email,
            "password": good_user.encrypted_password
        }
    )
    res1 = client.post("/api/login",
        json={"email": good_user.email,
            "password": good_user.encrypted_password
        }
    )
    token = res1.json()["access_token"]
    return token

def test_create_application(client: TestClient, get_user_token):
    """Tests if an application is successfully created"""
    application = UserApplication(
        company_name="Skibidi",
        role_name="Toilet",
        location="Tung",
        status="Pending",
    )
    result = client.post("/api/create_application", json=application.model_dump(), headers={
        "Authorization": f"Bearer {get_user_token}"
    })
    assert result.status_code == status.HTTP_200_OK
    assert result.json()["company_name"] == "Skibidi"

def test_get_application(client: TestClient, get_user_token):
    """Tests if a requested valid application is successfully received"""
    result = client.get("/api/get_application",
        params={"post_id": 1},
        headers={"Authorization": f"Bearer {get_user_token}"}
    )
    assert result.status_code == status.HTTP_200_OK
    assert result.json()["company_name"] == "Skibidi"

def test_get_wrong_application(client: TestClient, get_user_token):
    """Tests if a requested invalid application fails"""
    result = client.get("/api/get_application",
        params={"post_id": 2},
        headers={"Authorization": f"Bearer {get_user_token}"}
    )
    print(result.json())
    assert result.status_code == status.HTTP_404_NOT_FOUND

def test_get_all_applications(client: TestClient, get_user_token):
    """Tests if a user can get all their applications"""
    result = client.get("/api/get_all_applications",
        headers={"Authorization": f"Bearer {get_user_token}"}
    )
    assert result.status_code == status.HTTP_200_OK
    assert result.json()

def test_modify_application(client: TestClient, get_user_token):
    """Tests if a user can modify the correct application"""
    application = UserApplicationModify(
        company_name="Skibidi",
        role_name="Toilet",
        location="Tung",
        status="Interviewed",
        id=1
    )
    result = client.post("/api/modify_application", json=application.model_dump(), headers={
        "Authorization": f"Bearer {get_user_token}"
    })
    assert result.status_code == status.HTTP_200_OK
    assert result.json()["status"] == "Interviewed"

def test_modify_wrong_application(client: TestClient, get_user_token):
    """Tests if user fails to modify wrong application"""
    application = UserApplicationModify(
        company_name="Skibidi",
        role_name="Toilet",
        location="Tung",
        status="Pending",
        id=2
    )
    result = client.post("/api/modify_application", json=application.model_dump(), headers={
        "Authorization": f"Bearer {get_user_token}"
    })
    assert result.status_code == status.HTTP_404_NOT_FOUND

def test_delete_valid_application(client: TestClient, get_user_token):
    """Tests if a requested valid application is successfully deleted"""
    result = client.delete("/api/delete_application",
        params={"application_id": 1},
        headers={"Authorization": f"Bearer {get_user_token}"}
    )
    assert result.status_code == status.HTTP_202_ACCEPTED

def test_delete_invalid_application(client: TestClient, get_user_token):
    """Tests if a requested invalid application fails to delete"""
    result = client.delete("/api/delete_application",
        params={"application_id": 1},
        headers={"Authorization": f"Bearer {get_user_token}"}
    )
    assert result.status_code == status.HTTP_404_NOT_FOUND

def test_get_no_applications(client: TestClient, get_user_token):
    """Tests if a user without any applications gets an empty list"""
    result = client.get("/api/get_all_applications",
        headers={"Authorization": f"Bearer {get_user_token}"}
    )
    assert result.status_code == status.HTTP_200_OK
    assert result.json() == []
