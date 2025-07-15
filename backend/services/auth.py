import os
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models import UserInfo

logger = logging.getLogger(__name__)

class AuthService:
    """
    이건 보안적인 요소라고 생각하면 됨 -> 인공지능이 추가해줌.
    """
    
    def __init__(self):
        self.secret_key = os.getenv("JWT_SECRET_KEY", "your-secret-key-here-change-in-production")
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 60 * 24  # 24 hours
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
    def create_access_token(self, data: Dict[str, Any]) -> str:
        """
        Create a JWT access token.
        
        Args:
            data: Dictionary containing user information
            
        Returns:
            JWT token string
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        to_encode.update({"exp": expire})
        
        try:
            encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
            logger.info(f"Created access token for user: {data.get('sub')}")
            return encoded_jwt
        except Exception as e:
            logger.error(f"Error creating access token: {str(e)}")
            raise
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify and decode a JWT token.
        
        Args:
            token: JWT token string
            
        Returns:
            Decoded token payload or None if invalid
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError as e:
            logger.warning(f"Invalid token: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error verifying token: {str(e)}")
            return None
    
    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt."""
        return self.pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def authenticate_user(self, username: str, password: str) -> Optional[UserInfo]:
        """
        Authenticate a user with username and password.
        This is a stub implementation - replace with real authentication in production.
        
        Args:
            username: Username
            password: Password
            
        Returns:
            UserInfo if authentication successful, None otherwise
        """
        # Stub implementation - replace with database lookup
        # In production, this would query your user database
        # and integrate with hospital SSO system
        
        test_users = {
            "admin": {
                "id": "admin",
                "username": "admin",
                "password_hash": self.hash_password("password"),
                "role": "admin",
                "email": "admin@hospital.com",
                "department": "Radiology"
            },
            "doctor": {
                "id": "doctor1",
                "username": "doctor",
                "password_hash": self.hash_password("doctor123"),
                "role": "radiologist",
                "email": "doctor@hospital.com",
                "department": "Radiology"
            }
        }
        
        user_data = test_users.get(username)
        if not user_data:
            return None
        
        if not self.verify_password(password, user_data["password_hash"]):
            return None
        
        return UserInfo(
            id=user_data["id"],
            username=user_data["username"],
            role=user_data["role"],
            email=user_data["email"],
            department=user_data["department"]
        )
    
    def get_user_by_id(self, user_id: str) -> Optional[UserInfo]:
        """
        Get user information by user ID.
        This is a stub implementation - replace with database lookup in production.
        
        Args:
            user_id: User ID
            
        Returns:
            UserInfo if found, None otherwise
        """
        # Stub implementation - replace with database lookup
        test_users = {
            "admin": UserInfo(
                id="admin",
                username="admin",
                role="admin",
                email="admin@hospital.com",
                department="Radiology"
            ),
            "doctor1": UserInfo(
                id="doctor1",
                username="doctor",
                role="radiologist",
                email="doctor@hospital.com",
                department="Radiology"
            )
        }
        
        return test_users.get(user_id)
    
    def validate_role(self, user_role: str, required_roles: list) -> bool:
        """
        Validate if user has required role.
        
        Args:
            user_role: Current user's role
            required_roles: List of required roles
            
        Returns:
            True if user has required role, False otherwise
        """
        return user_role in required_roles
    
    def refresh_token(self, refresh_token: str) -> Optional[str]:
        """
        Refresh an access token using a refresh token.
        This is a stub implementation - implement refresh token logic in production.
        
        Args:
            refresh_token: Refresh token string
            
        Returns:
            New access token if successful, None otherwise
        """
        # Stub implementation - implement refresh token logic
        payload = self.verify_token(refresh_token)
        if not payload:
            return None
        
        # Create new access token
        new_token_data = {
            "sub": payload.get("sub"),
            "role": payload.get("role")
        }
        
        return self.create_access_token(new_token_data) 