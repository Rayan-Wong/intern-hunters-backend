"""List of metadata tags, error responses and other descriptions for /docs"""
TAGS_METADATA = [
    {
        "name": "register_user",
        "description": "Register a new user and returns JWT and access token."
    },
    {
        "name": "login_user",
        "description": "Log in a user and return JWT, access token and user's name."
    },
    {
        "name": "refresh_token",
        "description": "Use a refresh token to get a new JWT and refresh token."
    },
    {
        "name": "logout_user",
        "description": "Log out a user and invalidates their refresh token."
    },
    {
        "name": "application",
        "description": "Endpoints for creating, retrieving, modifying, and deleting individual user applications."
    },
    {
        "name": "upload_resume",
        "description": "Retrieve user's resume sections."
    },
    {
        "name": "internship_listings",
        "description": "Fetch 20 internship listings tailored to user. The listing description is sent as a HTML set. Note that date_posted may be null"
    },
    {
        "name": "resume_editor",
        "description": "Endpoints relevant to creating or editing resumes"
    }
]

DESCRIPTION = """
Note that for all protected routes (the ones with the padlock), 
the route may throw status code 401 and 403 for invalid JWT (and so the user should re-login),
or status code 407 for expired JWT, which means frontend should do silent token refresh at /api/token
The exception is /api/token which accepts expired JWTs
"""

FILE_DESCRIPTION = {
    200: {
        "description": "PDF download",
        "content": {
            "application/pdf": {
                "schema": {
                    "type": "binary",
                    "format": "binary"
                }
            }
        }
    }
}

NO_ACCOUNT_RESPONSE = {
    401: {
        "description": "No account associated with the given JWT",
        "content": {
            "application/json": {
                "example": {"detail": "No account"}
            }
        }
    }
}

EXPIRED_JWT_RESPONSE = {
    407: {
        "description": "JWT has expired",
        "content": {
            "application/json": {
                "example": {"detail": "Expired token"}
            }
        }
    }
}

INVALID_JWT_RESPONSE = {
    403: {
        "description": "JWT is malformed or otherwise invalid",
        "content": {
            "application/json": {
                "example": {"detail": "Invalid JWT"}
            }
        }
    }
}

NO_REFRESH_TOKEN_RESPONSE = {
    401: {
        "description": "No refresh token cookie provided",
        "content": {
            "application/json": {
                "example": {"detail": "No refresh token"}
            }
        }
    }
}

INVALID_SESSION_TOKEN_RESPONSE = {
    400: {
        "description": "Refresh token is invalid or corrupted",
        "content": {
            "application/json": {
                "example": {"detail": "Invalid session token"}
            }
        }
    }
}

EXPIRED_SESSION_TOKEN_RESPONSE = {
    401: {
        "description": "Session token expired",
        "content": {
            "application/json": {
                "example": {"detail": "Logged out"}
            }
        }
    }
}

EMAIL_ALREADY_EXISTS_RESPONSE = {
    400: {
        "description": "Email already exists in the database",
        "content": {
            "application/json": {
                "example": {"detail": "Email already exists"}
            }
        }
    }
}

ACCOUNT_NOT_CREATED_RESPONSE = {
    400: {
        "description": "No account exists with provided credentials",
        "content": {
            "application/json": {
                "example": {"detail": "Account not created"}
            }
        }
    }
}

PASSWORD_INCORRECT_RESPONSE = {
    401: {
        "description": "Password provided is incorrect",
        "content": {
            "application/json": {
                "example": {"detail": "Password incorrect"}
            }
        }
    }
}

BAD_REFRESH_TOKEN_RESPONSE = {
    401: {
        "description": "Refresh token was not provided or is malformed",
        "content": {
            "application/json": {
                "example": {"detail": "Bad refresh token"}
            }
        }
    }
}

BAD_JWT = {**NO_ACCOUNT_RESPONSE, **INVALID_JWT_RESPONSE, **EXPIRED_JWT_RESPONSE}

INVALID_APPLICATION_RESPONSE = {
    400: {
        "description": "The submitted application is invalid",
        "content": {
            "application/json": {
                "example": {"detail": "Invalid application"}
            }
        }
    }
}

APPLICATION_NOT_FOUND_RESPONSE = {
    404: {
        "description": "No application found with the given ID for the current user",
        "content": {
            "application/json": {
                "example": {"detail": "Application not found"}
            }
        }
    }
}

SERVICE_DEAD = {
    503: {
        "description": "A third party service (Gemini, spaCy etc) is down",
        "content": {
            "application/json": {
                "example": {"detail": "Third party worker down"}
            }
        }
    }
}

NO_DETAILS = {
    400: {
        "description": "The user has not uploaded details",
        "content": {
            "application/json": {
                "example": {"detail": "User has not uploaded details"}
            }
        }
    }
}

NO_UPLOADED_RESUME = {
    400: {
        "description": "The user has not uploaded resume",
        "content": {
            "application/json": {
                "example": {"detail": "User has not uploaded resume"}
            }
        }
    }
}
