"""
JSONL数据迁移到PostgreSQL脚本
将AI-Trader的JSONL格式数据迁移到PostgreSQL + TimescaleDB数据库
"""

import os
import sys
import json
import asyncio
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional
import asyncpg
from tqdm import tqdm

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.db.db_config import (
    DB_CONFIG, MIGRATION_CONFIG, get_connection_params,
    db_manager
)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('migration.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class JSONLToPostgreSQLMigrator:
    """
    JSONL到PostgreSQL迁移器
    """

    def __init__(self):
        self.connection_params = get_connection_params()
        self.batch_size = MIGRATION_CONFIG["batch_size"]
        self.retry_attempts = MIGRATION_CONFIG["retry_attempts"]
        self.retry_delay = MIGRATION_CONFIG["retry_delay"]

    async def migrate_all(self):
        """
        执行所有迁移任务
        """
        logger.info("🚀 开始JSONL到PostgreSQL迁移...")

        try:
            # 初始化数据库连接
            await db_manager.initialize()

            # 检查TimescaleDB
            if not await db_manager.check_timescaledb():
                logger.error("❌ TimescaleDB扩展未安装，无法继续迁移")
                return False

            # 执行迁移
            results = {}

            # 1. 迁移股票价格数据
            logger.info("📊 迁移股票价格数据...")
            results['stock_prices'] = await self.migrate_stock_prices()

            # 2. 迁移持仓历史数据
            logger.info("💼 迁移持仓历史数据...")
            results['position_history'] = await self.migrate_position_history()

            # 3. 迁移交易日志数据
            logger.info("📝 迁移交易日志数据...")
            results['trade_logs'] = await self.migrate_trade_logs()

            # 4. 迁移指数数据
            logger.info("📈 迁移指数数据...")
            results['index_prices'] = await self.migrate_index_prices()

            # 生成迁移报告
            await self.generate_migration_report(results)

            logger.info("✅ 所有迁移任务完成!")
            return True

        except Exception as e:
            logger.error(f"❌ 迁移过程中发生错误: {e}", exc_info=True)
            return False
        finally:
            await db_manager.close()

    async def migrate_stock_prices(self) -> Dict[str, Any]:
        """
        迁移股票价格数据 (merged.jsonl)
        """
        results = {
            "total_files": 0,
            "total_records": 0,
            "success_records": 0,
            "error_records": 0,
            "errors": []
        }

        data_dir = Path("/e/project/AI-Trader/data/A_stock")
        jsonl_file = data_dir / "merged.jsonl"

        if not jsonl_file.exists():
            logger.warning(f"⚠️  文件不存在: {jsonl_file}")
            return results

        try:
            async with db_manager._connection_pool.acquire() as conn:
                # 清空现有数据
                await conn.execute("TRUNCATE TABLE stock_prices RESTART IDENTITY CASCADE")

                records = []
                total_lines = 0

                logger.info(f"📖 读取文件: {jsonl_file}")
                with open(jsonl_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        total_lines += 1

                logger.info(f"📊 总共 {total_lines} 条记录需要迁移")

                # 重新读取并处理数据
                with open(jsonl_file, 'r', encoding='utf-8') as f:
                    for line in tqdm(f, total=total_lines, desc="迁移股票价格"):
                        try:
                            data = json.loads(line.strip())
                            record = self.parse_stock_price_record(data)
                            if record:
                                records.append(record)

                                if len(records) >= self.batch_size:
                                    await self.insert_stock_prices_batch(conn, records)
                                    results['success_records'] += len(records)
                                    records = []

                        except Exception as e:
                            results['error_records'] += 1
                            results['errors'].append(f"第{total_lines}行: {str(e)}")
                            logger.warning(f"解析失败: {line[:100]}... 错误: {e}")

                # 插入剩余记录
                if records:
                    await self.insert_stock_prices_batch(conn, records)
                    results['success_records'] += len(records)

                results['total_files'] = 1
                results['total_records'] = total_lines

                # 更新连续聚合视图
                await self.refresh_continuous_aggregates(conn)

                logger.info(f"✅ 股票价格数据迁移完成: {results['success_records']}/{total_lines} 成功")

        except Exception as e:
            logger.error(f"❌ 迁移股票价格数据失败: {e}", exc_info=True)
            results['errors'].append(str(e))

        return results

    def parse_stock_price_record(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        解析股票价格记录
        """
        try:
            # 处理时间戳
            if 'timestamp' in data:
                timestamp = data['timestamp']
            elif 'date' in data:
                timestamp = f"{data['date']} 00:00:00"
            else:
                return None

            # 标准化字段名
            symbol = data.get('symbol') or data.get('ts_code')
            if not symbol:
                return None

            return {
                'symbol': symbol,
                'timestamp': timestamp,
                'open_price': float(data.get('open', 0)),
                'high_price': float(data.get('high', 0)),
                'low_price': float(data.get('low', 0)),
                'close_price': float(data.get('close', 0)),
                'volume': int(data.get('volume', 0)),
                'turnover': float(data.get('turnover', 0)),
                'change_pct': float(data.get('change_pct', 0)),
                'meta_data': data
            }
        except Exception as e:
            logger.warning(f"解析股票价格记录失败: {e}")
            return None

    async def insert_stock_prices_batch(self, conn, records: List[Dict]):
        """
        批量插入股票价格数据
        """
        query = """
            INSERT INTO stock_prices (
                symbol, timestamp, open_price, high_price, low_price,
                close_price, volume, turnover, change_pct, meta_data
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
            ON CONFLICT (symbol, timestamp) DO UPDATE SET
                open_price = EXCLUDED.open_price,
                high_price = EXCLUDED.high_price,
                low_price = EXCLUDED.low_price,
                close_price = EXCLUDED.close_price,
                volume = EXCLUDED.volume,
                turnover = EXCLUDED.turnover,
                change_pct = EXCLUDED.change_pct,
                meta_data = EXCLUDED.meta_data,
                updated_at = NOW()
        """

        values = []
        for record in records:
            values.append((
                record['symbol'],
                record['timestamp'],
                record['open_price'],
                record['high_price'],
                record['low_price'],
                record['close_price'],
                record['volume'],
                record['turnover'],
                record['change_pct'],
                json.dumps(record['meta_data'])
            ))

        await conn.executemany(query, values)

    async def migrate_position_history(self) -> Dict[str, Any]:
        """
        迁移持仓历史数据
        """
        results = {
            "total_files": 0,
            "total_records": 0,
            "success_records": 0,
            "error_records": 0,
            "errors": []
        }

        data_dir = Path("/e/project/AI-Trader/data/agent_data_astock")
        if not data_dir.exists():
            logger.warning(f"⚠️  目录不存在: {data_dir}")
            return results

        try:
            async with db_manager._connection_pool.acquire() as conn:
                await conn.execute("TRUNCATE TABLE position_history RESTART IDENTITY CASCADE")

                # 遍历所有代理目录
                agent_dirs = [d for d in data_dir.iterdir() if d.is_dir()]
                logger.info(f"📁 找到 {len(agent_dirs)} 个代理目录")

                for agent_dir in tqdm(agent_dirs, desc="迁移持仓数据"):
                    agent_name = agent_dir.name
                    position_file = agent_dir / "position" / "position.jsonl"

                    if not position_file.exists():
                        continue

                    records = []
                    total_lines = 0

                    # 统计行数
                    with open(position_file, 'r', encoding='utf-8') as f:
                        total_lines = sum(1 for _ in f)

                    logger.info(f"📊 迁移代理 {agent_name}: {total_lines} 条记录")

                    # 读取并处理数据
                    with open(position_file, 'r', encoding='utf-8') as f:
                        for line in f:
                            try:
                                data = json.loads(line.strip())
                                record = self.parse_position_record(data, agent_name)
                                if record:
                                    records.append(record)

                                    if len(records) >= self.batch_size:
                                        await self.insert_positions_batch(conn, records)
                                        results['success_records'] += len(records)
                                        records = []

                            except Exception as e:
                                results['error_records'] += 1
                                results['errors'].append(f"{agent_name}: {str(e)}")

                    # 插入剩余记录
                    if records:
                        await self.insert_positions_batch(conn, records)
                        results['success_records'] += len(records)

                    results['total_files'] += 1
                    results['total_records'] += total_lines

                logger.info(f"✅ 持仓历史数据迁移完成: {results['success_records']}/{results['total_records']} 成功")

        except Exception as e:
            logger.error(f"❌ 迁移持仓历史数据失败: {e}", exc_info=True)
            results['errors'].append(str(e))

        return results

    def parse_position_record(self, data: Dict[str, Any], agent_name: str) -> Optional[Dict[str, Any]]:
        """
        解析持仓记录
        """
        try:
            return {
                'agent_name': agent_name,
                'trade_date': data.get('date'),
                'trade_time': data.get('timestamp'),
                'action': data.get('this_action', {}).get('action', 'hold'),
                'symbol': data.get('this_action', {}).get('symbol'),
                'amount': int(data.get('this_action', {}).get('amount', 0)),
                'price': float(data.get('this_action', {}).get('price', 0)),
                'cash': float(data.get('cash', 0)),
                'total_value': float(data.get('total_value', 0)),
                'positions': json.dumps(data.get('positions', {})),
                'reasoning': data.get('reasoning', ''),
                'meta_data': data
            }
        except Exception as e:
            logger.warning(f"解析持仓记录失败: {e}")
            return None

    async def insert_positions_batch(self, conn, records: List[Dict]):
        """
        批量插入持仓数据
        """
        query = """
            INSERT INTO position_history (
                agent_name, trade_date, trade_time, action, symbol,
                amount, price, cash, total_value, positions, reasoning, meta_data
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
        """

        values = []
        for record in records:
            values.append((
                record['agent_name'],
                record['trade_date'],
                record['trade_time'],
                record['action'],
                record['symbol'],
                record['amount'],
                record['price'],
                record['cash'],
                record['total_value'],
                record['positions'],
                record['reasoning'],
                json.dumps(record['meta_data'])
            ))

        await conn.executemany(query, values)

    async def migrate_trade_logs(self) -> Dict[str, Any]:
        """
        迁移交易日志数据
        """
        results = {
            "total_files": 0,
            "total_records": 0,
            "success_records": 0,
            "error_records": 0,
            "errors": []
        }

        data_dir = Path("/e/project/AI-Trader/data/agent_data_astock")
        if not data_dir.exists():
            return results

        try:
            async with db_manager._connection_pool.acquire() as conn:
                await conn.execute("TRUNCATE TABLE trade_logs RESTART IDENTITY CASCADE")

                agent_dirs = [d for d in data_dir.iterdir() if d.is_dir()]

                for agent_dir in tqdm(agent_dirs, desc="迁移日志数据"):
                    agent_name = agent_dir.name
                    log_dir = agent_dir / "log"

                    if not log_dir.exists():
                        continue

                    # 遍历所有日期目录
                    for date_dir in log_dir.iterdir():
                        if not date_dir.is_dir():
                            continue

                        log_file = date_dir / "log.jsonl"
                        if not log_file.exists():
                            continue

                        records = []
                        total_lines = 0

                        # 统计行数
                        with open(log_file, 'r', encoding='utf-8') as f:
                            total_lines = sum(1 for _ in f)

                        # 读取并处理数据
                        with open(log_file, 'r', encoding='utf-8') as f:
                            for line in f:
                                try:
                                    data = json.loads(line.strip())
                                    record = self.parse_trade_log_record(data, agent_name, date_dir.name)
                                    if record:
                                        records.append(record)

                                        if len(records) >= self.batch_size:
                                            await self.insert_trade_logs_batch(conn, records)
                                            results['success_records'] += len(records)
                                            records = []

                                except Exception as e:
                                    results['error_records'] += 1
                                    results['errors'].append(f"{agent_name}/{date_dir.name}: {str(e)}")

                        # 插入剩余记录
                        if records:
                            await self.insert_trade_logs_batch(conn, records)
                            results['success_records'] += len(records)

                        results['total_files'] += 1
                        results['total_records'] += total_lines

                logger.info(f"✅ 交易日志数据迁移完成: {results['success_records']}/{results['total_records']} 成功")

        except Exception as e:
            logger.error(f"❌ 迁移交易日志数据失败: {e}", exc_info=True)
            results['errors'].append(str(e))

        return results

    def parse_trade_log_record(self, data: Dict[str, Any], agent_name: str, log_date: str) -> Optional[Dict[str, Any]]:
        """
        解析交易日志记录
        """
        try:
            return {
                'agent_name': agent_name,
                'log_timestamp': data.get('timestamp'),
                'log_date': log_date,
                'log_type': data.get('type', 'market_analysis'),
                'summary': data.get('summary', ''),
                'content': json.dumps(data),
                'tokens_used': int(data.get('tokens_used', 0)),
                'processing_time_ms': int(data.get('processing_time_ms', 0))
            }
        except Exception as e:
            logger.warning(f"解析交易日志记录失败: {e}")
            return None

    async def insert_trade_logs_batch(self, conn, records: List[Dict]):
        """
        批量插入交易日志数据
        """
        query = """
            INSERT INTO trade_logs (
                agent_name, log_timestamp, log_date, log_type,
                summary, content, tokens_used, processing_time_ms
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
        """

        values = []
        for record in records:
            values.append((
                record['agent_name'],
                record['log_timestamp'],
                record['log_date'],
                record['log_type'],
                record['summary'],
                record['content'],
                record['tokens_used'],
                record['processing_time_ms']
            ))

        await conn.executemany(query, values)

    async def migrate_index_prices(self) -> Dict[str, Any]:
        """
        迁移指数价格数据
        """
        results = {
            "total_files": 0,
            "total_records": 0,
            "success_records": 0,
            "error_records": 0,
            "errors": []
        }

        # 这里可以添加指数数据的迁移逻辑
        # 目前主要是为了演示结构

        logger.info("ℹ️  指数数据迁移功能待实现")

        return results

    async def refresh_continuous_aggregates(self, conn):
        """
        刷新连续聚合视图
        """
        try:
            logger.info("🔄 刷新连续聚合视图...")

            await conn.execute("SELECT refresh_continuous_aggregate('weekly_stock_prices', NOW() - INTERVAL '1 year', NOW())")
            await conn.execute("SELECT refresh_continuous_aggregate('monthly_stock_prices', NOW() - INTERVAL '2 years', NOW())")

            logger.info("✅ 连续聚合视图刷新完成")
        except Exception as e:
            logger.warning(f"⚠️  刷新连续聚合视图失败: {e}")

    async def generate_migration_report(self, results: Dict[str, Any]):
        """
        生成迁移报告
        """
        report = {
            "migration_time": datetime.now().isoformat(),
            "summary": {
                "total_tables": len(results),
                "total_files": sum(r.get('total_files', 0) for r in results.values()),
                "total_records": sum(r.get('total_records', 0) for r in results.values()),
                "success_records": sum(r.get('success_records', 0) for r in results.values()),
                "error_records": sum(r.get('error_records', 0) for r in results.values())
            },
            "details": results
        }

        report_file = Path("migration_report.json")
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        logger.info(f"📄 迁移报告已保存到: {report_file}")
        logger.info(f"📊 迁移摘要: {report['summary']}")

async def main():
    """
    主函数
    """
    logger.info("=" * 60)
    logger.info("🚀 AI-Trader JSONL 到 PostgreSQL 迁移工具")
    logger.info("=" * 60)

    migrator = JSONLToPostgreSQLMigrator()
    success = await migrator.migrate_all()

    if success:
        logger.info("✅ 迁移完成!")
        sys.exit(0)
    else:
        logger.error("❌ 迁移失败!")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
