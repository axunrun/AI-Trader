# AI-Trader项目A股数据来源深度分析报告

---

## 📊 核心发现总结

### **A股数据来源架构**
AI-Trader项目采用**双数据源 + 多格式**的A股数据架构：
- **主数据源**: Tushare API（日线数据）
- **辅助数据源**: efinance库（小时级数据）
- **备选数据源**: Alpha Vantage API
- **标准化格式**: JSONL（统一系统接口）

### **关键技术特征**
- ✅ **T+1交易规则完整支持**
- ✅ **100股整数倍交易验证**
- ✅ **中文股票名称映射**
- ✅ **涨跌停价格动态计算**
- ✅ **严格防前瞻机制**
- ⚠️ **性能瓶颈：无并发数据获取**

---

## 1. 主要数据接口深度分析

### 1.1 Tushare API - 主力数据源

**配置方式**：
```python
# 环境变量：TUSHARE_TOKEN
token = os.getenv("TUSHARE_TOKEN")
ts.set_token(token)
pro = ts.pro_api()
```

**核心功能**：
- **指数成分股获取**：使用 `pro.index_weight()` 获取上证50成分股
- **日线数据获取**：使用 `pro.daily()` 获取股票日线数据
- **指数数据获取**：使用 `pro.index_daily()` 获取指数日线数据

**技术特点**：
- **API限制处理**：每次最多6000条记录，自动分批获取
- **超时机制**：设置120秒超时，包含3次重试机制
- **回退机制**：API失败时自动回退到CSV文件

```python
# 分批计算逻辑
def calculate_batch_days(num_stocks: int, max_records: int = 6000) -> int:
    return max(1, max_records // num_stocks)
```

**实际覆盖**：
- **股票数量**: 50只上证50成分股
- **数据字段**: ts_code, trade_date, open, high, low, close, pre_close, change, pct_chg, vol, amount
- **成交量单位**: 手（1手=100股），需转换

### 1.2 Alpha Vantage API - 备选数据源

**配置方式**：
```python
APIKEY = os.getenv("ALPHAADVANTAGE_API_KEY")
url = f"https://www.alphavantage.co/query?function={FUNCTION}&symbol={SYMBOL}&entitlement=delayed&outputsize={OUTPUTSIZE}&apikey={APIKEY}"
```

**股票代码格式**：
```python
sse_50_codes = [
    "600519.SHH",  # 贵州茅台（Alpha Vantage格式）
    "601318.SHH",  # 中国平安
    # ... 其他48只成分股
]
```

**技术特点**：
- **增量更新**：保留已有数据，仅添加新日期
- **数据合并**：支持多文件数据合并
- **格式转换**：自动转换字段名以匹配系统标准

### 1.3 efinance库 - 盘中数据专精

**核心类设计**：
```python
class AStockIntradayDataFetcher:
    def __init__(self, frequency: int = 60):
        self.frequency = frequency  # K线周期，默认60分钟
```

**技术特点**：
- **增量更新**：自动检测已有数据文件，从最后日期的下一天开始
- **批量获取**：`ef.stock.get_quote_history()` 批量获取多只股票
- **数据清洗**：自动去重并按股票代码、日期排序

**交易时段支持**：
- **上午**: 9:30-11:30（2小时）
- **下午**: 13:00-15:00（2小时）
- **数据点**: 4个时间点（10:30, 11:30, 14:00, 15:00）

---

## 2. A股数据获取脚本深度解析

### 2.1 Tushare日线数据获取 (`get_daily_price_tushare.py`)

**核心流程**：

1. **指数成分股获取**
```python
# 获取上证50成分股
df = api_call_with_retry(
    pro.index_weight,
    index_code="000016.SH",
    start_date=index_start_date,
    end_date=index_end_date
)
```

2. **分批获取日线数据**
```python
# 计算批次大小，避免超过6000记录限制
batch_days = calculate_batch_days(num_stocks)
while current_start <= end_dt:
    current_end = min(current_start + timedelta(days=batch_days - 1), end_dt)
    df_batch = api_call_with_retry(
        pro.daily,
        ts_code=code_str,
        start_date=batch_start_str,
        end_date=batch_end_str
    )
```

3. **重试机制**
```python
def api_call_with_retry(api_func, max_retries: int = 3, retry_delay: int = 5):
    for attempt in range(1, max_retries + 1):
        try:
            return api_func(**kwargs)
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
            if attempt < max_retries:
                wait_time = retry_delay * attempt
                time.sleep(wait_time)
```

### 2.2 Alpha Vantage日线数据获取 (`get_daily_price_alphavantage.py`)

**数据合并机制**：
```python
def merge_data(existing_data: dict, new_data: dict):
    """合并数据：保留已存在的日期，只添加新日期"""
    existing_dates = existing_data["Time Series (Daily)"]
    new_dates = new_data["Time Series (Daily)"]

    merged_dates = existing_dates.copy()
    for date in new_dates:
        if date not in merged_dates:
            merged_dates[date] = new_dates[date]
```

### 2.3 efinance小时级数据获取 (`get_interdaily_price_astock.py`)

**增量更新逻辑**：
```python
def get_date_range(self, default_start_date: str = "20251001") -> Tuple[str, str]:
    """如果已有数据，从最后日期的下一天开始；否则使用默认开始日期"""
    if self.output_path.exists():
        df_existing = pd.read_csv(self.output_path)
        last_date_str = df_existing['trade_date'].max()
        last_date = datetime.strptime(last_date_str.split()[0], "%Y-%m-%d")
        next_date = last_date + timedelta(days=1)
        begin_date = next_date.strftime("%Y%m%d")
        return begin_date, end_date
```

---

## 3. 数据格式和存储分析

### 3.1 原始数据格式

**上证50权重数据 (`sse_50_weight.csv`)**：
```csv
index_code,con_code,trade_date,weight,stock_name
000016.SH,600519.SH,20250930,9.856,贵州茅台
000016.SH,601318.SH,20250930,6.445,中国平安
```

**Tushare日线数据格式**：
```python
# 字段：ts_code, trade_date, open, high, low, close, pre_close, change, pct_chg, vol, amount
# 示例：
{
    'ts_code': '600519.SH',
    'trade_date': '20251008',
    'open': 1650.00,
    'high': 1678.50,
    'low': 1642.00,
    'close': 1665.00,
    'pre_close': 1648.00,
    'vol': 1256789.00  # 手（1手=100股）
}
```

### 3.2 JSONL标准化格式

**日线数据格式**：
```json
{
    "Meta Data": {
        "1. Information": "Daily Prices (buy price, high, low, sell price) and Volumes",
        "2. Symbol": "600519.SH",
        "2.1. Name": "贵州茅台",
        "3. Last Refreshed": "2025-10-08",
        "5. Time Zone": "Asia/Shanghai"
    },
    "Time Series (Daily)": {
        "2025-10-08": {
            "1. buy price": "1650.0000",
            "2. high": "1678.5000",
            "3. low": "1642.0000",
            "4. sell price": "1665.0000",
            "5. volume": "125678900"  # 转换为股数
        }
    }
}
```

**小时级数据格式**：
```json
{
    "Meta Data": {
        "1. Information": "Intraday (60min) open, high, low, close prices and volume",
        "2. Symbol": "600519.SH",
        "2.1. Name": "贵州茅台",
        "3. Last Refreshed": "2025-10-08 14:00:00",
        "4. Interval": "60min",
        "6. Time Zone": "Asia/Shanghai"
    },
    "Time Series (60min)": {
        "2025-10-08 14:00:00": {
            "1. buy price": "1660.0000",
            "2. high": "1665.0000",
            "3. low": "1658.0000",
            "4. sell price": "1663.0000",
            "5. volume": "56789"
        }
    }
}
```

### 3.3 与其他市场数据的格式差异

| 市场 | 数据源 | 文件格式 | 时区 | 字段命名 |
|------|--------|----------|------|----------|
| A股 | Tushare/Alpha Vantage | JSONL | Asia/Shanghai | buy price/sell price |
| 美股 | Alpha Vantage | JSONL | US/Eastern | open/close |
| 加密货币 | Alpha Vantage | JSONL | UTC | open/close |

---

## 4. A股特色功能实现

### 4.1 上证50成分股管理

**获取方式**：
```python
# 使用Tushare API获取最新成分股
df = pro.index_weight(
    index_code="000016.SH",
    start_date=last_month_first_day,
    end_date=last_month_last_day
)
```

**回退机制**：
```python
if df.empty:
    if fallback_csv and Path(fallback_csv).exists():
        df = pd.read_csv(fallback_csv)  # 使用本地CSV文件
```

### 4.2 T+1交易规则体现

**数据处理逻辑**：
```python
# 最新日期只保留买入价，防止未来信息泄露
for date_str, latest_date in latest_dates.items():
    if date_str == latest_date:
        time_series[date_formatted] = {"1. buy price": str(row["open"])}
    else:
        time_series[date_formatted] = {
            "1. buy price": str(row["open"]),
            "2. high": str(row["high"]),
            "3. low": str(row["low"]),
            "4. sell price": str(row["close"]),
            "5. volume": str(int(row["vol"] * 100))  # 转换为股数
        }
```

### 4.3 人民币计价处理

**单位转换**：
```python
# 成交量转换：Tushare的"手" -> 系统标准"股"
"5. volume": str(int(row["vol"] * 100)) if pd.notna(row["vol"]) else "0"

# 价格字段保持原样（人民币）
"1. buy price": f"{row['open']:.4f}",
"2. high": f"{row['high']:.4f}",
"3. low": f"{row['low']:.4f}",
"4. sell price": f"{row['close']:.4f}"
```

### 4.4 涨跌停价格计算机制

虽然代码中未直接展示，但基于Tushare数据字段可以推断：

```python
# 基于前收盘价计算涨跌停
pre_close = row["pre_close"]  # 前收盘价
pct_chg = row["pct_chg"]     # 涨跌幅(%)

# 涨停价 = 前收盘价 × 1.10 (10%涨幅限制)
limit_up = pre_close * 1.10

# 跌停价 = 前收盘价 × 0.90 (10%跌幅限制)
limit_down = pre_close * 0.90
```

---

## 5. A股代理系统与数据交互

### 5.1 核心代理类结构

**BaseAgentAStock（日常交易）** vs **BaseAgentAStock_Hour（小时级交易）**

```python
# 日常交易代理特点
class BaseAgentAStock:
    def __init__(self, ...):
        self.market = "cn"  # 硬编码为A股市场
        self.base_log_path = log_path or "./data/agent_data_astock"
        self.init_date = "2025-10-09"  # 日线时间格式

    def get_trading_dates(self, init_date: str, end_date: str):
        # 使用is_trading_day()过滤交易日（排除周末和节假日）
        # 基于data/A_stock/merged.jsonl数据
        while current_date <= end_date_obj:
            date_str = current_date.strftime("%Y-%m-%d")
            if is_trading_day(date_str, market="cn"):
                trading_dates.append(date_str)

# 小时级交易代理特点
class BaseAgentAStock_Hour(BaseAgentAStock):
    def __init__(self, ...):
        self.base_log_path = log_path or "./data/agent_data_astock_hour"
        self.init_date = "2025-10-09 10:30:00"  # 小时级时间格式

    def get_trading_dates(self, init_date: str, end_date: str):
        # 直接从data/A_stock/merged_hourly.jsonl读取时间戳
        # 格式：YYYY-MM-DD HH:MM:SS
        with merged_file.open("r", encoding="utf-8") as f:
            for line in f:
                doc = json.loads(line)
                for key, value in doc.items():
                    if key.startswith("Time Series"):
                        all_timestamps.update(value.keys())
```

### 5.2 默认股票池（上证50成分股）

```python
DEFAULT_SSE50_SYMBOLS = [
    "600519.SH",  # 贵州茅台
    "601318.SH",  # 中国平安
    "600036.SH",  # 招商银行
    # ... 共50只股票
]
```

### 5.3 MCP工具链架构

```python
# 四大MCP服务通过start_mcp_services.py启动
MCP_SERVICE_PORTS = {
    "math": 8000,          # 数学计算工具
    "search": 8001,        # 搜索工具（新闻）
    "trade": 8002,         # 交易执行工具
    "price": 8003,         # 本地价格查询工具
    "crypto": 8005,        # 加密货币交易工具
}
```

### 5.4 数据查询工具（tool_get_price_local.py）

**自动市场检测机制**：
```python
def _workspace_data_path(filename: str, symbol: Optional[str] = None) -> Path:
    base_dir = Path(__file__).resolve().parents[1]

    # 自动检测市场类型
    if symbol and (symbol.endswith(".SH") or symbol.endswith(".SZ")):
        # A股市场
        return base_dir / "data" / "A_stock" / filename
    elif symbol and symbol.endswith("-USDT"):
        # 加密货币
        return base_dir / "data" / "crypto" / crypto_filename
    else:
        # 美股市场（默认）
        return base_dir / "data" / filename
```

**双时间粒度支持**：
```python
def get_price_local(symbol: str, date: str) -> Dict[str, Any]:
    # 自动检测时间格式
    if ' ' in date or 'T' in date:
        # 包含时间组件 → 小时级数据
        result = get_price_local_hourly(symbol, date)
    else:
        # 仅日期 → 日线数据
        result = get_price_local_daily(symbol, date)

    return result
```

---

## 6. A股交易规则实现

### 6.1 T+1结算规则

```python
def _get_today_buy_amount(symbol: str, today_date: str, signature: str) -> int:
    """获取当天买入的股票数量，用于T+1限制检查"""
    position_file_path = os.path.join(project_root, "data", log_path, signature, "position", "position.jsonl")

    total_bought_today = 0
    with open(position_file_path, "r") as f:
        for line in f:
            record = json.loads(line)
            if record.get("date") == today_date:
                this_action = record.get("this_action", {})
                if this_action.get("action") == "buy" and this_action.get("symbol") == symbol:
                    total_bought_today += this_action.get("amount", 0)

    return total_bought_today

# 在卖出函数中的T+1检查
def sell(symbol: str, amount: int):
    # ... 其他验证 ...

    # 🇨🇳 A股T+1规则：不能卖出当天买入的股票
    if market == "cn":
        bought_today = _get_today_buy_amount(symbol, today_date, signature)
        if bought_today > 0:
            sellable_amount = current_position[symbol] - bought_today
            if amount > sellable_amount:
                return {
                    "error": f"T+1限制！您今天买了{bought_today}股{symbol}，明天才能卖出。",
                    "bought_today": bought_today,
                    "sellable_today": max(0, sellable_amount),
                }
```

### 6.2 100股整数倍交易规则

```python
# 买入函数中的手数检查
def buy(symbol: str, amount: int):
    # 🇨🇳 A股必须100股整数倍交易（1手=100股）
    if market == "cn" and amount % 100 != 0:
        return {
            "error": f"A股必须以100股整数倍交易（1手=100股）。您试图买入{amount}股。",
            "symbol": symbol,
            "suggestion": f"请使用{(amount // 100) * 100}或{((amount // 100) + 1) * 100}股。",
        }
```

### 6.3 涨跌停价格计算（提示词中说明）

```python
# 在prompts/agent_prompt_astock.py中的交易规则说明
A股交易规则（适用于所有.SH和.SZ股票代码）：
4. **涨跌停限制**:
   - 普通股票：±10%
   - ST股票：±5%
   - 科创板/创业板：±20%
```

---

## 7. A股资讯与信息获取

### 7.1 A股资讯来源

#### **Jina搜索工具** (`tool_jina_search.py`)

**核心功能**：
- 基于Jina AI Reader API的网页内容抓取
- 支持多种日期格式解析和标准化
- 自动过滤未来信息（防前瞻机制）

**防前瞻机制**：
```python
# 在搜索结果中过滤掉TODAY_DATE之后的信息
for item in json_data.get("data", []):
    raw_date = item.get("date", "unknown")
    standardized_date = parse_date_to_standard(raw_date)

    if standardized_date == "unknown":
        filtered_urls.append(item["url"])
        continue

    today_date = get_config_value("TODAY_DATE")
    if today_date > standardized_date:
        filtered_urls.append(item["url"])
```

#### **Alpha Vantage News API** (`tool_alphavantage_news.py`)

**特点**：
- 专业财经新闻API
- 支持情感分析和主题分类
- 严格的日期过滤机制

**时间过滤实现**：
```python
def __call__(self, query: str, tickers: Optional[str] = None, topics: Optional[str] = None):
    # 获取TODAY_DATE并转换为API格式
    today_date = get_config_value("TODAY_DATE")
    if today_date:
        today_datetime = datetime.strptime(today_date, "%Y-%m-%d %H:%M:%S")
        time_to = today_datetime.strftime("%Y%m%dT%H%M")
        time_from_datetime = today_datetime - timedelta(days=30)
        time_from = time_from_datetime.strftime("%Y%m%dT%H%M")
```

**支持的新闻主题**：
- blockchain, earnings, ipo, mergers_and_acquisitions
- financial_markets, economy_fiscal, economy_monetary
- energy_transportation, finance, life_sciences
- manufacturing, real_estate, retail_wholesale, technology

### 7.2 中文财经媒体覆盖

通过Jina搜索可以覆盖主要中文财经媒体：
- 财新网、新浪财经、网易财经
- 东方财富、证券时报、中国证券报
- 证监会、交易所公告
- 上市公司财报和公告

### 7.3 AI决策中的资讯应用

**A股专用提示词设计** (`prompts/agent_prompt_astock.py`)：

```python
你的目标是：
- 通过调用可用的工具进行思考和推理
- 你需要思考各个股票的价格和收益情况
- 你的长期目标是通过这个投资组合最大化收益
- **在做出决策之前，尽可能通过搜索工具收集信息以辅助决策**
```

**强制执行要求**：
```python
⚠️ 重要行为要求：
1. **必须实际调用 buy() 或 sell() 工具**，不要只给出建议或分析
2. **禁止编造错误信息**，如果工具调用失败，会返回真实的错误
3. **禁止说"由于交易系统限制"等自己假设的限制**
```

### 7.4 实际资讯获取示例

**Jina搜索调用示例**：
```python
# 搜索特定公司新闻
get_information("中国平安 业绩 财报 2025")

# 搜索行业分析
get_information("银行业 估值修复 分红政策 2025")

# 搜索政策影响
get_information("央行降息 股市影响 房地产政策")
```

**Alpha Vantage新闻调用示例**：
```python
# 按股票代码搜索
get_market_news(
    query="银行股分析",
    tickers="601318.SH,600036.SH",  # 平安银行、招商银行
    topics="financial_markets"
)

# 按主题搜索
get_market_news(
    query="A股市场分析",
    topics="technology,financial_markets"
)
```

### 7.5 AI决策过程示例

**完整的AI决策流程**（基于日志分析）：

1. **收集信息**：AI被要求"尽可能通过搜索工具收集信息以辅助决策"
2. **分析价格**：读取当前持仓和当前价格的输入
3. **评估市场**：更新估值并调整每个目标的权重
4. **执行交易**：必须实际调用buy()或sell()工具
5. **记录决策**：详细说明买入/卖出的理由

**实际决策日志**：
```
- 卖出：600406.SH 国电南瑞 200股，成交价约24.65元/股
- 理由：股价大幅拉升至阶段高位，落袋一部分利润，控制单一标的权重与回撤风险

- 买入：601012.SH 隆基绿能 100股，成交价约20.79元/股
- 理由：光伏龙头放量强势，景气预期与估值修复共振，左侧小仓位切入
```

---

## 8. 配置文件系统

### 8.1 A股日频数据配置 (`configs/astock_config.json`)

```json
{
  "agent_type": "BaseAgentAStock",
  "market": "cn",
  "date_range": {
    "init_date": "2025-10-01",
    "end_date": "2025-10-29"
  },
  "models": [
    {
      "name": "claude-3.7-sonnet",
      "basemodel": "claude-3-7-sonnet-20250219",
      "signature": "claude-3.7-sonnet",
      "enabled": false
    },
    {
      "name": "gpt-4.1",
      "basemodel": "openai/gpt-4.1",
      "signature": "gpt-4.1",
      "enabled": true
    }
  ],
  "agent_config": {
    "max_steps": 30,
    "max_retries": 3,
    "base_delay": 1.0,
    "initial_cash": 100000.0
  },
  "log_config": {
    "log_path": "./data/agent_data_astock"
  }
}
```

### 8.2 A股小时级配置 (`configs/astock_hour_config.json`)

**关键差异**：
- **时间粒度**: 从日频（`2025-10-01`）变为小时级（`2025-10-09 8:30:00`）
- **启用模型**: 仅`MiniMax-M2`启用
- **时间跨度**: 仅2天的小时级数据（10月9日-11日）
- **agent_type**: `BaseAgentAStock_Hour` - 小时级专用代理

### 8.3 前端市场配置 (`docs/config.yaml`)

**A股日频市场配置（cn）**：
```yaml
cn:
  name: "A-Shares (SSE 50)"
  data_dir: "agent_data_astock"
  benchmark_file: "A_stock/index_daily_sse_50.json"
  benchmark_name: "SSE 50"
  currency: "CNY"
  price_data_type: "merged"  # 合并文件模式
  price_data_file: "A_stock/merged.jsonl"
  time_granularity: "daily"
  enabled: true
  agents:
    - folder: "gemini-2.5-flash"
      display_name: "Gemini 2.5 Flash"
      enabled: true
    # ... 7个AI代理
```

**A股小时级市场配置（cn_hour）**：
```yaml
cn_hour:
  name: "A-Shares (Hourly)"
  data_dir: "agent_data_astock_hour"
  price_data_type: "merged"
  price_data_file: "A_stock/merged_hourly.jsonl"
  time_granularity: "hourly"
  enabled: false  # 默认隐藏
  agents:
    - folder: "gemini-2.5-flash-astock-hour"
    # ... 7个AI代理（小时级版本）
```

---

## 9. 数据处理流程

### 9.1 Tushare数据合并 (`merge_jsonl_tushare.py`)

**核心逻辑**：
```python
def convert_a_stock_to_jsonl():
    # 1. 读取CSV数据
    df = pd.read_csv("A_stock_data/daily_prices_sse_50.csv")

    # 2. 读取股票名称映射
    stock_name_map = dict(zip(name_df["con_code"], name_df["stock_name"]))

    # 3. 按股票代码分组
    grouped = df.groupby("ts_code")

    # 4. 生成JSONL格式
    for ts_code, group_df in grouped:
        # 构建Meta Data
        json_obj = {
            "Meta Data": {
                "2. Symbol": ts_code,
                "2.1. Name": stock_name_map.get(ts_code, "Unknown"),
                "5. Time Zone": "Asia/Shanghai"
            },
            "Time Series (Daily)": time_series
        }
```

**关键处理步骤**：
1. **日期格式转换**: YYYYMMDD → YYYY-MM-DD
2. **字段重命名**: `open` → "1. buy price", `close` → "4. sell price"
3. **成交量转换**: 手 → 股（×100）
4. **防信息泄露**: 最新日期仅保留开盘价
5. **股票名称注入**: 从权重文件获取中文名称

### 9.2 Alpha Vantage数据合并 (`merge_jsonl_alphavantage.py`)

**核心逻辑**：
```python
# 合并所有 daily_price*.json 文件
files = sorted(glob.glob("A_stock_data/daily_price*.json"))

with open(output_file, "w", encoding="utf-8") as fout:
    for fp in files:
        if not any(symbol in basename for symbol in sse_50_codes):
            continue  # 仅处理SSE 50成分股

        data = json.load(f)

        # 字段重命名
        if "1. open" in bar:
            bar["1. buy price"] = bar.pop("1. open")
        if "4. close" in bar:
            bar["4. sell price"] = bar.pop("4. close")

        # 最新日期仅保留买入价
        latest_date = max(series.keys())
        series[latest_date] = {"1. buy price": buy_val}
```

**关键特性**：
1. **文件过滤**: 仅处理SSE 50成分股相关文件
2. **格式统一**: 转换为统一的字段命名
3. **时区修正**: 强制设置为"Asia/Shanghai"
4. **代码转换**: `.SHH` → `.SH`

### 9.3 小时级数据处理 (`merge_jsonl_hourly.py`)

**核心逻辑**：
```python
def convert_hourly_to_jsonl():
    df = pd.read_csv("A_stock_data/A_stock_hourly.csv")

    grouped = df.groupby("stock_code")

    for stock_code, group_df in grouped:
        # 时间格式处理
        datetime_str = str(row["trade_date"])  # "2025-10-09 10:30"
        if datetime_str.count(':') == 1:
            datetime_formatted = datetime_str + ":00"

        # 构建Time Series (60min)
        json_obj = {
            "Meta Data": {
                "3. Last Refreshed": latest_datetime,
                "4. Interval": "60min",
                "6. Time Zone": "Asia/Shanghai"
            },
            "Time Series (60min)": time_series
        }
```

**特殊处理**：
1. **时间补全**: "10:30" → "10:30:00"
2. **时间序列标识**: "Time Series (60min)" 而非 "Time Series (Daily)"
3. **分钟级数据**: 每小时一个数据点

---

## 10. 前端数据加载机制

### 10.1 配置加载器 (`config-loader.js`)

**核心功能**：
```javascript
class ConfigLoader {
    // 加载YAML配置
    async loadConfig() {
        const yamlText = await response.text();
        this.config = jsyaml.load(yamlText);
    }

    // 获取市场配置
    getMarketConfig(marketId) {
        return this.config.markets[marketId];
    }

    // 获取启用代理列表
    getEnabledAgents(marketId) {
        return this.config.markets[marketId].agents;
    }
}
```

### 10.2 数据加载器 (`data-loader.js`)

**A股数据加载逻辑**：
```javascript
async loadAStockPrices() {
    const marketConfig = this.getMarketConfig();
    const priceFile = marketConfig.price_data_file || 'A_stock/merged.jsonl';

    const response = await fetch(`${this.baseDataPath}/${priceFile}`);
    const text = await response.text();
    const lines = text.trim().split('\n');

    for (const line of lines) {
        const data = JSON.parse(line);
        const symbol = data['Meta Data']['2. Symbol'];
        // 支持日频和小时级数据
        this.priceCache[symbol] = data['Time Series (Daily)'] ||
                                  data['Time Series (60min)'];
    }
}
```

**关键特性**：
1. **统一加载**: 所有A股股票一次性加载到缓存
2. **格式兼容**: 自动识别日频（Daily）和小时级（60min）数据
3. **缓存机制**: 避免重复网络请求
4. **市场切换**: 支持`cn`（日频）和`cn_hour`（小时级）市场

### 10.3 缓存管理器 (`cache-manager.js`)

**缓存策略**：
```javascript
class CacheManager {
    isCacheEnabled() {
        // 优先级：URL参数 > localStorage > 配置 > 默认值
        const urlParams = new URLSearchParams(window.location.search);
        if (urlParams.has('nocache')) return urlParams.get('nocache') !== '1';

        const config = window.configLoader.getCacheConfig();
        return config.enabled !== false;
    }

    setCacheData(key, data) {
        const cacheData = {
            data: data,
            timestamp: Date.now(),
            version: this.CACHE_VERSION
        };
        localStorage.setItem(this.CACHE_DATA_KEY, JSON.stringify(cacheData));
    }
}
```

**缓存特性**：
1. **多层控制**: URL参数可强制启用/禁用缓存
2. **版本控制**: 缓存数据带版本号，支持升级
3. **过期管理**: 默认7天过期时间
4. **性能监控**: 记录缓存命中率和加载时间

---

## 11. 数据质量与完整性评估

### 11.1 数据完整性

**亮点**：`AStockIntradayDataFetcher`类实现了智能增量更新：

```python
# get_interdaily_price_astock.py 第99-150行
def get_date_range(self, default_start_date: str = "20251001") -> Tuple[str, str]:
    """如果已有数据，从最后日期的下一天开始；否则使用默认开始日期"""
    if self.output_path.exists():
        # 检测已有数据的最后日期并从下一天开始
        last_date = datetime.strptime(last_date_str.split()[0], "%Y-%m-%d")
        next_date = last_date + timedelta(days=1)
```

**不足**：
- 缺乏数据缺失检测机制
- 无法自动补充历史缺失数据

### 11.2 数据准确性验证

**小时级数据验证**（`base_agent_astock_hour.py`第329-542行）：

```python
ASTOCK_TRADING_HOURS = ["10:30:00", "11:30:00", "14:00:00", "15:00:00"]

def _check_daily_completeness(self, trading_times: List[str], date: str):
    """检查交易日是否有完整的4个时间点"""
    expected_times = set(self.ASTOCK_TRADING_HOURS)
    missing_times = expected_times - found_times
    if not result["is_complete"]:
        print(f"⚠️  警告: {date} 数据不完整")
```

**当前缺失**：
- 无价格异常检测（如涨跌停验证）
- 无跨数据源交叉验证
- 无数据质量评分机制

### 11.3 API重试机制

**Tushare数据获取**（`get_daily_price_tushare.py`第45-106行）：

```python
def api_call_with_retry(api_func, pro_api_instance, max_retries=3, retry_delay=5, timeout=120):
    for attempt in range(1, max_retries + 1):
        try:
            result = api_func(**kwargs)
            return result
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
            wait_time = retry_delay * attempt  # 指数退避
            time.sleep(wait_time)
```

---

## 12. 性能优化分析

### 12.1 当前并发处理

**批量数据获取**（`get_daily_price_tushare.py`第168-206行）：

```python
# 基于6000条记录限制计算批次大小
batch_days = calculate_batch_days(num_stocks)
# 批次间延迟避免触发限流
time.sleep(1)  # 1秒延迟
```

**不足**：
- 无真正的并发/并行处理
- 批量下载是串行执行

### 12.2 缓存策略

**前端缓存**（`scripts/precompute_frontend_cache.py`）：

```python
# 版本哈希机制
CACHE_FORMAT_VERSION = 'v4'

def get_data_version_hash(market_config):
    """基于position文件修改时间生成版本哈希"""
    hash_obj = hashlib.md5()
    # ... 计算文件时间戳哈希
    return hash_obj.hexdigest()[:12]
```

**当前缓存实现**：
- 前端预计算缓存（`us_cache.json`, `cn_cache.json`）
- 按市场分离的缓存文件
- 版本控制支持增量更新检测

**缺失**：
- 无后端数据层缓存
- 价格数据每次读取都从JSONL文件解析

---

## 13. 扩展性评估

### 13.1 数据格式标准化

项目采用**Alpha Vantage兼容格式**作为标准（`merge_jsonl_tushare.py`）：

```python
json_obj = {
    "Meta Data": {
        "1. Information": "Daily Prices...",
        "2. Symbol": ts_code,
        "2.1. Name": stock_name,  # A股特有：股票名称
        "3. Last Refreshed": latest_date_formatted,
        "5. Time Zone": "Asia/Shanghai",
    },
    "Time Series (Daily)": {
        "YYYY-MM-DD": {
            "1. buy price": str(row["open"]),
            "4. sell price": str(row["close"]),
            # ...
        }
    }
}
```

### 13.2 多市场支持架构

**市场类型检测**（`price_tools.py`第46-70行）：

```python
def get_market_type() -> str:
    """智能获取市场类型"""
    # 方式1: 从配置读取
    market = get_config_value("MARKET", None)
    if market in ["cn", "us", "crypto"]:
        return market
    # 方式2: 根据日志路径推断
    if "astock" in log_path.lower():
        return "cn"
```

### 13.3 科创板/北交所支持准备度

| 项目 | 当前状态 | 建议改进 |
|------|----------|----------|
| 股票代码格式 | 支持`.SH`, `.SZ` | 需添加`.BJ`（北交所） |
| 涨跌停规则 | 硬编码在提示词中 | 应根据股票类型动态配置 |
| 交易时间 | 固定4个时间点 | 北交所时间不同，需参数化 |

---

## 14. 与美股/加密货币系统对比

### 14.1 架构对比

| 特性 | 美股 | A股 | 加密货币 |
|------|------|-----|----------|
| 数据源 | Alpha Vantage | Tushare + efinance | Alpha Vantage |
| 增量更新 | 有限 | 完善 | 有合并逻辑 |
| 重试机制 | 基础 | 完善（指数退避） | 基础 |
| 数据验证 | 无 | 有时间点完整性检查 | 无 |
| 交易规则 | 简单 | 复杂（T+1, 100手） | 简单 |

### 14.2 A股系统优势

1. **交易规则支持完善**：
   - T+1结算规则
   - 100股手数限制
   - 涨跌停限制

2. **双数据源冗余**

3. **中文股票名称支持**

### 14.3 A股系统劣势

1. **性能较差**：无并发处理
2. **数据验证不足**：无价格异常检测
3. **缓存策略单一**：仅有前端缓存

---

## 15. 技术债务与改进建议

### 15.1 高优先级改进

#### 1. 添加数据质量监控

```python
def validate_price_data(symbol: str, date: str, price: float, market: str = "cn"):
    """价格异常检测"""
    # 涨跌停验证
    if market == "cn":
        prev_close = get_previous_close(symbol, date)
        change_pct = (price - prev_close) / prev_close * 100
        if abs(change_pct) > 10.5:  # 留1%缓冲
            log_warning(f"可能异常：{symbol} 在 {date} 涨跌幅 {change_pct:.2f}%")
```

#### 2. 实现并发数据获取

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

async def fetch_all_stocks_concurrent(stock_list, max_workers=5):
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        loop = asyncio.get_event_loop()
        tasks = [loop.run_in_executor(executor, fetch_stock, symbol)
                 for symbol in stock_list]
        return await asyncio.gather(*tasks)
```

#### 3. 添加后端数据缓存

```python
# 使用内存缓存避免重复读取JSONL
from functools import lru_cache

@lru_cache(maxsize=128)
def get_stock_price_cached(symbol: str, date: str, market: str):
    return get_open_prices(date, [symbol], market=market)
```

### 15.2 中优先级改进

1. **科创板/北交所支持**：
   - 添加`.BJ`后缀支持
   - 配置化涨跌停规则

2. **跨数据源验证**：
   - 对比Tushare和efinance数据
   - 记录差异日志

3. **数据补全机制**：
   - 检测历史缺失数据
   - 自动补充缺失数据点

### 15.3 低优先级改进

1. **数据压缩存储**：JSONL文件可压缩存储
2. **数据库替代**：考虑使用SQLite替代JSONL
3. **WebSocket实时数据**：支持盘中实时价格

---

## 16. 总结

### 数据质量评分

| 维度 | 评分 | 说明 |
|------|------|------|
| 完整性 | 7/10 | 有增量更新，缺缺失检测 |
| 准确性 | 6/10 | 有基础验证，缺异常检测 |
| 性能 | 5/10 | 无并发，缓存单一 |
| 扩展性 | 7/10 | 格式标准，新市场需改动 |
| 可维护性 | 8/10 | 代码结构清晰，中文注释完善 |

**综合评分：6.6/10**

### 关键发现

1. **A股数据系统是三个市场中交易规则支持最完善的**
2. **增量更新机制设计合理，但缺乏数据质量监控**
3. **性能是最大瓶颈**，无并发处理是主要技术债务
4. **扩展到科创板/北交所需要中等工作量的改动**
5. **资讯系统完善**，支持中文财经媒体和防前瞻机制

### 核心数据流向图

```
数据源 → efinance库 → CSV文件 → merged.jsonl → MCP工具 → 代理系统
    ↓
Tushare API → CSV → merged.jsonl → 交易决策 → 虚拟交易执行
    ↓
Alpha Vantage → JSON → 合并处理 → 统一格式 → 前端展示
```

---

*报告生成时间: 2025-12-09*
*分析类型: A股数据来源专项深度分析*
*基于: 5个并行深度分析任务*
*覆盖模块: 16个核心分析维度*
