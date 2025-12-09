"""
AI-Trader FastAPI 后端服务
提供RESTful API接口给前端使用
"""

import logging
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn

from api.db.database import init_db, close_db
from api.routers import prices, positions, logs, indices, auth

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('api.log')
    ]
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    """
    # 启动时执行
    logger.info("🚀 启动AI-Trader API服务...")
    try:
        await init_db()
        logger.info("✅ 数据库连接成功")
    except Exception as e:
        logger.error(f"❌ 数据库连接失败: {e}")
        raise

    yield

    # 关闭时执行
    logger.info("🔄 关闭AI-Trader API服务...")
    await close_db()
    logger.info("✅ API服务已关闭")

# 创建FastAPI应用
app = FastAPI(
    title="AI-Trader API",
    description="A股AI交易分析平台后端API",
    version="1.0.0",
    lifespan=lifespan
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(prices.router)
app.include_router(positions.router)
app.include_router(logs.router)
app.include_router(indices.router)
app.include_router(auth.router)

@app.get("/", tags=["root"])
async def root():
    """
    根路径，返回API信息
    """
    return {
        "message": "AI-Trader API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running"
    }

@app.get("/health", tags=["health"])
async def health_check():
    """
    健康检查接口
    """
    return {
        "status": "healthy",
        "timestamp": "2025-12-10T00:00:00Z"
    }

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    HTTP异常处理器
    """
    logger.warning(f"HTTP异常: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
            "timestamp": "2025-12-10T00:00:00Z"
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    通用异常处理器
    """
    logger.error(f"未处理异常: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "内部服务器错误",
            "timestamp": "2025-12-10T00:00:00Z"
        }
    )

if __name__ == "__main__":
    # 运行开发服务器
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
