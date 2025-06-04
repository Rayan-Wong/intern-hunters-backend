"""List of metadata tags and error responses for /docs"""
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
        "name": "all_applications",
        "description": "Retrieve all applications submitted by a specific user."
    },
    {
        "name": "all_deadlines",
        "description": "Retrieve all applications sorted by their upcoming deadlines."
    }
]

DESCRIPTION = """
Note that for all protected routes (the ones with the padlock), 
the route may throw status code 401 and 403 for invalid JWT (and so the user should re-login),
or status code 407 for expired JWT, which means frontend should do silent token refresh at /api/token
The exception is /api/token which accepts expired JWTs
"""

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

SPACY_DEAD = {
    503: {
        "description": "spaCy is down",
        "content": {
            "application/json": {
                "example": {"detail": "spaCy down"}
            }
        }
    }
}