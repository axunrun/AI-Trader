"""
指数数据API路由
提供A股指数数据的查询接口
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from datetime import datetime, timedelta
import logging

from api.db.database import db_manager
from api.models.schemas import (
    IndexPrice, IndexPriceResponse, IndexQueryParams,
    ApiResponse, ErrorResponse
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/indices", tags=["indices"])

@router.get(
    "/{index_code}",
    response_model=IndexPriceResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}}
)
async def get_index_prices(
    index_code: str,
    start_date: Optional[str] = Query(None, description="开始日期 (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="结束日期 (YYYY-MM-DD)"),
    period: str = Query("daily", description="周期: daily/weekly/monthly"),
    limit: int = Query(1000, ge=1, le=10000, description="限制返回数量")
):
    """
    获取指定指数的价格数据

    - **index_code**: 指数代码，如 000001.SH (上证指数)
    - **start_date**: 开始日期，格式 YYYY-MM-DD
    - **end_date**: 结束日期，格式 YYYY-MM-DD
    - **period**: 数据周期 (daily/weekly/monthly)
    - **limit**: 返回记录数限制，最大10000
    """
    try:
        # 构建查询条件
        where_conditions = ["index_code = $1"]
        params = [index_code]
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
            table_name = "weekly_index_prices"
        elif period == "monthly":
            table_name = "monthly_index_prices"
        else:
            table_name = "index_prices"

        # 构建查询SQL
        query = f"""
            SELECT
                index_code, timestamp, open_price, high_price, low_price,
                close_price, volume, change_pct
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
            price = IndexPrice(
                index_code=record['index_code'],
                timestamp=record['timestamp'],
                open_price=float(record['open_price']) if record['open_price'] else None,
                high_price=float(record['high_price']) if record['high_price'] else None,
                low_price=float(record['low_price']) if record['low_price'] else None,
                close_price=float(record['close_price']),
                volume=int(record['volume']) if record['volume'] else 0,
                change_pct=float(record['change_pct']) if record['change_pct'] else 0
            )
            prices.append(price)

        return IndexPriceResponse(
            index_code=index_code,
            data=prices,
            count=len(prices)
        )

    except Exception as e:
        logger.error(f"获取指数价格数据失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"获取指数价格数据失败: {str(e)}"
        )

@router.get(
    "/list/available",
    response_model=ApiResponse,
    responses={500: {"model": ErrorResponse}}
)
async def get_available_indices():
    """
    获取所有可用的指数列表
    """
    try:
        query = """
            SELECT index_code, index_name, market, description
            FROM benchmark_indices
            WHERE is_active = true
            ORDER BY market, index_code
        """
        records = await db_manager.fetch(query)

        indices = []
        for record in records:
            index = {
                "code": record['index_code'],
                "name": record['index_name'],
                "market": record['market'],
                "description": record['description']
            }
            indices.append(index)

        return ApiResponse(
            success=True,
            message="获取指数列表成功",
            data={"indices": indices, "count": len(indices)}
        )

    except Exception as e:
        logger.error(f"获取指数列表失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"获取指数列表失败: {str(e)}"
        )

@router.get(
    "/summary/{index_code}",
    response_model=ApiResponse,
    responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}}
)
async def get_index_summary(index_code: str):
    """
    获取指数摘要信息（最新价格和统计）

    - **index_code**: 指数代码，如 000001.SH
    """
    try:
        query = """
            SELECT
                index_code,
                timestamp,
                close_price,
                change_pct,
                volume,
                high_price - low_price as price_range,
                (high_price - low_price) / low_price * 100 as volatility_pct
            FROM index_prices
            WHERE index_code = $1
            ORDER BY timestamp DESC
            LIMIT 1
        """
        record = await db_manager.fetchrow(query, index_code)

        if not record:
            raise HTTPException(
                status_code=404,
                detail=f"未找到指数 {index_code} 的数据"
            )

        # 获取30日均价
        avg_query = """
            SELECT AVG(close_price) as avg_price_30d
            FROM index_prices
            WHERE index_code = $1
            AND timestamp >= NOW() - INTERVAL '30 days'
        """
        avg_record = await db_manager.fetchrow(avg_query, index_code)

        summary = {
            "index_code": record['index_code'],
            "latest_price": float(record['close_price']),
            "change_pct": float(record['change_pct']) if record['change_pct'] else 0,
            "volume": int(record['volume']) if record['volume'] else 0,
            "price_range": float(record['price_range']) if record['price_range'] else 0,
            "volatility_pct": float(record['volatility_pct']) if record['volatility_pct'] else 0,
            "avg_price_30d": float(avg_record['avg_price_30d']) if avg_record['avg_price_30d'] else 0,
            "last_updated": record['timestamp'].isoformat()
        }

        return ApiResponse(
            success=True,
            message="获取指数摘要成功",
            data=summary
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取指数摘要失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"获取指数摘要失败: {str(e)}"
        )

@router.get(
    "/realtime/all",
    response_model=ApiResponse,
    responses={500: {"model": ErrorResponse}}
)
async def get_realtime_indices():
    """
    获取所有指数的实时数据（基于最新数据）
    """
    try:
        query = """
            SELECT DISTINCT ON (index_code)
                index_code,
                timestamp,
                close_price,
                change_pct,
                volume
            FROM index_prices
            ORDER BY index_code, timestamp DESC
        """
        records = await db_manager.fetch(query)

        indices = []
        for record in records:
            index = {
                "code": record['index_code'],
                "price": float(record['close_price']),
                "change_pct": float(record['change_pct']) if record['change_pct'] else 0,
                "volume": int(record['volume']) if record['volume'] else 0,
                "timestamp": record['timestamp'].isoformat()
            }
            indices.append(index)

        # 按市场分组
        indices_grouped = {}
        for index in indices:
            # 这里可以根据指数代码前缀进行分组
            if index['code'].startswith('000'):
                market = '上证'
            elif index['code'].startswith('399'):
                market = '深证'
            else:
                market = '其他'

            if market not in indices_grouped:
                indices_grouped[market] = []
            indices_grouped[market].append(index)

        return ApiResponse(
            success=True,
            message="获取实时指数成功",
            data={
                "indices": indices_grouped,
                "total_count": len(indices),
                "update_time": datetime.now().isoformat()
            }
        )

    except Exception as e:
        logger.error(f"获取实时指数失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"获取实时指数失败: {str(e)}"
        )

@router.get(
    "/comparison",
    response_model=ApiResponse,
    responses={500: {"model": ErrorResponse}}
)
async def compare_indices(
    indices: str = Query(..., description="指数代码列表，用逗号分隔"),
    period: str = Query("daily", description="周期: daily/weekly/monthly")
):
    """
    对比多个指数的表现

    - **indices**: 指数代码列表，如 "000001.SH,000300.SH,399001.SZ"
    - **period**: 数据周期
    """
    try:
        index_list = [idx.strip() for idx in indices.split(',')]

        if len(index_list) > 10:
            raise HTTPException(
                status_code=400,
                detail="最多支持10个指数对比"
            )

        # 构建查询条件
        placeholders = ','.join([f"${i+1}" for i in range(len(index_list))])
        where_clause = f"index_code IN ({placeholders})"

        # 根据周期选择表
        if period == "weekly":
            table_name = "weekly_index_prices"
        elif period == "monthly":
            table_name = "monthly_index_prices"
        else:
            table_name = "index_prices"

        query = f"""
            SELECT
                index_code,
                timestamp,
                close_price,
                change_pct
            FROM {table_name}
            WHERE {where_clause}
            AND timestamp >= NOW() - INTERVAL '30 days'
            ORDER BY index_code, timestamp DESC
        """

        records = await db_manager.fetch(query, *index_list)

        # 按指数分组数据
        comparison_data = {}
        for record in records:
            code = record['index_code']
            if code not in comparison_data:
                comparison_data[code] = []

            comparison_data[code].append({
                "timestamp": record['timestamp'].isoformat(),
                "price": float(record['close_price']),
                "change_pct": float(record['change_pct']) if record['change_pct'] else 0
            })

        return ApiResponse(
            success=True,
            message="获取指数对比成功",
            data={
                "comparison": comparison_data,
                "period": period,
                "count": len(comparison_data)
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取指数对比失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"获取指数对比失败: {str(e)}"
        )
