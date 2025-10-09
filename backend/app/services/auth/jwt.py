from datetime import datetime, timedelta, timezone
from typing import Dict, Optional, Tuple

from jose import JWTError, jwt

from config.settings import settings


class JWTService:
    def __init__(self):
        self.secret_key = settings.JWT_SECRET
        self.algorithm = settings.JWT_ALGORITHM
        self.expire_minutes = settings.JWT_EXPIRE_MINUTES
    
    def create_access_token(self, data: Dict, user_type: str) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(minutes=self.expire_minutes)
        to_encode.update({
            "exp": expire,
            "user_type": user_type,
            "iat": datetime.now(timezone.utc)
        })
        
        encoded_jwt = jwt.encode(
            to_encode, 
            self.secret_key, 
            algorithm=self.algorithm
        )
        return encoded_jwt
    
    def decode_access_token(self, token: str) -> Optional[Dict]:
        try:
            payload = jwt.decode(
                token, 
                self.secret_key, 
                algorithms=[self.algorithm]
            )
            return payload
        except JWTError:
            return None
    
    def create_user_token(self, email: str, user_type: str, is_active: bool) -> str:
        access_token = self.create_access_token(
            data={"sub": email, "is_active": is_active},
            user_type=user_type
        )
        return access_token
    
    def verify_and_refresh_token(self, token: str) -> Tuple[bool, Optional[str], Optional[Dict]]:
        """
        토크 검증 함수
        
        Returns:
            Tuple[bool, Optional[str], Optional[Dict]]: 
            - bool: 토큰 유효성
            - Optional[str]: 갱신된 토큰 (갱신이 필요한 경우)
            - Optional[Dict]: 디코드된 payload
        """
        payload = self.decode_access_token(token)
        
        if not payload:
            return False, None, None
        
        # 토큰 만료 시간 확인
        exp = datetime.fromtimestamp(payload['exp'], tz=timezone.utc)
        now = datetime.now(timezone.utc)
        
        # 토큰이 만료되었으면 무효
        if exp < now:
            return False, None, None
        
        # 토큰 만료까지 5분 미만 남았으면 갱신
        if exp - now < timedelta(minutes=5):
            new_token = self.create_user_token(
                email=payload['sub'],
                user_type=payload['user_type'],
                is_active=payload['is_active']
            )
            return True, new_token, payload
        
        return True, None, payload