"""
持仓数据API路由
提供代理持仓历史数据的查询接口
 import APIRouter,"""

from fastapi HTTPException, Query
from typing import Optional, List
from datetime import datetime, timedelta
import logging

from api.db.database import db_manager
from api.models.schemas import (
    Position, PositionResponse, PositionQueryParams,
    AgentPerformance, ApiResponse, ErrorResponse
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/positions", tags=["positions"])

@router.get(
    "/{agent}",
    response_model=PositionResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}}
)
async def get_agent_positions(
    agent: str,
    start_date: Optional[str] = Query(None, description="开始日期 (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="结束日期 (YYYY-MM-DD)"),
    limit: int = Query(1000, ge=1, le=10000, description="限制返回数量")
):
    """
    获取指定代理的持仓历史

    - **agent**: 代理名称，如 deepseek-chat-v3.1
    - **start_date**: 开始日期，格式 YYYY-MM-DD
    - **end_date**: 结束日期，格式 YYYY-MM-DD
    - **limit**: 返回记录数限制，最大10000
    """
    try:
        # 构建查询条件
        where_conditions = ["agent_name = $1"]
        params = [agent]
        param_count = 1

        if start_date:
            param_count += 1
            where_conditions.append(f"trade_date >= ${param_count}")
            params.append(start_date)

        if end_date:
            param_count += 1
            where_conditions.append(f"trade_date <= ${param_count}")
            params.append(end_date)

        # 构建查询SQL
        query = f"""
            SELECT
                id, agent_name, trade_date, trade_time, action, symbol,
                amount, price, cash, total_value, positions, reasoning, meta_data
            FROM position_history
            WHERE {' AND '.join(where_conditions)}
            ORDER BY trade_date DESC, trade_time DESC
            LIMIT ${param_count + 1}
        """
        params.append(limit)

        # 执行查询
        records = await db_manager.fetch(query, *params)

        # 转换为响应模型
        positions = []
        for record in records:
            position = Position(
                id=record['id'],
                agent_name=record['agent_name'],
                trade_date=str(record['trade_date']),
                trade_time=record['trade_time'],
                action=record['action'],
                symbol=record['symbol'],
                amount=int(record['amount']) if record['amount'] else 0,
                price=float(record['price']) if record['price'] else 0,
                cash=float(record['cash']) if record['cash'] else 0,
                total_value=float(record['total_value']) if record['total_value'] else 0,
                positions=record['positions'],
                reasoning=record['reasoning'],
                meta_data=record['meta_data']
            )
            positions.append(position)

        return PositionResponse(
            agent_name=agent,
            data=positions,
            count=len(positions)
        )

    except Exception as e:
        logger.error(f"获取持仓数据失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"获取持仓数据失败: {str(e)}"
        )

@router.get(
    "/agents/list",
    response_model=ApiResponse,
    responses={500: {"model": ErrorResponse}}
)
async def get_available_agents():
    """
    获取所有可用的代理列表
    """
    try:
        query = """
            SELECT DISTINCT agent_name
            FROM position_history
            ORDER BY agent_name
        """
        records = await db_manager.fetch(query)

        agents = [record['agent_name'] for record in records]

        return ApiResponse(
            success=True,
            message="获取代理列表成功",
            data={"agents": agents, "count": len(agents)}
        )

    except Exception as e:
        logger.error(f"获取代理列表失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"获取代理列表失败: {str(e)}"
        )

@router.get(
    "/performance",
    response_model=ApiResponse,
    responses={500: {"model": ErrorResponse}}
)
async def get_agents_performance():
    """
    获取所有代理的性能统计
    """
    try:
        query = """
            SELECT
                agent_name,
                COUNT(*) as total_trades,
                SUM(CASE WHEN action = 'buy' THEN amount ELSE -amount END) as net_positions,
                MIN(trade_date) as start_date,
                MAX(trade_date) as end_date,
                (MAX(total_value) - MIN(total_value)) / MIN(total_value) * 100 as total_return_pct,
                MAX(total_value) as peak_value,
                MIN(total_value) as trough_value,
                (MIN(total_value) - MAX(total_value)) / MAX(total_value) * 100 as max_drawdown_pct
            FROM position_history
            GROUP BY agent_name
            ORDER BY total_return_pct DESC
        """
        records = await db_manager.fetch(query)

        performances = []
        for record in records:
            performance = AgentPerformance(
                agent_name=record['agent_name'],
                total_trades=int(record['total_trades']) if record['total_trades'] else 0,
                net_positions=int(record['net_positions']) if record['net_positions'] else 0,
                start_date=str(record['start_date']) if record['start_date'] else '',
                end_date=str(record['end_date']) if record['end_date'] else '',
                total_return_pct=float(record['total_return_pct']) if record['total_return_pct'] else 0,
                peak_value=float(record['peak_value']) if record['peak_value'] else 0,
                trough_value=float(record['trough_value']) if record['trough_value'] else 0,
                max_drawdown_pct=float(record['max_drawdown_pct']) if record['max_drawdown_pct'] else 0
            )
            performances.append(performance)

        return ApiResponse(
            success=True,
            message="获取代理性能统计成功",
            data={"performances": performances, "count": len(performances)}
        )

    except Exception as e:
        logger.error(f"获取代理性能统计失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"获取代理性能统计失败: {str(e)}"
        )

@router.get(
    "/current/{agent}",
    response_model=ApiResponse,
    responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}}
)
async def get_current_positions(agent: str):
    """
    获取代理当前持仓快照

    - **agent**: 代理名称
    """
    try:
        query = """
            SELECT DISTINCT ON (agent_name, symbol)
                agent_name,
                symbol,
                (positions->symbol->>'amount')::int as amount,
                (positions->symbol->>'avg_price')::numeric as avg_price,
                (positions->symbol->>'market_value')::numeric as market_value,
                cash,
                total_value,
                trade_date
            FROM position_history
            WHERE agent_name = $1
            AND (positions->symbol->>'amount')::int > 0
            ORDER BY agent_name, symbol, trade_date DESC
        """
        records = await db_manager.fetch(query, agent)

        if not records:
            return ApiResponse(
                success=True,
                message=f"代理 {agent} 当前无持仓",
                data={"positions": [], "cash": 0, "total_value": 0}
            )

        positions = []
        total_cash = 0
        total_value = 0

        for record in records:
            position = {
                "symbol": record['symbol'],
                "amount": int(record['amount']) if record['amount'] else 0,
                "avg_price": float(record['avg_price']) if record['avg_price'] else 0,
                "market_value": float(record['market_value']) if record['market_value'] else 0,
                "trade_date": str(record['trade_date'])
            }
            positions.append(position)

            total_cash = float(record['cash']) if record['cash'] else 0
            total_value = float(record['total_value']) if record['total_value'] else 0

        return ApiResponse(
            success=True,
            message="获取当前持仓成功",
            data={
                "agent_name": agent,
                "positions": positions,
                "cash": total_cash,
                "total_value": total_value,
                "position_count": len(positions)
            }
        )

    except Exception as e:
        logger.error(f"获取当前持仓失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"获取当前持仓失败: {str(e)}"
        )

@router.get(
    "/recent/{agent}",
    response_model=ApiResponse,
    responses={500: {"model": ErrorResponse}}
)
async def get_recent_trades(
    agent: str,
    limit: int = Query(20, ge=1, le=100, description="限制返回数量")
):
    """
    获取代理最近的交易记录

    - **agent**: 代理名称
    - **limit**: 返回记录数限制，最大100
    """
    try:
        query = """
            SELECT
                trade_date, trade_time, action, symbol,
                amount, price, total_value, reasoning
            FROM position_history
            WHERE agent_name = $1
            AND action != 'hold'
            ORDER BY trade_date DESC, trade_time DESC
            LIMIT $2
        """
        records = await db_manager.fetch(query, agent, limit)

        trades = []
        for record in records:
            trade = {
                "trade_date": str(record['trade_date']),
                "trade_time": record['trade_time'].isoformat() if record['trade_time'] else None,
                "action": record['action'],
                "symbol": record['symbol'],
                "amount": int(record['amount']) if record['amount'] else 0,
                "price": float(record['price']) if record['price'] else 0,
                "total_value": float(record['total_value']) if record['total_value'] else 0,
                "reasoning": record['reasoning']
            }
            trades.append(trade)

        return ApiResponse(
            success=True,
            message="获取最近交易成功",
            data={"trades": trades, "count": len(trades)}
        )

    except Exception as e:
        logger.error(f"获取最近交易失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"获取最近交易失败: {str(e)}"
        )
