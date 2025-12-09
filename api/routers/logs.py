"""
交易日志API路由
提供AI代理推理日志的查询接口
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from datetime import datetime, timedelta
import logging

from api.db.database import db_manager
from api.models.schemas import (
    TradeLog, TradeLogResponse, LogQueryParams,
    ApiResponse, ErrorResponse
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/logs", tags=["logs"])

@router.get(
    "/{agent}",
    response_model=TradeLogResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}}
)
async def get_agent_logs(
    agent: str,
    log_type: Optional[str] = Query(None, description="日志类型"),
    start_date: Optional[str] = Query(None, description="开始日期 (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="结束日期 (YYYY-MM-DD)"),
    limit: int = Query(1000, ge=1, le=10000, description="限制返回数量")
):
    """
    获取指定代理的推理日志

    - **agent**: 代理名称，如 deepseek-chat-v3.1
    - **log_type**: 日志类型 (market_analysis/decision/trade/research)
    - **start_date**: 开始日期，格式 YYYY-MM-DD
    - **end_date**: 结束日期，格式 YYYY-MM-DD
    - **limit**: 返回记录数限制，最大10000
    """
    try:
        # 构建查询条件
        where_conditions = ["agent_name = $1"]
        params = [agent]
        param_count = 1

        if log_type:
            param_count += 1
            where_conditions.append(f"log_type = ${param_count}")
            params.append(log_type)

        if start_date:
            param_count += 1
            where_conditions.append(f"log_date >= ${param_count}")
            params.append(start_date)

        if end_date:
            param_count += 1
            where_conditions.append(f"log_date <= ${param_count}")
            params.append(end_date)

        # 构建查询SQL
        query = f"""
            SELECT
                id, agent_name, log_timestamp, log_date, log_type,
                summary, content, tokens_used, processing_time_ms
            FROM trade_logs
            WHERE {' AND '.join(where_conditions)}
            ORDER BY log_timestamp DESC
            LIMIT ${param_count + 1}
        """
        params.append(limit)

        # 执行查询
        records = await db_manager.fetch(query, *params)

        # 转换为响应模型
        logs = []
        for record in records:
            log = TradeLog(
                id=record['id'],
                agent_name=record['agent_name'],
                log_timestamp=record['log_timestamp'],
                log_date=str(record['log_date']) if record['log_date'] else None,
                log_type=record['log_type'],
                summary=record['summary'],
                content=record['content'],
                tokens_used=int(record['tokens_used']) if record['tokens_used'] else 0,
                processing_time_ms=int(record['processing_time_ms']) if record['processing_time_ms'] else 0
            )
            logs.append(log)

        return TradeLogResponse(
            agent_name=agent,
            data=logs,
            count=len(logs)
        )

    except Exception as e:
        logger.error(f"获取日志数据失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"获取日志数据失败: {str(e)}"
        )

@router.get(
    "/types/list",
    response_model=ApiResponse,
    responses={500: {"model": ErrorResponse}}
)
async def get_log_types():
    """
    获取所有可用的日志类型
    """
    try:
        query = """
            SELECT DISTINCT log_type
            FROM trade_logs
            ORDER BY log_type
        """
        records = await db_manager.fetch(query)

        log_types = [record['log_type'] for record in records]

        return ApiResponse(
            success=True,
            message="获取日志类型成功",
            data={"log_types": log_types, "count": len(log_types)}
        )

    except Exception as e:
        logger.error(f"获取日志类型失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"获取日志类型失败: {str(e)}"
        )

@router.get(
    "/summary/{agent}",
    response_model=ApiResponse,
    responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}}
)
async def get_agent_log_summary(agent: str):
    """
    获取代理日志摘要统计

    - **agent**: 代理名称
    """
    try:
        query = """
            SELECT
                COUNT(*) as total_logs,
                COUNT(DISTINCT log_date) as trading_days,
                SUM(tokens_used) as total_tokens,
                AVG(processing_time_ms) as avg_processing_time,
                COUNT(CASE WHEN log_type = 'market_analysis' THEN 1 END) as market_analysis_count,
                COUNT(CASE WHEN log_type = 'decision' THEN 1 END) as decision_count,
                COUNT(CASE WHEN log_type = 'trade' THEN 1 END) as trade_count,
                COUNT(CASE WHEN log_type = 'research' THEN 1 END) as research_count
            FROM trade_logs
            WHERE agent_name = $1
        """
        record = await db_manager.fetchrow(query, agent)

        if not record:
            raise HTTPException(
                status_code=404,
                detail=f"未找到代理 {agent} 的日志数据"
            )

        summary = {
            "agent_name": agent,
            "total_logs": int(record['total_logs']) if record['total_logs'] else 0,
            "trading_days": int(record['trading_days']) if record['trading_days'] else 0,
            "total_tokens": int(record['total_tokens']) if record['total_tokens'] else 0,
            "avg_processing_time": float(record['avg_processing_time']) if record['avg_processing_time'] else 0,
            "log_type_breakdown": {
                "market_analysis": int(record['market_analysis_count']) if record['market_analysis_count'] else 0,
                "decision": int(record['decision_count']) if record['decision_count'] else 0,
                "trade": int(record['trade_count']) if record['trade_count'] else 0,
                "research": int(record['research_count']) if record['research_count'] else 0
            }
        }

        return ApiResponse(
            success=True,
            message="获取日志摘要成功",
            data=summary
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取日志摘要失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"获取日志摘要失败: {str(e)}"
        )

@router.get(
    "/recent/{agent}",
    response_model=ApiResponse,
    responses={500: {"model": ErrorResponse}}
)
async def get_recent_logs(
    agent: str,
    log_type: Optional[str] = Query(None, description="日志类型"),
    limit: int = Query(50, ge=1, le=200, description="限制返回数量")
):
    """
    获取代理最近的推理日志

    - **agent**: 代理名称
    - **log_type**: 日志类型筛选
    - **limit**: 返回记录数限制，最大200
    """
    try:
        where_conditions = ["agent_name = $1"]
        params = [agent]
        param_count = 1

        if log_type:
            param_count += 1
            where_conditions.append(f"log_type = ${param_count}")
            params.append(log_type)

        query = f"""
            SELECT
                log_timestamp, log_type, summary, content,
                tokens_used, processing_time_ms
            FROM trade_logs
            WHERE {' AND '.join(where_conditions)}
            ORDER BY log_timestamp DESC
            LIMIT ${param_count + 1}
        """
        params.append(limit)

        records = await db_manager.fetch(query, *params)

        logs = []
        for record in records:
            log = {
                "log_timestamp": record['log_timestamp'].isoformat(),
                "log_type": record['log_type'],
                "summary": record['summary'],
                "content": record['content'],
                "tokens_used": int(record['tokens_used']) if record['tokens_used'] else 0,
                "processing_time_ms": int(record['processing_time_ms']) if record['processing_time_ms'] else 0
            }
            logs.append(log)

        return ApiResponse(
            success=True,
            message="获取最近日志成功",
            data={"logs": logs, "count": len(logs)}
        )

    except Exception as e:
        logger.error(f"获取最近日志失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"获取最近日志失败: {str(e)}"
        )

@router.get(
    "/statistics",
    response_model=ApiResponse,
    responses={500: {"model": ErrorResponse}}
)
async def get_logs_statistics():
    """
    获取所有日志的全局统计
    """
    try:
        query = """
            SELECT
                COUNT(DISTINCT agent_name) as total_agents,
                COUNT(*) as total_logs,
                COUNT(DISTINCT log_date) as total_trading_days,
                SUM(tokens_used) as total_tokens_used,
                AVG(processing_time_ms) as avg_processing_time,
                MAX(log_timestamp) as last_log_time
            FROM trade_logs
        """
        record = await db_manager.fetchrow(query)

        # 获取各类型日志分布
        type_query = """
            SELECT log_type, COUNT(*) as count
            FROM trade_logs
            GROUP BY log_type
            ORDER BY count DESC
        """
        type_records = await db_manager.fetch(type_query)

        statistics = {
            "total_agents": int(record['total_agents']) if record['total_agents'] else 0,
            "total_logs": int(record['total_logs']) if record['total_logs'] else 0,
            "total_trading_days": int(record['total_trading_days']) if record['total_trading_days'] else 0,
            "total_tokens_used": int(record['total_tokens_used']) if record['total_tokens_used'] else 0,
            "avg_processing_time": float(record['avg_processing_time']) if record['avg_processing_time'] else 0,
            "last_log_time": record['last_log_time'].isoformat() if record['last_log_time'] else None,
            "log_type_distribution": {
                rec['log_type']: int(rec['count']) for rec in type_records
            }
        }

        return ApiResponse(
            success=True,
            message="获取日志统计成功",
            data=statistics
        )

    except Exception as e:
        logger.error(f"获取日志统计失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"获取日志统计失败: {str(e)}"
        )
