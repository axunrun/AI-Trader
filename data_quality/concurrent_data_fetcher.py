#!/usr/bin/env python3
"""
并发数据获取优化器
使用asyncio和ThreadPoolExecutor实现高效的并发数据获取
"""

import asyncio
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class ConcurrentDataFetcher:
    """并发数据获取器"""

    def __init__(self, max_workers: int = 10, batch_size: int = 20, timeout: int = 30):
        self.max_workers = max_workers
        self.batch_size = batch_size
        self.timeout = timeout
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_time": 0,
            "average_time": 0
        }

    async def fetch_stock_pool_concurrent(self, stock_codes: List[str],
                                         fetch_func) -> Dict[str, Any]:
        """并发获取股票池数据

        Args:
            stock_codes: 股票代码列表
            fetch_func: 数据获取函数

        Returns:
            获取结果字典
        """
        start_time = time.time()
        self.stats["total_requests"] = len(stock_codes)

        logger.info(f"Starting concurrent fetch for {len(stock_codes)} stocks")

        # 分批处理
        batches = [stock_codes[i:i + self.batch_size]
                  for i in range(0, len(stock_codes), self.batch_size)]

        logger.info(f"Processing {len(batches)} batches of size {self.batch_size}")

        # 使用信号量控制并发数
        semaphore = asyncio.Semaphore(self.max_workers)

        async def fetch_batch_with_semaphore(batch):
            async with semaphore:
                return await self._fetch_batch(batch, fetch_func)

        # 并发执行所有批次
        tasks = [fetch_batch_with_semaphore(batch) for batch in batches]
        batch_results = await asyncio.gather(*tasks, return_exceptions=True)

        # 合并结果
        results = {}
        for batch_result in batch_results:
            if isinstance(batch_result, Exception):
                logger.error(f"Batch failed: {batch_result}")
                self.stats["failed_requests"] += self.batch_size
            else:
                results.update(batch_result)
                self.stats["successful_requests"] += len(batch_result)

        # 更新统计
        self.stats["total_time"] = time.time() - start_time
        if self.stats["total_requests"] > 0:
            self.stats["average_time"] = (
                self.stats["total_time"] / self.stats["total_requests"]
            )

        logger.info(f"Fetch completed in {self.stats['total_time']:.2f}s")
        logger.info(f"Success rate: {self.stats['successful_requests']}/{self.stats['total_requests']}")

        return results

    async def _fetch_batch(self, batch: List[str], fetch_func) -> Dict[str, Any]:
        """获取一批股票数据"""
        loop = asyncio.get_event_loop()
        results = {}

        # 使用线程池执行同步的fetch_func
        tasks = []
        for symbol in batch:
            task = loop.run_in_executor(
                self.executor,
                fetch_func,
                symbol
            )
            tasks.append((symbol, task))

        # 等待所有任务完成
        for symbol, task in tasks:
            try:
                result = await asyncio.wait_for(task, timeout=self.timeout)
                if result:
                    results[symbol] = result
            except asyncio.TimeoutError:
                logger.warning(f"Timeout fetching {symbol}")
                self.stats["failed_requests"] += 1
            except Exception as e:
                logger.error(f"Error fetching {symbol}: {e}")
                self.stats["failed_requests"] += 1

        return results

    async def fetch_with_retry(self, symbol: str, fetch_func,
                              max_retries: int = 3,
                              base_delay: float = 1.0) -> Optional[Dict[str, Any]]:
        """带重试的数据获取

        Args:
            symbol: 股票代码
            fetch_func: 获取函数
            max_retries: 最大重试次数
            base_delay: 基础延迟时间

        Returns:
            获取结果或None
        """
        for attempt in range(max_retries + 1):
            try:
                result = await asyncio.wait_for(
                    asyncio.get_event_loop().run_in_executor(
                        self.executor, fetch_func, symbol
                    ),
                    timeout=self.timeout
                )
                return result
            except Exception as e:
                if attempt < max_retries:
                    delay = base_delay * (2 ** attempt)  # 指数退避
                    logger.warning(f"Attempt {attempt + 1} failed for {symbol}: {e}, retrying in {delay}s")
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"All attempts failed for {symbol}: {e}")
                    return None

        return None

    def get_stats(self) -> Dict[str, Any]:
        """获取获取统计信息"""
        return {
            **self.stats,
            "success_rate": (
                self.stats["successful_requests"] / max(1, self.stats["total_requests"])
            ) * 100,
            "throughput": (
                self.stats["total_requests"] / max(0.001, self.stats["total_time"])
            )
        }

    def print_stats(self):
        """打印统计信息"""
        stats = self.get_stats()
        print("\n" + "=" * 60)
        print("并发数据获取统计")
        print("=" * 60)
        print(f"总请求数: {stats['total_requests']}")
        print(f"成功请求: {stats['successful_requests']}")
        print(f"失败请求: {stats['failed_requests']}")
        print(f"成功率: {stats['success_rate']:.2f}%")
        print(f"总耗时: {stats['total_time']:.2f}s")
        print(f"平均耗时: {stats['average_time']:.3f}s/请求")
        print(f"吞吐量: {stats['throughput']:.2f} 请求/秒")
        print("=" * 60)

    def cleanup(self):
        """清理资源"""
        self.executor.shutdown(wait=True)


# 模拟数据获取函数
def mock_fetch_func(symbol: str) -> Optional[Dict[str, Any]]:
    """模拟数据获取函数

    实际使用时替换为真实的数据获取逻辑
    """
    import random

    # 模拟网络延迟
    time.sleep(random.uniform(0.1, 0.5))

    # 模拟失败率
    if random.random() < 0.05:  # 5%失败率
        raise Exception(f"模拟网络错误: {symbol}")

    # 返回模拟数据
    return {
        "symbol": symbol,
        "date": "2025-12-09",
        "open": 100.0 + random.uniform(-5, 5),
        "high": 105.0 + random.uniform(-3, 3),
        "low": 98.0 + random.uniform(-3, 3),
        "close": 103.0 + random.uniform(-4, 4),
        "volume": random.randint(100000, 10000000),
        "timestamp": time.time()
    }


async def test_concurrent_fetcher():
    """测试并发数据获取器"""
    print("Testing Concurrent Data Fetcher")
    print("=" * 60)

    # 创建100个模拟股票代码
    test_symbols = [f"600{i:03d}.SH" for i in range(100)]

    # 创建获取器
    fetcher = ConcurrentDataFetcher(max_workers=10, batch_size=20)

    try:
        # 并发获取数据
        results = await fetcher.fetch_stock_pool_concurrent(
            test_symbols,
            mock_fetch_func
        )

        # 打印统计
        fetcher.print_stats()

        # 验证结果
        print(f"\n成功获取 {len(results)}/{len(test_symbols)} 只股票数据")

        # 保存示例数据
        if results:
            sample_data = dict(list(results.items())[:3])
            print("\n示例数据:")
            for symbol, data in sample_data.items():
                print(f"{symbol}: {data}")

    finally:
        fetcher.cleanup()


if __name__ == "__main__":
    # 运行测试
    asyncio.run(test_concurrent_fetcher())
