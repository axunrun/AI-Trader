"""
价格数据API路由
提供股票价格数据的查询接口
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from datetime import datetime, timedelta
import logging

from api.db.database import db_manager
from api.models.schemas import (
    StockPrice, StockPriceResponse, PriceQueryParams,
    ApiResponse, ErrorResponse
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/prices", tags=["prices"])

@router.get(
    "/{symbol}",
    response_model=StockPriceResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}}
)
async def get_stock_prices(
    symbol: str,
    start_date: Optional[str] = Query(None, description="开始日期 (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="结束日期 (YYYY-MM-DD)"),
    period: str = Query("daily", description="周期: daily/weekly/monthly"),
    limit: int = Query(1000, ge=1, le=10000, description="限制返回数量")
):
    """
    获取指定股票的价格数据

    - **symbol**: 股票代码，如 600519.SH
    - **start_date**: 开始日期，格式 YYYY-MM-DD
    - **end_date**: 结束日期，格式 YYYY-MM-DD
    - **period**: 数据周期 (daily/weekly/monthly)
    - **limit**: 返回记录数限制，最大10000
    """
    try:
        # 构建查询条件
        where_conditions = ["symbol = $1"]
        params = [symbol]
        param_count = 1

        if start_date:
            param_count += 1
            where_conditions.append(f"timestamp >= ${param_count}")
            params.append(start_date)

        if end_date:
            param_count += 1
            where_conditions.append(f"timestamp <= ${param_count}")
            params.append(f"{end_date} 23:59:59")

        # 根据周期选择表
        if period == "weekly":
            table_name = "weekly_stock_prices"
            # 使用周聚合数据
        elif period == "monthly":
            table_name = "monthly_stock_prices"
            # 使用月聚合数据
        else:
            table_name = "stock_prices"
            # 使用原始日线数据

        # 构建查询SQL
        query = f"""
            SELECT
                symbol, timestamp, open_price, high_price, low_price,
                close_price, volume, turnover, change_pct, meta_data
            FROM {table_name}
            WHERE {' AND '.join(where_conditions)}
            ORDER BY timestamp DESC
            LIMIT ${param_count + 1}
        """
        params.append(limit)

        # 执行查询
        records = await db_manager.fetch(query, *params)

        # 转换为响应模型
        prices = []
        for record in records:
            price = StockPrice(
                symbol=record['symbol'],
                timestamp=record['timestamp'],
                open_price=float(record['open_price']),
                high_price=float(record['high_price']),
                low_price=float(record['low_price']),
                close_price=float(record['close_price']),
                volume=int(record['volume']),
                turnover=float(record['turnover']) if record['turnover'] else 0,
                change_pct=float(record['change_pct']) if record['change_pct'] else 0,
                meta_data=record['meta_data']
            )
            prices.append(price)

        return StockPriceResponse(
            symbol=symbol,
            data=prices,
            count=len(prices)
        )

    except Exception as e:
        logger.error(f"获取股票价格数据失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"获取股票价格数据失败: {str(e)}"
        )

@router.get(
    "/symbols/list",
    response_model=ApiResponse,
    responses={500: {"model": ErrorResponse}}
)
async def get_available_symbols():
    """
    获取所有可用的股票代码列表
    """
    try:
        query = """
            SELECT DISTINCT symbol
            FROM stock_prices
            ORDER BY symbol
        """
        records = await db_manager.fetch(query)

        symbols = [record['symbol'] for record in records]

        return ApiResponse(
            success=True,
            message="获取股票代码列表成功",
            data={"symbols": symbols, "count": len(symbols)}
        )

    except Exception as e:
        logger.error(f"获取股票代码列表失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"获取股票代码列表失败: {str(e)}"
        )

@router.get(
    "/summary/{symbol}",
    response_model=ApiResponse,
    responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}}
)
async def get_stock_summary(symbol: str):
    """
    获取股票摘要信息（最新价格和统计）

    - **symbol**: 股票代码，如 600519.SH
    """
    try:
        query = """
            SELECT
                symbol,
                timestamp,
                close_price,
                change_pct,
                volume,
                high_price - low_price as price_range,
                (high_price - low_price) / low_price * 100 as volatility_pct
            FROM stock_prices
            WHERE symbol = $1
            ORDER BY timestamp DESC
            LIMIT 1
        """
        record = await db_manager.fetchrow(query, symbol)

        if not record:
            raise HTTPException(
                status_code=404,
                detail=f"未找到股票 {symbol} 的数据"
            )

        # 获取30日均价
        avg_query = """
            SELECT AVG(close_price) as avg_price_30d
            FROM stock_prices
            WHERE symbol = $1
            AND timestamp >= NOW() - INTERVAL '30 days'
        """
        avg_record = await db_manager.fetchrow(avg_query, symbol)

        summary = {
            "symbol": record['symbol'],
            "latest_price": float(record['close_price']),
            "change_pct": float(record['change_pct']) if record['change_pct'] else 0,
            "volume": int(record['volume']),
            "price_range": float(record['price_range']) if record['price_range'] else 0,
            "volatility_pct": float(record['volatility_pct']) if record['volatility_pct'] else 0,
            "avg_price_30d": float(avg_record['avg_price_30d']) if avg_record['avg_price_30d'] else 0,
            "last_updated": record['timestamp'].isoformat()
        }

        return ApiResponse(
            success=True,
            message="获取股票摘要成功",
            data=summary
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取股票摘要失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"获取股票摘要失败: {str(e)}"
        )

@router.get(
    "/market/summary",
    response_model=ApiResponse,
    responses={500: {"model": ErrorResponse}}
)
async def get_market_summary():
    """
    获取市场整体摘要信息
    """
    try:
        query = """
            SELECT
                COUNT(DISTINCT symbol) as total_symbols,
                COUNT(*) as total_records,
                MAX(timestamp) as last_update,
                AVG(change_pct) as avg_change_pct
            FROM stock_prices
            WHERE timestamp >= NOW() - INTERVAL '7 days'
        """
        record = await db_manager.fetchrow(query)

        summary = {
            "total_symbols": int(record['total_symbols']) if record['total_symbols'] else 0,
            "total_records": int(record['total_records']) if record['total_records'] else 0,
            "last_update": record['last_update'].isoformat() if record['last_update'] else None,
            "avg_change_pct": float(record['avg_change_pct']) if record['avg_change_pct'] else 0,
            "market_status": "open" if datetime.now().weekday() < 5 else "closed"
        }

        return ApiResponse(
            success=True,
            message="获取市场摘要成功",
            data=summary
        )

    except Exception as e:
        logger.error(f"获取市场摘要失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"获取市场摘要失败: {str(e)}"
        )
