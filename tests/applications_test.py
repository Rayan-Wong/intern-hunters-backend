from fastapi import status
from tests.conftest import make_client, good_user
import pytest
from datetime import datetime, timedelta, timezone
from typing import Optional
from pydantic import BaseModel

class UserApplication(BaseModel):
    company_name: str
    role_name: str
    location: str
    status: str
    action_deadline: Optional[datetime] = None
    notes: Optional[str] = None

client = make_client()

def test_create_application(good_user):
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
    application = UserApplication(
        company_name="Skibidi",
        role_name="Toilet",
        location="Tung",
        status="Pending",
    )
    result = client.post("/api/create_application", json=application.model_dump(), headers={
        "Authorization": f"Bearer {token}"
    })
    assert result.status_code == status.HTTP_200_OK