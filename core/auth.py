#!/usr/bin/env python3
"""
认证模块
处理用户登录、注册、JWT令牌管理
"""

import os
import jwt
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from pydantic import BaseModel

# JWT配置
SECRET_KEY = os.environ.get("MERIT_JWT_SECRET", "dev-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7天


class Token(BaseModel):
    """令牌响应模型"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int = ACCESS_TOKEN_EXPIRE_MINUTES * 60  # 秒数


class TokenData(BaseModel):
    """令牌数据"""
    user_id: Optional[str] = None
    nickname: Optional[str] = None


class UserLogin(BaseModel):
    """用户登录请求"""
    user_id: str
    password: str


class UserRegisterAuth(UserLogin):
    """用户注册请求（带认证）"""
    nickname: str
    avatar_url: Optional[str] = None


def hash_password(password: str) -> str:
    """
    哈希密码
    
    Args:
        password: 明文密码
        
    Returns:
        哈希后的密码
    """
    salt = os.urandom(32)
    key = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt,
        100000
    )
    return salt.hex() + key.hex()


def verify_password(password: str, hashed_password: str) -> bool:
    """
    验证密码
    
    Args:
        password: 明文密码
        hashed_password: 哈希密码
        
    Returns:
        是否匹配
    """
    # 从哈希中提取盐值
    salt = bytes.fromhex(hashed_password[:64])
    stored_key = hashed_password[64:]
    
    # 使用相同盐值计算哈希
    key = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt,
        100000
    ).hex()
    
    return key == stored_key


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    创建JWT访问令牌
    
    Args:
        data: 令牌数据
        expires_delta: 过期时间增量
        
    Returns:
        JWT令牌字符串
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> TokenData:
    """
    验证JWT令牌
    
    Args:
        token: JWT令牌
        
    Returns:
        令牌数据
        
    Raises:
        HTTPException: 令牌无效或过期
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的认证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        nickname: str = payload.get("nickname")
        
        if user_id is None:
            raise credentials_exception
        
        return TokenData(user_id=user_id, nickname=nickname)
    except jwt.PyJWTError:
        raise credentials_exception


def generate_secure_password() -> str:
    """
    生成安全密码
    
    Returns:
        随机生成的密码
    """
    return secrets.token_urlsafe(16)


class AuthService:
    """认证服务"""
    
    def __init__(self, db_manager):
        """
        初始化认证服务
        
        Args:
            db_manager: 数据库管理器实例
        """
        self.db = db_manager
        
    def register_user(self, user_data: UserRegisterAuth) -> Dict[str, Any]:
        """
        注册新用户（带密码）
        
        Args:
            user_data: 用户注册数据
            
        Returns:
            注册结果
            
        Raises:
            HTTPException: 用户已存在或注册失败
        """
        # 检查用户是否已存在
        existing_user = self.db.get_user(user_data.user_id)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户ID已存在"
            )
        
        # 哈希密码
        hashed_password = hash_password(user_data.password)
        
        # 创建用户（需要扩展数据库以存储密码）
        # 这里假设数据库有add_user_with_password方法
        try:
            # 先使用现有方法创建用户
            success = self.db.create_user(
                user_id=user_data.user_id,
                nickname=user_data.nickname,
                avatar_url=user_data.avatar_url
            )
            
            if success:
                # 存储密码（需要扩展数据库）
                # self.db.store_user_password(user_data.user_id, hashed_password)
                
                # 生成访问令牌
                access_token = create_access_token(
                    data={"sub": user_data.user_id, "nickname": user_data.nickname}
                )
                
                return {
                    "success": True,
                    "user_id": user_data.user_id,
                    "nickname": user_data.nickname,
                    "access_token": access_token,
                    "token_type": "bearer"
                }
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="用户创建失败"
                )
                
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"注册失败: {str(e)}"
            )
    
    def authenticate_user(self, user_id: str, password: str) -> Optional[Dict[str, Any]]:
        """
        验证用户凭据
        
        Args:
            user_id: 用户ID
            password: 密码
            
        Returns:
            用户信息或None
        """
        # 获取用户（需要扩展数据库以获取密码）
        user = self.db.get_user(user_id)
        if not user:
            return None
        
        # 验证密码（需要扩展数据库以获取哈希密码）
        # hashed_password = self.db.get_user_password(user_id)
        # if not verify_password(password, hashed_password):
        #     return None
        
        # 临时实现：演示模式下允许任何密码
        # 在生产环境中，应该实现完整的密码验证
        
        return user
    
    def login_user(self, user_login: UserLogin) -> Dict[str, Any]:
        """
        用户登录
        
        Args:
            user_login: 登录请求
            
        Returns:
            登录结果
            
        Raises:
            HTTPException: 登录失败
        """
        user = self.authenticate_user(user_login.user_id, user_login.password)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 生成访问令牌
        access_token = create_access_token(
            data={"sub": user_login.user_id, "nickname": user.get("nickname", user_login.user_id)}
        )
        
        return {
            "success": True,
            "user_id": user_login.user_id,
            "nickname": user.get("nickname", user_login.user_id),
            "access_token": access_token,
            "token_type": "bearer"
        }


def get_current_user(token: str) -> TokenData:
    """
    获取当前用户（依赖注入）
    
    Args:
        token: Bearer令牌
        
    Returns:
        令牌数据
    """
    # 提取Bearer令牌
    if token.startswith("Bearer "):
        token = token[7:]
    
    return verify_token(token)


# 简易演示认证（不存储密码）
class DemoAuth:
    """演示认证（用于开发环境）"""
    
    @staticmethod
    def demo_login(user_id: str) -> Dict[str, Any]:
        """
        演示登录（不验证密码）
        
        Args:
            user_id: 用户ID
            
        Returns:
            登录结果
        """
        access_token = create_access_token(
            data={"sub": user_id, "nickname": user_id}
        )
        
        return {
            "success": True,
            "user_id": user_id,
            "access_token": access_token,
            "token_type": "bearer"
        }
    
    @staticmethod
    def demo_register(user_id: str, nickname: str) -> Dict[str, Any]:
        """
        演示注册
        
        Args:
            user_id: 用户ID
            nickname: 昵称
            
        Returns:
            注册结果
        """
        access_token = create_access_token(
            data={"sub": user_id, "nickname": nickname}
        )
        
        return {
            "success": True,
            "user_id": user_id,
            "nickname": nickname,
            "access_token": access_token,
            "token_type": "bearer"
        }