"""
API数据模型定义
使用Pydantic进行数据验证和序列化
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

# 股票价格相关模型

class StockPriceBase(BaseModel):
    """股票价格基础模型"""
    symbol: str = Field(..., description="股票代码")
    timestamp: datetime = Field(..., description="时间戳")
    open_price: float = Field(..., description="开盘价")
    high_price: float = Field(..., description="最高价")
    low_price: float = Field(..., description="最低价")
    close_price: float = Field(..., description="收盘价")
    volume: int = Field(default=0, description="成交量")
    turnover: float = Field(default=0, description="成交额")
    change_pct: float = Field(default=0, description="涨跌幅(%)")

class StockPrice(StockPriceBase):
    """股票价格模型"""
    id: Optional[int] = None
    meta_data: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True

class StockPriceResponse(BaseModel):
    """股票价格响应模型"""
    symbol: str
    data: List[StockPrice]
    count: int

# 持仓相关模型

class PositionBase(BaseModel):
    """持仓基础模型"""
    agent_name: str = Field(..., description="代理名称")
    trade_date: str = Field(..., description="交易日期")
    action: str = Field(..., description="交易动作")
    symbol: Optional[str] = Field(None, description="股票代码")
    amount: int = Field(default=0, description="数量")
    price: float = Field(default=0, description="价格")
    cash: float = Field(..., description="现金")
    total_value: float = Field(..., description="总价值")
    positions: Dict[str, Any] = Field(..., description="持仓信息")
    reasoning: Optional[str] = Field(None, description="交易理由")

class Position(PositionBase):
    """持仓模型"""
    id: Optional[int] = None
    trade_time: Optional[datetime] = None
    meta_data: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True

class PositionResponse(BaseModel):
    """持仓响应模型"""
    agent_name: str
    data: List[Position]
    count: int

# 交易日志相关模型

class TradeLogBase(BaseModel):
    """交易日志基础模型"""
    agent_name: str = Field(..., description="代理名称")
    log_timestamp: datetime = Field(..., description="日志时间戳")
    log_type: str = Field(..., description="日志类型")
    summary: Optional[str] = Field(None, description="摘要")
    content: Dict[str, Any] = Field(..., description="日志内容")
    tokens_used: int = Field(default=0, description="使用Token数")
    processing_time_ms: int = Field(default=0, description="处理时间(毫秒)")

class TradeLog(TradeLogBase):
    """交易日志模型"""
    id: Optional[int] = None
    log_date: Optional[str] = None

    class Config:
        from_attributes = True

class TradeLogResponse(BaseModel):
    """交易日志响应模型"""
    agent_name: str
    data: List[TradeLog]
    count: int

# 指数相关模型

class IndexPriceBase(BaseModel):
    """指数价格基础模型"""
    index_code: str = Field(..., description="指数代码")
    timestamp: datetime = Field(..., description="时间戳")
    open_price: Optional[float] = Field(None, description="开盘价")
    high_price: Optional[float] = Field(None, description="最高价")
    low_price: Optional[float] = Field(None, description="最低价")
    close_price: float = Field(..., description="收盘价")
    volume: int = Field(default=0, description="成交量")
    change_pct: float = Field(default=0, description="涨跌幅(%)")

class IndexPrice(IndexPriceBase):
    """指数价格模型"""
    id: Optional[int] = None

    class Config:
        from_attributes = True

class IndexPriceResponse(BaseModel):
    """指数价格响应模型"""
    index_code: str
    data: List[IndexPrice]
    count: int

# 性能统计模型

class AgentPerformance(BaseModel):
    """代理性能模型"""
    agent_name: str = Field(..., description="代理名称")
    total_trades: int = Field(..., description="总交易次数")
    net_positions: int = Field(..., description="净持仓")
    start_date: str = Field(..., description="开始日期")
    end_date: str = Field(..., description="结束日期")
    total_return_pct: float = Field(..., description="总收益率(%)")
    peak_value: float = Field(..., description="峰值")
    trough_value: float = Field(..., description("谷值"))
    max_drawdown_pct: float = Field(..., description="最大回撤(%)")

# 响应模型

class ApiResponse(BaseModel):
    """通用API响应模型"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="响应消息")
    data: Optional[Any] = Field(None, description="响应数据")
    timestamp: datetime = Field(default_factory=datetime.now, description="响应时间")

class ErrorResponse(BaseModel):
    """错误响应模型"""
    success: bool = Field(default=False, description="是否成功")
    error: str = Field(..., description="错误信息")
    details: Optional[str] = Field(None, description="错误详情")
    timestamp: datetime = Field(default_factory=datetime.now, description="响应时间")

# 查询参数模型

class PriceQueryParams(BaseModel):
    """价格查询参数"""
    symbol: Optional[str] = Field(None, description="股票代码")
    start_date: Optional[str] = Field(None, description="开始日期")
    end_date: Optional[str] = Field(None, description="结束日期")
    period: str = Field(default="daily", description="周期: daily/weekly/monthly")
    limit: int = Field(default=1000, description="限制返回数量")

class PositionQueryParams(BaseModel):
    """持仓查询参数"""
    agent: Optional[str] = Field(None, description="代理名称")
    start_date: Optional[str] = Field(None, description="开始日期")
    end_date: Optional[str] = Field(None, description="结束日期")
    limit: int = Field(default=1000, description="限制返回数量")

class LogQueryParams(BaseModel):
    """日志查询参数"""
    agent: Optional[str] = Field(None, description="代理名称")
    log_type: Optional[str] = Field(None, description="日志类型")
    start_date: Optional[str] = Field(None, description="开始日期")
    end_date: Optional[str] = Field(None, description="结束日期")
    limit: int = Field(default=1000, description="限制返回数量")

class IndexQueryParams(BaseModel):
    """指数查询参数"""
    index_code: Optional[str] = Field(None, description="指数代码")
    start_date: Optional[str] = Field(None, description="开始日期")
    end_date: Optional[str] = Field(None, description="结束日期")
    period: str = Field(default="daily", description="周期: daily/weekly/monthly")
    limit: int = Field(default=1000, description="限制返回数量")

# 统计数据模型

class StatisticsResponse(BaseModel):
    """统计数据响应模型"""
    total_agents: int = Field(..., description="总代理数")
    total_trades: int = Field(..., description="总交易次数")
    best_performer: str = Field(..., description="最佳代理")
    best_return: float = Field(..., description("最佳收益率")
    trading_period: str = Field(..., description="交易周期")
    last_updated: datetime = Field(..., description="最后更新时间")

# 认证相关模型

class LoginRequest(BaseModel):
    """登录请求模型"""
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")

class LoginResponse(BaseModel):
    """登录响应模型"""
    success: bool = Field(..., description="是否成功")
    token: str = Field(..., description="访问令牌")
    user: Dict[str, Any] = Field(..., description="用户信息")
    expires_in: int = Field(..., description="过期时间(秒)")
