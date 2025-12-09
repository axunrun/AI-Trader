#!/usr/bin/env python3
"""
A股股票池管理器
支持多板块股票池管理，包括上证50、上证180、深证100、创业板指、科创50等
"""

import os
import json
import pandas as pd
from typing import List, Dict, Optional
from pathlib import Path


class AStockPoolManager:
    """A股股票池管理器"""

    def __init__(self):
        self.pools = {
            "sse50": {"codes": [], "name": "上证50", "index_code": "000016.SH"},
            "sse180": {"codes": [], "name": "上证180", "index_code": "000010.SH"},
            "sz100": {"codes": [], "name": "深证100", "index_code": "000004.SZ"},
            "cyb100": {"codes": [], "name": "创业板100", "index_code": "399006.SZ"},
            "kc50": {"codes": [], "name": "科创50", "index_code": "000688.SH"},
        }

        # 初始化Tushare API
        self.pro = None
        self.tushare_available = False

        try:
            import tushare as ts

            # 尝试从环境变量获取token
            token = os.getenv('TUSHARE_TOKEN')
            if token:
                try:
                    self.pro = ts.pro_api(token)
                    self.tushare_available = True
                    print("[OK] Tushare API initialized")
                except Exception as e:
                    print(f"[WARN] Failed to initialize Tushare with token: {e}")
                    self.pro = None
                    self.tushare_available = False
            else:
                # 尝试无token初始化（可能有限制）
                try:
                    self.pro = ts.pro_api()
                    self.tushare_available = True
                    print("[OK] Tushare API initialized (no token, limited calls)")
                except Exception as e:
                    print(f"[WARN] Tushare not configured, using fallback methods: {e}")
                    self.pro = None
                    self.tushare_available = False
        except ImportError:
            print("[WARN] Tushare not installed, using fallback methods")
            self.pro = None
            self.tushare_available = False

    def fetch_pool_stocks(self, pool_name: str) -> List[str]:
        """获取指定板块的成分股"""
        if pool_name not in self.pools:
            raise ValueError(f"Unsupported pool: {pool_name}")

        pool_info = self.pools[pool_name]

        try:
            if pool_name == "sse50":
                # 上证50使用现有逻辑
                return self._get_sse50()
            elif pool_name in ["sse180", "sz100", "cyb100", "kc50"]:
                # 其他板块使用模拟数据（如果没有Tushare token）
                return self._get_mock_pool_data(pool_name)
            else:
                # 使用Tushare API
                return self._get_index_stocks(
                    pool_info["index_code"],
                    pool_name
                )
        except Exception as e:
            print(f"[ERROR] Failed to get {pool_info['name']}: {e}")
            return []

    def _get_sse50(self) -> List[str]:
        """获取上证50成分股（现有逻辑）"""
        # 读取CSV文件
        csv_path = Path(__file__).parent / "A_stock_data" / "sse_50_weight.csv"

        if not csv_path.exists():
            print(f"[ERROR] SSE50 file not found: {csv_path}")
            return []

        try:
            df = pd.read_csv(csv_path)
            codes = df['con_code'].tolist()
            # 转换为标准格式（如：600519.SH保持不变，或者转换为600519.SS）
            # 这里我们保持.SH和.SZ格式不变，因为其他模块也使用这种格式
            return codes
        except Exception as e:
            print(f"[ERROR] Failed to read SSE50 data: {e}")
            return []

    def _get_mock_pool_data(self, pool_name: str) -> List[str]:
        """获取模拟股票池数据"""
        csv_files = {
            "sse180": "sse_180_weight.csv",
            "sz100": "sz_100_weight.csv",
            "cyb100": "cyb_100_weight.csv",
            "kc50": "kc_50_weight.csv"
        }

        if pool_name not in csv_files:
            return []

        csv_path = Path(__file__).parent / "A_stock_data" / csv_files[pool_name]

        if not csv_path.exists():
            print(f"[WARN] Mock data file not found: {csv_path}")
            return []

        try:
            df = pd.read_csv(csv_path)
            codes = df['con_code'].tolist()
            return codes
        except Exception as e:
            print(f"[ERROR] Failed to read {pool_name} data: {e}")
            return []

    def _get_index_stocks(self, index_code: str, pool_name: str) -> List[str]:
        """获取指数成分股的通用方法"""
        if not self.tushare_available or self.pro is None:
            print(f"[WARN] Tushare not available, skipping {index_code}")
            return []

        try:
            # 使用tushare获取指数成分股
            df = self.pro.index_weight(index_code=index_code)

            if df.empty:
                print(f"[WARN] No data for index {index_code}")
                return []

            # 提取股票代码并转换为标准格式
            codes = []
            for _, row in df.iterrows():
                code = row['con_code']

                # 转换为标准格式
                if code.startswith('6'):
                    # 上海股票
                    standard_code = f"{code}.SH"
                elif code.startswith(('0', '3')):
                    # 深圳股票
                    standard_code = f"{code}.SZ"
                else:
                    standard_code = code

                codes.append(standard_code)

            print(f"[OK] Got {pool_name} stocks: {len(codes)}")
            return codes

        except Exception as e:
            print(f"[ERROR] Failed to get index {index_code} stocks: {e}")
            return []

    def fetch_all_pools(self) -> Dict[str, List[str]]:
        """获取所有板块的股票池"""
        results = {}

        for pool_name in self.pools.keys():
            print(f"\n[INFO] Fetching {self.pools[pool_name]['name']}...")
            codes = self.fetch_pool_stocks(pool_name)
            results[pool_name] = codes
            self.pools[pool_name]["codes"] = codes

        return results

    def get_balanced_portfolio(self, total_stocks: int = 300) -> List[str]:
        """选择平衡型投资组合"""
        # 各板块股票数量分配
        pool_allocation = {
            "sse50": 50,      # 保留现有上证50
            "sse180": 80,     # 上证180
            "sz100": 80,      # 深证100
            "cyb100": 50,     # 创业板100
            "kc50": 40,       # 科创50
        }

        selected_stocks = []

        # 从每个板块选择股票
        for pool_name, count in pool_allocation.items():
            if pool_name not in self.pools or not self.pools[pool_name]["codes"]:
                continue

            available_stocks = self.pools[pool_name]["codes"]
            # 简单取前N只（实际应该按市值等指标排序）
            selected = available_stocks[:count]
            selected_stocks.extend(selected)

            print(f"[OK] Selected {len(selected)} stocks from {self.pools[pool_name]['name']}")

        # 如果总数量不足，用上证50补足
        if len(selected_stocks) < total_stocks:
            remaining = total_stocks - len(selected_stocks)
            sse50_stocks = self.pools.get("sse50", {}).get("codes", [])

            # 添加未选中的上证50股票
            already_selected = set(selected_stocks)
            for stock in sse50_stocks:
                if stock not in already_selected and remaining > 0:
                    selected_stocks.append(stock)
                    remaining -= 1

        print(f"\n[INFO] Total selected stocks: {len(selected_stocks)}")
        return selected_stocks[:total_stocks]

    def save_pool_config(self, output_path: str = None):
        """保存股票池配置到JSON文件"""
        if output_path is None:
            output_path = Path(__file__).parent / "stock_pools_config.json"

        config = {
            "pools": {},
            "total_stocks": 0,
            "updated_at": "2025-12-09",
            "version": "2.0"
        }

        for pool_name, pool_info in self.pools.items():
            config["pools"][pool_name] = {
                "name": pool_info["name"],
                "codes": pool_info["codes"],
                "count": len(pool_info["codes"])
            }
            config["total_stocks"] += len(pool_info["codes"])

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

        print(f"[OK] Stock pool config saved to: {output_path}")

    def load_pool_config(self, config_path: str = None):
        """从JSON文件加载股票池配置"""
        if config_path is None:
            config_path = Path(__file__).parent / "stock_pools_config.json"

        if not os.path.exists(config_path):
            print(f"[WARN] Config file not found: {config_path}")
            return

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            for pool_name, pool_data in config.get("pools", {}).items():
                if pool_name in self.pools:
                    self.pools[pool_name]["codes"] = pool_data.get("codes", [])

            print(f"[OK] Loaded stock pool config, total {config.get('total_stocks', 0)} stocks")
        except Exception as e:
            print(f"[ERROR] Failed to load config: {e}")


if __name__ == "__main__":
    def main():
        manager = AStockPoolManager()

        # 获取所有板块股票
        print("[INFO] Starting to fetch A-stock sector pools...")
        manager.fetch_all_pools()

        # 生成平衡型投资组合
        print("\n[INFO] Generating balanced portfolio (300 stocks)...")
        portfolio = manager.get_balanced_portfolio(300)

        # 保存配置
        manager.save_pool_config()

        # 打印结果
        print(f"\n[INFO] Final portfolio contains {len(portfolio)} stocks")
        print("First 10 stocks:", portfolio[:10])

    # 运行
    main()
