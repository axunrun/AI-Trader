"""
认证API路由
提供用户登录和认证功能
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import logging
import jwt
from datetime import datetime, timedelta

from api.models.schemas import (
    LoginRequest, LoginResponse,
    ApiResponse, ErrorResponse
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/auth", tags=["auth"])

# JWT配置（生产环境应使用环境变量）
JWT_SECRET_KEY = "your-secret-key-change-in-production"
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = 60 * 24  # 24小时

# 模拟用户数据库（生产环境应使用真实数据库）
MOCK_USERS = {
    "admin": {
        "username": "admin",
        "password": "admin123",
        "display_name": "管理员",
        "avatar": "👨‍💼",
        "role": "admin"
    },
    "user": {
        "username": "user",
        "password": "user123",
        "display_name": "用户",
        "avatar": "👤",
        "role": "user"
    },
    "demo": {
        "username": "demo",
        "password": "demo123",
        "display_name": "演示用户",
        "avatar": "📊",
        "role": "user"
    }
}

security = HTTPBearer()

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    创建JWT访问令牌
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=JWT_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    验证JWT令牌
    """
    try:
        payload = jwt.decode(
            credentials.credentials,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的认证凭据",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return username
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭据",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.post(
    "/login",
    response_model=LoginResponse,
    responses={401: {"model": ErrorResponse}, 500: {"model": ErrorResponse}}
)
async def login(login_request: LoginRequest):
    """
    用户登录

    - **username**: 用户名
    - **password**: 密码

    支持的测试用户：
    - admin / admin123
    - user / user123
    - demo / demo123
    """
    try:
        username = login_request.username
        password = login_request.password

        # 验证用户凭据
        user = MOCK_USERS.get(username)
        if not user or user["password"] != password:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # 创建JWT令牌
        access_token_expires = timedelta(minutes=JWT_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": username, "role": user["role"]},
            expires_delta=access_token_expires
        )

        # 返回用户信息
        user_info = {
            "username": user["username"],
            "display_name": user["display_name"],
            "avatar": user["avatar"],
            "role": user["role"]
        }

        return LoginResponse(
            success=True,
            token=access_token,
            user=user_info,
            expires_in=JWT_EXPIRE_MINUTES * 60
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"登录失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"登录失败: {str(e)}"
        )

@router.post(
    "/logout",
    response_model=ApiResponse,
    responses={401: {"model": ErrorResponse}}
)
async def logout(current_user: str = Depends(verify_token)):
    """
    用户注销

    注意：由于使用JWT令牌，注销通常由客户端删除令牌实现
    这里主要用于记录日志
    """
    try:
        logger.info(f"用户 {current_user} 注销")
        return ApiResponse(
            success=True,
            message="注销成功"
        )
    except Exception as e:
        logger.error(f"注销失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"注销失败: {str(e)}"
        )

@router.get(
    "/me",
    response_model=ApiResponse,
    responses={401: {"model": ErrorResponse}}
)
async def get_current_user_info(current_user: str = Depends(verify_token)):
    """
    获取当前用户信息

    需要在请求头中提供JWT令牌：
    Authorization: Bearer <token>
    """
    try:
        user = MOCK_USERS.get(current_user)
        if not user:
            raise HTTPException(
                status_code=404,
                detail="用户不存在"
            )

        user_info = {
            "username": user["username"],
            "display_name": user["display_name"],
            "avatar": user["avatar"],
            "role": user["role"],
            "last_login": datetime.now().isoformat()
        }

        return ApiResponse(
            success=True,
            message="获取用户信息成功",
            data=user_info
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取用户信息失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"获取用户信息失败: {str(e)}"
        )

@router.post(
    "/verify",
    response_model=ApiResponse,
    responses={401: {"model": ErrorResponse}}
)
async def verify_token_endpoint(current_user: str = Depends(verify_token)):
    """
    验证令牌是否有效

    用于前端定期检查登录状态
    """
    try:
        return ApiResponse(
            success=True,
            message="令牌有效",
            data={"username": current_user}
        )
    except Exception as e:
        logger.error(f"验证令牌失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"验证令牌失败: {str(e)}"
        )

@router.get(
    "/test-users",
    response_model=ApiResponse,
    responses={500: {"model": ErrorResponse}}
)
async def get_test_users():
    """
    获取测试用户列表（仅开发环境使用）
    """
    try:
        test_users = []
        for username, user in MOCK_USERS.items():
            test_users.append({
                "username": user["username"],
                "password": user["password"],
                "display_name": user["display_name"],
                "role": user["role"]
            })

        return ApiResponse(
            success=True,
            message="获取测试用户成功",
            data={"users": test_users}
        )

    except Exception as e:
        logger.error(f"获取测试用户失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"获取测试用户失败: {str(e)}"
        )
