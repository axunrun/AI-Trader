#!/usr/bin/env python3
"""
创建模拟股票池数据
用于演示股票池管理器功能，无需Tushare API
"""

import pandas as pd
import random
from pathlib import Path

def create_sse180_data():
    """创建上证180模拟数据"""
    # 上证180包含180只股票，我们模拟生成
    codes = []
    for i in range(180):
        # 生成6位数字代码
        code_num = random.randint(600000, 603999)
        codes.append(f"{code_num}.SH")

    df = pd.DataFrame({
        'index_code': ['000010.SH'] * 180,
        'con_code': codes,
        'trade_date': ['20250930'] * 180,
        'weight': [random.uniform(0.1, 2.0) for _ in range(180)],
        'stock_name': [f'股票{i+1:03d}' for i in range(180)]
    })

    return df

def create_sz100_data():
    """创建深证100模拟数据"""
    codes = []
    for i in range(100):
        # 深证股票以000或002开头
        if random.random() < 0.5:
            code_num = random.randint(0, 999)
            codes.append(f"{code_num:06d}.SZ")
        else:
            code_num = random.randint(2000, 3999)
            codes.append(f"{code_num:04d}.SZ")

    df = pd.DataFrame({
        'index_code': ['000004.SZ'] * 100,
        'con_code': codes,
        'trade_date': ['20250930'] * 100,
        'weight': [random.uniform(0.2, 3.0) for _ in range(100)],
        'stock_name': [f'深证股票{i+1:03d}' for i in range(100)]
    })

    return df

def create_cyb100_data():
    """创建创业板100模拟数据"""
    codes = []
    for i in range(100):
        # 创业板股票以300开头
        code_num = random.randint(300000, 399999)
        codes.append(f"{code_num}.SZ")

    df = pd.DataFrame({
        'index_code': ['399006.SZ'] * 100,
        'con_code': codes,
        'trade_date': ['20250930'] * 100,
        'weight': [random.uniform(0.3, 2.5) for _ in range(100)],
        'stock_name': [f'创业板股票{i+1:03d}' for i in range(100)]
    })

    return df

def create_kc50_data():
    """创建科创50模拟数据"""
    codes = []
    for i in range(50):
        # 科创板股票以688开头
        code_num = random.randint(688000, 688999)
        codes.append(f"{code_num}.SH")

    df = pd.DataFrame({
        'index_code': ['000688.SH'] * 50,
        'con_code': codes,
        'trade_date': ['20250930'] * 50,
        'weight': [random.uniform(0.5, 5.0) for _ in range(50)],
        'stock_name': [f'科创板股票{i+1:02d}' for i in range(50)]
    })

    return df

def main():
    """生成所有模拟数据"""
    data_dir = Path(__file__).parent / "A_stock_data"
    data_dir.mkdir(exist_ok=True)

    print("[INFO] Creating mock stock pool data...")

    # 创建上证180数据
    sse180_df = create_sse180_data()
    sse180_df.to_csv(data_dir / "sse_180_weight.csv", index=False, encoding='utf-8')
    print(f"[OK] Created SSE180 data: {len(sse180_df)} stocks")

    # 创建深证100数据
    sz100_df = create_sz100_data()
    sz100_df.to_csv(data_dir / "sz_100_weight.csv", index=False, encoding='utf-8')
    print(f"[OK] Created SZ100 data: {len(sz100_df)} stocks")

    # 创建创业板100数据
    cyb100_df = create_cyb100_data()
    cyb100_df.to_csv(data_dir / "cyb_100_weight.csv", index=False, encoding='utf-8')
    print(f"[OK] Created CYB100 data: {len(cyb100_df)} stocks")

    # 创建科创50数据
    kc50_df = create_kc50_data()
    kc50_df.to_csv(data_dir / "kc_50_weight.csv", index=False, encoding='utf-8')
    print(f"[OK] Created KC50 data: {len(kc50_df)} stocks")

    print(f"\n[INFO] Mock data creation completed!")
    print(f"Total stocks: {len(sse180_df) + len(sz100_df) + len(cyb100_df) + len(kc50_df)}")

if __name__ == "__main__":
    main()
