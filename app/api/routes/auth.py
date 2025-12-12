"""
Authentication routes for login and sign-up with Google OAuth.
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse

from app.core.exceptions import AuthenticationError, ValidationError
from app.models.schemas import (
    TokenResponse,
    GoogleAuthRequest,
    UserResponse,
    IdTokenRequest,
    VerifyTokenResponse,
)
from app.services.auth_service import auth_service
from app.models.storage import UserRecord
from app.api.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/google/token", response_model=TokenResponse)
async def google_token_auth(request: GoogleAuthRequest):
    """
    Authenticate with Google ID token or Firebase ID token directly.
    This endpoint accepts a Google ID token or Firebase ID token and returns a JWT access token.
    Useful for mobile apps or direct token exchange.

    Set firebase_token=true if sending a Firebase ID token.
    """
    try:
        # Authenticate with Google token or Firebase token
        user, access_token = auth_service.authenticate_with_google_token(
            request.code, is_firebase_token=request.firebase_token or False
        )

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user={
                "id": user.user_id,
                "email": user.email,
                "name": user.name,
                "picture": user.picture,
                "provider": user.provider,
                "created_at": user.created_at.isoformat(),
            },
        )
    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Authentication error: {str(e)}")


@router.post("/verify", response_model=VerifyTokenResponse)
async def verify_id_token(request: IdTokenRequest):
    """
    Verify ID token (Firebase or Google), decode user info, and save to user table.
    This endpoint accepts an ID token, verifies it, extracts user information,
    creates or updates the user in the database, and returns access and refresh tokens.
    """
    try:
        # Verify token and get or create user
        user = auth_service.verify_token_and_get_user(
            request.idToken, is_firebase_token=request.is_firebase_token or False
        )

        # Generate access and refresh tokens
        access_token = auth_service.create_access_token(user)
        refresh_token = auth_service.create_refresh_token(user)

        return VerifyTokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
        )
    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error verifying token: {str(e)}")


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(user: UserRecord = Depends(get_current_user)):
    """
    Get current user information from access token.
    Token should be passed in Authorization header as: Bearer <token>
    """
    return UserResponse(
        id=user.user_id,
        email=user.email,
        name=user.name,
        picture=user.picture,
        provider=user.provider,
        created_at=user.created_at,
    )
