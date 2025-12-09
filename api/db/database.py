"""
数据库连接管理模块
使用asyncpg实现异步PostgreSQL连接
"""

import asyncpg
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    """
    数据库连接管理器
    """

    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None

    async def initialize(self, host: str, port: int, database: str, user: str, password: str):
        """
        初始化数据库连接池
        """
        try:
            self.pool = await asyncpg.create_pool(
                host=host,
                port=port,
                database=database,
                user=user,
                password=password,
                min_size=5,
                max_size=20,
                command_timeout=60
            )
            logger.info("✅ 数据库连接池初始化成功")
        except Exception as e:
            logger.error(f"❌ 数据库连接池初始化失败: {e}")
            raise

    async def close(self):
        """
        关闭数据库连接池
        """
        if self.pool:
            await self.pool.close()
            logger.info("✅ 数据库连接池已关闭")

    async def fetch(self, query: str, *args):
        """
        执行查询并返回所有结果
        """
        async with self.pool.acquire() as conn:
            return await conn.fetch(query, *args)

    async def fetchrow(self, query: str, *args):
        """
        执行查询并返回单行结果
        """
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(query, *args)

    async def fetchval(self, query: str, *args):
        """
        执行查询并返回单个值
        """
        async with self.pool.acquire() as conn:
            return await conn.fetchval(query, *args)

    async def execute(self, query: str, *args):
        """
        执行SQL语句
        """
        async with self.pool.acquire() as conn:
            return await conn.execute(query, *args)

    async def executemany(self, query: str, args_list):
        """
        批量执行SQL语句
        """
        async with self.pool.acquire() as conn:
            return await conn.executemany(query, args_list)

# 全局数据库管理器实例
db_manager = DatabaseManager()

async def init_db(host: str = "192.168.1.21", port: int = 5432, database: str = "postgres", user: str = "postgres", password: str = "axunrun0429"):
    """
    初始化数据库连接
    """
    await db_manager.initialize(host, port, database, user, password)

async def close_db():
    """
    关闭数据库连接
    """
    await db_manager.close()
