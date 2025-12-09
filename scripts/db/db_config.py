"""
AI-Trader PostgreSQL 数据库配置
支持TimescaleDB时间序列数据库扩展
"""

import os
from typing import Dict, Optional

# 数据库连接配置
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "192.168.1.21"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "database": os.getenv("DB_NAME", "postgres"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "axunrun0429"),
    "min_connections": 5,
    "max_connections": 20,
    "command_timeout": 60
}

# TimescaleDB配置
TIMESCALEDB_CONFIG = {
    "enabled": True,
    "compression_age": "7 days",
    "retention_period": "2 years",
    "chunk_interval": "1 day",
    "continuous_aggregate": {
        "refresh_interval": "1 hour",
        "max_offset": "30 minutes"
    }
}

# 数据表配置
TABLE_CONFIG = {
    "stock_prices": {
        "hypertable": True,
        "time_column": "timestamp",
        "compression_policy": "7 days",
        "retention_policy": "2 years"
    },
    "index_prices": {
        "hypertable": True,
        "time_column": "timestamp",
        "compression_policy": "7 days",
        "retention_policy": "2 years"
    },
    "position_history": {
        "hypertable": False,
        "retention_policy": "2 years"
    },
    "trade_logs": {
        "hypertable": False,
        "retention_policy": "2 years"
    }
}

# 索引配置
INDEX_CONFIG = {
    "stock_prices": [
        "idx_stock_prices_symbol",
        "idx_stock_prices_timestamp",
        "idx_stock_prices_symbol_timestamp"
    ],
    "index_prices": [
        "idx_index_prices_code",
        "idx_index_prices_timestamp"
    ],
    "position_history": [
        "idx_position_agent",
        "idx_position_date",
        "idx_position_agent_date"
    ],
    "trade_logs": [
        "idx_logs_agent",
        "idx_logs_timestamp",
        "idx_logs_type"
    ]
}

# 连续聚合配置
CONTINUOUS_AGGREGATE_CONFIG = {
    "weekly_stock_prices": {
        "time_bucket": "1 week",
        "refresh_interval": "1 hour",
        "max_offset": "30 minutes"
    },
    "monthly_stock_prices": {
        "time_bucket": "1 month",
        "refresh_interval": "1 day",
        "max_offset": "1 hour"
    },
    "weekly_index_prices": {
        "time_bucket": "1 week",
        "refresh_interval": "1 hour",
        "max_offset": "30 minutes"
    },
    "monthly_index_prices": {
        "time_bucket": "1 month",
        "refresh_interval": "1 day",
        "max_offset": "1 hour"
    }
}

# 数据源配置
DATA_SOURCE_CONFIG = {
    "tushare": {
        "enabled": True,
        "token": os.getenv("TUSHARE_TOKEN"),
        "daily_batch_size": 100,
        "rate_limit": 500  # 每分钟请求数
    },
    "efinance": {
        "enabled": True,
        "realtime_refresh_interval": 5  # 秒
    }
}

# 查询配置
QUERY_CONFIG = {
    "default_time_range": "30 days",
    "max_results": 10000,
    "timeout": 30,
    "cache_ttl": 300  # 5分钟
}

# 迁移配置
MIGRATION_CONFIG = {
    "batch_size": 1000,
    "retry_attempts": 3,
    "retry_delay": 5,  # 秒
    "validate_data": True,
    "backup_before_migration": True
}

def get_database_url() -> str:
    """
    获取数据库连接URL
    """
    config = DB_CONFIG
    return (
        f"postgresql://{config['user']}:{config['password']}"
        f"@{config['host']}:{config['port']}/{config['database']}"
    )

def get_async_database_url() -> str:
    """
    获取异步数据库连接URL
    """
    config = DB_CONFIG
    return (
        f"postgresql+asyncpg://{config['user']}:{config['password']}"
        f"@{config['host']}:{config['port']}/{config['database']}"
    )

def get_connection_params() -> Dict:
    """
    获取数据库连接参数
    """
    return {
        "host": DB_CONFIG["host"],
        "port": DB_CONFIG["port"],
        "database": DB_CONFIG["database"],
        "user": DB_CONFIG["user"],
        "password": DB_CONFIG["password"],
        "min_size": DB_CONFIG["min_connections"],
        "max_size": DB_CONFIG["max_connections"],
        "command_timeout": DB_CONFIG["command_timeout"]
    }

def is_timescaledb_enabled() -> bool:
    """
    检查TimescaleDB是否启用
    """
    return TIMESCALEDB_CONFIG["enabled"]

def get_table_config(table_name: str) -> Optional[Dict]:
    """
    获取指定表的配置
    """
    return TABLE_CONFIG.get(table_name)

def get_index_config(table_name: str) -> list:
    """
    获取指定表的索引配置
    """
    return INDEX_CONFIG.get(table_name, [])

def get_continuous_aggregate_config(view_name: str) -> Optional[Dict]:
    """
    获取连续聚合配置
    """
    return CONTINUOUS_AGGREGATE_CONFIG.get(view_name)

class DatabaseManager:
    """
    数据库管理器
    提供数据库连接和基本操作
    """

    def __init__(self):
        self.config = DB_CONFIG
        self._connection_pool = None

    async def initialize(self):
        """
        初始化数据库连接池
        """
        try:
            import asyncpg
            self._connection_pool = await asyncpg.create_pool(
                **get_connection_params()
            )
            print("✅ 数据库连接池初始化成功")
        except Exception as e:
            print(f"❌ 数据库连接池初始化失败: {e}")
            raise

    async def close(self):
        """
        关闭数据库连接池
        """
        if self._connection_pool:
            await self._connection_pool.close()
            print("✅ 数据库连接池已关闭")

    async def test_connection(self) -> bool:
        """
        测试数据库连接
        """
        try:
            async with self._connection_pool.acquire() as conn:
                result = await conn.fetchval("SELECT 1")
                print("✅ 数据库连接测试成功")
                return True
        except Exception as e:
            print(f"❌ 数据库连接测试失败: {e}")
            return False

    async def check_timescaledb(self) -> bool:
        """
        检查TimescaleDB扩展是否安装
        """
        try:
            async with self._connection_pool.acquire() as conn:
                result = await conn.fetchval(
                    "SELECT EXISTS(SELECT 1 FROM pg_extension WHERE extname = 'timescaledb')"
                )
                if result:
                    print("✅ TimescaleDB扩展已安装")
                else:
                    print("⚠️  TimescaleDB扩展未安装")
                return result
        except Exception as e:
            print(f"❌ 检查TimescaleDB失败: {e}")
            return False

    async def get_table_stats(self) -> Dict:
        """
        获取数据库表统计信息
        """
        stats = {}
        try:
            async with self._connection_pool.acquire() as conn:
                # 获取表列表
                tables = await conn.fetch("""
                    SELECT tablename
                    FROM pg_tables
                    WHERE schemaname = 'public'
                    AND tabletype = 'BASE TABLE'
                """)

                for table in tables:
                    table_name = table['tablename']
                    # 获取行数
                    count = await conn.fetchval(f"SELECT COUNT(*) FROM {table_name}")
                    stats[table_name] = {"rows": count}

                print("✅ 数据库表统计信息获取成功")
        except Exception as e:
            print(f"❌ 获取表统计信息失败: {e}")

        return stats

# 全局数据库管理器实例
db_manager = DatabaseManager()

# 导出常用配置
__all__ = [
    'DB_CONFIG',
    'TIMESCALEDB_CONFIG',
    'TABLE_CONFIG',
    'INDEX_CONFIG',
    'CONTINUOUS_AGGREGATE_CONFIG',
    'DATA_SOURCE_CONFIG',
    'QUERY_CONFIG',
    'MIGRATION_CONFIG',
    'get_database_url',
    'get_async_database_url',
    'get_connection_params',
    'is_timescaledb_enabled',
    'get_table_config',
    'get_index_config',
    'get_continuous_aggregate_config',
    'DatabaseManager',
    'db_manager'
]
