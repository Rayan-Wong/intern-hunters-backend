from fastapi import status
from tests.conftest import make_client

client = make_client()

def test_read_main():
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "ur mum"}

def test_register():
    response = client.post("/api/register",
        json={"name": "admin", 
            "email": "urmum@gmail.com",
            "password": "password"
        }
    )
    assert response.status_code == status.HTTP_201_CREATED

def test_register_duplicate():
    response = client.post("/api/register",
        json={"name": "admin", 
            "email": "urmum@gmail.com",
            "password": "password"
        }
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_login():
    response = client.post("/api/login",
        json={"email": "urmum@gmail.com",
            "password": "password"
        }
    )
    assert response.status_code == status.HTTP_200_OK

def test_no_account_login():
    response = client.post("/api/login",
        json={"email": "urdad@gmail.com",
            "password": "password"
        }
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_wrong_account_login():
    response = client.post("/api/login",
        json={"email": "urmum@gmail.com",
            "password": "pasword"
        }
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
