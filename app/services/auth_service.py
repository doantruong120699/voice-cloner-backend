"""
Authentication service for handling Google OAuth, Firebase Auth, and JWT tokens.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from google.oauth2 import id_token
from google.auth.transport import requests
from jose import JWTError, jwt
import firebase_admin
from firebase_admin import credentials, auth as firebase_auth

from app.core.config import settings
from app.core.exceptions import AuthenticationError, ValidationError
from app.models.storage import user_storage, UserRecord


class AuthService:
    """Service for handling authentication operations."""

    def __init__(self):
        self.google_request = requests.Request()
        self._initialize_firebase()

    def _initialize_firebase(self):
        """Initialize Firebase Admin SDK if credentials are provided."""
        if not firebase_admin._apps:
            import os
            import logging
            from pathlib import Path

            logger = logging.getLogger(__name__)

            # Option 1: Use service account credentials file from FIREBASE_CREDENTIALS_PATH
            if settings.FIREBASE_CREDENTIALS_PATH:
                cred_path = Path(settings.FIREBASE_CREDENTIALS_PATH)
                if cred_path.exists():
                    try:
                        cred = credentials.Certificate(str(cred_path))
                        firebase_admin.initialize_app(cred)
                        logger.info(
                            "Firebase Admin SDK initialized from credentials file"
                        )
                        return
                    except Exception as e:
                        logger.error(
                            f"Failed to initialize Firebase from credentials file: {e}"
                        )

            # Option 1b: Try default serviceAccountKey.json in backend root
            default_cred_path = (
                Path(__file__).parent.parent.parent / "serviceAccountKey.json"
            )
            if default_cred_path.exists():
                try:
                    cred = credentials.Certificate(str(default_cred_path))
                    firebase_admin.initialize_app(cred)
                    logger.info(
                        "Firebase Admin SDK initialized from default serviceAccountKey.json"
                    )
                    return
                except Exception as e:
                    logger.error(
                        f"Failed to initialize Firebase from default credentials file: {e}"
                    )

            # Option 2: Use environment variables (recommended for production)
            firebase_private_key = os.getenv("FIREBASE_PRIVATE_KEY", "")
            firebase_client_email = os.getenv("FIREBASE_CLIENT_EMAIL", "")
            firebase_project_id = os.getenv(
                "FIREBASE_PROJECT_ID", settings.FIREBASE_PROJECT_ID
            )
            firebase_private_key_id = os.getenv("FIREBASE_PRIVATE_KEY_ID", "")
            firebase_client_id = os.getenv("FIREBASE_CLIENT_ID", "")

            if firebase_private_key and firebase_client_email and firebase_project_id:
                try:
                    cred = credentials.Certificate(
                        {
                            "type": "service_account",
                            "project_id": firebase_project_id,
                            "private_key_id": firebase_private_key_id,
                            "private_key": firebase_private_key.replace("\\n", "\n"),
                            "client_email": firebase_client_email,
                            "client_id": firebase_client_id,
                            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                            "token_uri": "https://oauth2.googleapis.com/token",
                        }
                    )
                    firebase_admin.initialize_app(cred)
                    logger.info(
                        "Firebase Admin SDK initialized from environment variables"
                    )
                    return
                except Exception as e:
                    logger.error(
                        f"Failed to initialize Firebase from environment variables: {e}"
                    )

            # Option 3: Initialize with default credentials (for GCP environments)
            if settings.FIREBASE_PROJECT_ID:
                try:
                    firebase_admin.initialize_app()
                    logger.info(
                        "Firebase Admin SDK initialized with default credentials"
                    )
                    return
                except Exception as e:
                    logger.warning(
                        f"Failed to initialize Firebase with default credentials: {e}"
                    )

            # If neither is set, Firebase verification will be skipped
            # This is OK if you're only using Google OAuth tokens
            logger.warning(
                "Firebase Admin SDK not initialized. Firebase token verification will not be available. "
                "Set FIREBASE_CREDENTIALS_PATH, FIREBASE_PROJECT_ID, or Firebase environment variables to enable."
            )

    def is_firebase_initialized(self) -> bool:
        """
        Check if Firebase Admin SDK is initialized.

        Returns:
            True if Firebase is initialized, False otherwise
        """
        return bool(firebase_admin._apps)

    def verify_firebase_token(self, token: str) -> Dict[str, Any]:
        """
        Verify Firebase ID token and extract user information.

        Args:
            token: Firebase ID token

        Returns:
            Dictionary containing user information from Firebase

        Raises:
            AuthenticationError: If token is invalid or Firebase is not initialized
        """
        if not self.is_firebase_initialized():
            raise AuthenticationError(
                "Firebase Admin SDK not initialized. "
                "Please configure Firebase credentials (FIREBASE_CREDENTIALS_PATH, "
                "FIREBASE_PROJECT_ID, or Firebase environment variables) to use Firebase token verification."
            )

        try:

            # Verify the Firebase ID token
            decoded_token = firebase_auth.verify_id_token(token)

            # Extract user information
            user_info = {
                "sub": decoded_token.get("uid"),
                "email": decoded_token.get("email"),
                "name": decoded_token.get("name"),
                "picture": decoded_token.get("picture"),
                "email_verified": decoded_token.get("email_verified", False),
            }

            return user_info
        except firebase_auth.InvalidIdTokenError as e:
            raise AuthenticationError(f"Invalid Firebase token: {str(e)}")
        except Exception as e:
            raise AuthenticationError(f"Error verifying Firebase token: {str(e)}")

    def verify_google_token(self, token: str) -> Dict[str, Any]:
        """
        Verify Google OAuth token and extract user information.

        Args:
            token: Google ID token

        Returns:
            Dictionary containing user information from Google

        Raises:
            AuthenticationError: If token is invalid
        """
        try:
            # Verify the token
            idinfo = id_token.verify_oauth2_token(
                token, self.google_request, settings.GOOGLE_CLIENT_ID
            )

            # Verify the issuer
            if idinfo["iss"] not in [
                "accounts.google.com",
                "https://accounts.google.com",
            ]:
                raise AuthenticationError("Invalid token issuer")

            return idinfo
        except ValueError as e:
            raise AuthenticationError(f"Invalid Google token: {str(e)}")
        except Exception as e:
            raise AuthenticationError(f"Error verifying Google token: {str(e)}")

    def create_access_token(self, user: UserRecord) -> str:
        """
        Create JWT access token for user.

        Args:
            user: User record

        Returns:
            JWT access token string
        """
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        to_encode = {
            "sub": user.user_id,
            "email": user.email,
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access",
        }
        encoded_jwt = jwt.encode(
            to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
        )
        return encoded_jwt

    def create_refresh_token(self, user: UserRecord) -> str:
        """
        Create JWT refresh token for user.

        Args:
            user: User record

        Returns:
            JWT refresh token string
        """
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode = {
            "sub": user.user_id,
            "email": user.email,
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh",
        }
        encoded_jwt = jwt.encode(
            to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
        )
        return encoded_jwt

    def verify_access_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify JWT access token.

        Args:
            token: JWT access token

        Returns:
            Decoded token payload or None if invalid
        """
        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            return payload
        except JWTError:
            return None

    def get_or_create_user_from_google(
        self, google_user_info: Dict[str, Any]
    ) -> UserRecord:
        """
        Get existing user or create new user from Google OAuth info.

        Args:
            google_user_info: User information from Google OAuth

        Returns:
            User record
        """
        email = google_user_info.get("email")
        if not email:
            raise ValidationError("Email not provided in Google account")

        # Check if user exists
        user = user_storage.get_by_email(email)

        if user:
            # Update user info if needed
            name = google_user_info.get("name")
            picture = google_user_info.get("picture")
            user_storage.update(user.user_id, name=name, picture=picture)
            # Get updated user
            user = user_storage.get(user.user_id)
        else:
            # Create new user
            user = user_storage.create(
                email=email,
                name=google_user_info.get("name"),
                picture=google_user_info.get("picture"),
                provider="google",
            )

        return user

    def verify_token_and_get_user(
        self, token: str, is_firebase_token: bool = False
    ) -> UserRecord:
        """
        Verify ID token (Firebase or Google) and get or create user.

        Args:
            token: Firebase ID token or Google ID token
            is_firebase_token: Whether the token is a Firebase ID token

        Returns:
            User record

        Raises:
            AuthenticationError: If token is invalid or Firebase is not initialized
        """
        # Verify token (either Firebase or Google OAuth)
        if is_firebase_token:
            if not self.is_firebase_initialized():
                raise AuthenticationError(
                    "Firebase Admin SDK not initialized. "
                    "Please configure Firebase credentials to use Firebase token verification, "
                    "or use Google OAuth token instead."
                )
            user_info = self.verify_firebase_token(token)
            # Map Firebase user info to Google OAuth format
            google_user_info = {
                "email": user_info.get("email"),
                "name": user_info.get("name"),
                "picture": user_info.get("picture"),
                "sub": user_info.get("sub"),
            }
        else:
            google_user_info = self.verify_google_token(token)

        # Get or create user
        return self.get_or_create_user_from_google(google_user_info)

    def authenticate_with_google_token(
        self, google_token: str, is_firebase_token: bool = False
    ) -> tuple[UserRecord, str]:
        """
        Authenticate user with Google OAuth token or Firebase ID token.

        Args:
            google_token: Google ID token from OAuth flow or Firebase ID token
            is_firebase_token: Whether the token is a Firebase ID token

        Returns:
            Tuple of (UserRecord, access_token)

        Raises:
            AuthenticationError: If authentication fails
        """
        # Verify token and get or create user
        user = self.verify_token_and_get_user(google_token, is_firebase_token)

        # Create access token
        access_token = self.create_access_token(user)

        return user, access_token

    def get_current_user(self, token: str) -> Optional[UserRecord]:
        """
        Get current user from access token.

        Args:
            token: JWT access token

        Returns:
            User record or None if invalid
        """
        payload = self.verify_access_token(token)
        if payload is None:
            return None

        user_id = payload.get("sub")
        if not user_id:
            return None

        return user_storage.get(user_id)


# Global auth service instance
auth_service = AuthService()
