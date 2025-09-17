"""
Authentication module for Google OAuth 2.0 and JWT token handling
"""
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import httpx
from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from sql_utils import get_engine, User, create_or_update_user, get_user_by_google_id, get_user_by_id, check_email_access

# JWT Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))

# Google OAuth Configuration
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")

# Security scheme
security = HTTPBearer()


class AuthError(Exception):
    """Custom authentication error"""
    pass


def create_access_token(data: Dict[str, Any]) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Dict[str, Any]:
    """Verify and decode a JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except JWTError:
        raise AuthError("Invalid token")


async def get_google_user_info(access_token: str) -> Dict[str, Any]:
    """Get user information from Google using access token"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        
        if response.status_code != 200:
            raise AuthError("Failed to get user info from Google")
        
        return response.json()


async def exchange_code_for_token(code: str, redirect_uri: str = None) -> str:
    """Exchange authorization code for access token"""
    async with httpx.AsyncClient() as client:
        data = {
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri or GOOGLE_REDIRECT_URI,
        }
        
        response = await client.post(
            "https://oauth2.googleapis.com/token",
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code != 200:
            error_details = response.text()
            print(f"Google OAuth token exchange failed: {error_details}")
            raise AuthError(f"Failed to exchange code for token: {error_details}")
        
        token_data = response.json()
        return token_data["access_token"]


async def authenticate_google_user(code: str, db_path: str = "db.sqlite") -> Dict[str, Any]:
    """
    Authenticate user with Google OAuth and return user info with JWT token
    
    Args:
        code: Authorization code from Google OAuth
        db_path: Path to the database
        
    Returns:
        Dictionary with user info and access token
        
    Raises:
        AuthError: If authentication fails or email is not whitelisted
    """
    try:
        # Exchange code for access token
        access_token = await exchange_code_for_token(code)
    
        # Get user info from Google
        user_info = await get_google_user_info(access_token)
        
        email = user_info.get("email")
        if not email:
            raise AuthError("No email found in Google user info")
        
        # Check if email is whitelisted
        if not check_email_access(email):
            raise AuthError(f"Access denied. Email {email} is not authorized.")
        
        # Create or update user in database
        engine = get_engine(db_path)
        with Session(engine) as session:
            user = create_or_update_user(
                session=session,
                google_id=user_info["id"],
                email=email,
                name=user_info.get("name", ""),
                picture=user_info.get("picture")
            )
        
            # Create JWT token
            token_data = {
                "sub": str(user.id),
                "email": user.email,
                "name": user.name,
                "google_id": user.google_id
            }
            jwt_token = create_access_token(token_data)
            
            return {
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "name": user.name,
                    "picture": user.picture,
                    "created_at": user.created_at.isoformat(),
                    "last_login": user.last_login.isoformat() if user.last_login else None
                },
                "access_token": jwt_token,
                "token_type": "bearer"
            }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise


async def authenticate_google_user_with_redirect(code: str, redirect_uri: str, db_path: str = "db.sqlite") -> Dict[str, Any]:
    """
    Authenticate user with Google OAuth using custom redirect URI and return user info with JWT token
    
    Args:
        code: Authorization code from Google OAuth
        redirect_uri: The redirect URI used in the original OAuth request
        db_path: Path to the database
        
    Returns:
        Dictionary with user info and access token
        
    Raises:
        AuthError: If authentication fails or email is not whitelisted
    """
    try:
        # Exchange code for access token using custom redirect URI
        access_token = await exchange_code_for_token(code, redirect_uri)
    
        # Get user info from Google
        user_info = await get_google_user_info(access_token)
        
        email = user_info.get("email")
        if not email:
            raise AuthError("No email found in Google user info")
        
        # Check if email is whitelisted
        if not check_email_access(email):
            raise AuthError(f"Access denied. Email {email} is not authorized.")
        
        # Create or update user in database
        engine = get_engine(db_path)
        with Session(engine) as session:
            user = create_or_update_user(
                session=session,
                google_id=user_info["id"],
                email=email,
                name=user_info.get("name", ""),
                picture=user_info.get("picture")
            )
        
            # Create JWT token
            token_data = {
                "sub": str(user.id),
                "email": user.email,
                "name": user.name,
                "google_id": user.google_id
            }
            jwt_token = create_access_token(token_data)
            
            return {
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "name": user.name,
                    "picture": user.picture,
                    "created_at": user.created_at.isoformat(),
                    "last_login": user.last_login.isoformat() if user.last_login else None
                },
                "access_token": jwt_token,
                "token_type": "bearer"
            }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db_path: str = "db.sqlite") -> User:
    """
    Get current authenticated user from JWT token
    
    Args:
        credentials: HTTP Bearer token credentials
        db_path: Path to the database
        
    Returns:
        User object
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    try:
        # Verify token
        payload = verify_token(credentials.credentials)
        
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        
        # Get user from database
        engine = get_engine(db_path)
        with Session(engine) as session:
            user = get_user_by_id(session, int(user_id))
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found"
                )
            return user
            
    except AuthError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed"
        )


def get_google_oauth_url() -> str:
    """Generate Google OAuth authorization URL"""
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "scope": "openid email profile",
        "response_type": "code",
        "access_type": "offline",
        "prompt": "consent"
    }
    
    query_string = "&".join([f"{k}={v}" for k, v in params.items()])
    return f"https://accounts.google.com/o/oauth2/v2/auth?{query_string}"
