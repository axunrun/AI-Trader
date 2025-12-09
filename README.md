<div align="center">
  <picture>
      <img src="./assets/AI-Trader-log.png" width="30%" style="border: none; box-shadow: none;">
  </picture>
</div >

<div align="center">

# 🚀 AI-Trader: A股AI交易分析平台
### *专业的A股AI交易分析系统*

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Feishu](https://img.shields.io/badge/💬Feishu-Group-blue?style=flat)](./Communication.md) 
[![WeChat](https://img.shields.io/badge/WeChat-Group-green?style=flat&logo=wechat)](./Communication.md)


**一个专业的A股AI交易分析平台，集成机器学习、强化学习和自然语言生成技术，实现AI决策完全可视化！**

## 🏆 当前锦标赛排行榜 🏆 
[*点击查看: AI实时交易*](https://ai4trade.ai)

</div>



---

## AI-Trader 的朋友们：其他有趣的项目
- [TradeTrap](https://github.com/Yanlewen/TradeTrap): 一个专注安全的工具包，用于评估并加固基于大语言模型的交易代理，提供提示注入与 MCP 劫持攻击等模块，用于韧性测试。

- [RockAlpha](https://rockalpha.rockflow.ai/): 由 RockFlow 推出的投资竞技场。模型输入包括交易规则、行情数据、账户状态与买入力以及新闻资讯；输出为下单决策。

- [TwinMarket](https://github.com/FreedomIntelligence/TwinMarket): 一个多智能体框架，利用大语言模型模拟中国A股市场中的投资者行为和新兴社会经济现象。

---

## **如何使用这个数据集**

很简单！

你只需要提交一个pr，这个pr至少包含：`./agent/{你的策略}.py`（你可以继承Basemodel来创建你的策略！），`./configs/{yourconfig}`,如何运行你的策略的说明，只要我们能够运行，我们将在我们的平台上运行一周以上并持续更新你的战绩！

## 🎉 本周更新

我们很高兴宣布以下重大更新已于本周完成：

### 📈 市场专业化
- ✅ **专注A股市场** - 全面聚焦中国A股市场，支持上证50、上证180、深证100、创业板100、科创50等480只股票。
- ✅ **股票池扩展** - 从50只扩展到480只，覆盖5大核心板块。

### ⏰ 增强交易能力
- ✅ **小时级别交易支持** - 从日线级别升级到小时级别交易间隔，实现更精确、更及时的市场参与，具有精细的时间控制。

### 🎨 用户体验改进
- ✅ **实时交易仪表板** - 引入所有代理交易活动的实时可视化，提供全面的市场运营监督。

- ✅ **代理推理显示** - 实现AI决策过程的完全透明，展示详细的推理链，显示每个交易决策是如何形成的。

- ✅ **交互式排行榜** - 推出动态性能排名系统，实时更新，允许用户实时跟踪和比较代理性能。

---

<div align="center">

[🚀 快速开始](#-快速开始) • [📈 性能分析](#-性能分析) • [🛠️ 配置指南](#-配置指南) • [English Documentation](README.md)

</div>

---

## 🌟 项目介绍

> **AI-Trader是一个专业的A股AI交易分析平台，集成机器学习、强化学习和自然语言生成技术，实现100% AI决策透明化和480只A股全覆盖！**

### 🎯 核心特性

- 🤖 **完全自主决策**: AI代理100%独立分析、决策、执行，零人工干预
- 🛠️ **纯工具驱动架构**: 基于MCP工具链，AI通过标准化工具调用完成所有交易操作
- 🏆 **多模型支持**: 支持GPT、Claude、Qwen、DeepSeek等主流AI模型进行A股交易分析
- 📊 **实时性能分析**: 完整的交易记录、持仓监控和盈亏分析
- 🔍 **智能市场情报**: 集成Jina搜索，获取实时市场新闻和财务报告
- ⚡ **MCP工具链集成**: 基于Model Context Protocol的模块化工具生态系统
- 🔌 **可扩展策略框架**: 支持第三方策略和自定义AI代理集成
- ⏰ **历史回放功能**: 时间段回放功能，自动过滤未来信息


---

### 🎮 交易环境
每个AI模型以100,000¥起始资金在受控环境中交易480只A股，覆盖上证50、上证180、深证100、创业板100、科创50，使用真实市场数据和历史回放功能。

- 💰 **初始资金**: 100,000¥人民币（A股）
- 📈 **交易范围**:
  - 上证50成分股（50只稳定蓝筹）
  - 上证180成分股（130只大盘成长）
  - 深证100成分股（100只创新活力）
  - 创业板100成分股（100只科技前沿）
  - 科创50成分股（50只科创龙头）
- ⏰ **交易时间**: A股工作日市场时间（T+1交易制度），支持历史模拟
- 📊 **数据集成**: Tushare Pro API结合Jina AI市场情报
- 🔄 **时间管理**: 历史期间回放，自动过滤未来信息

---

### 🧠 智能交易能力
AI代理完全自主运行，进行市场研究、制定交易决策，并在无人干预的情况下持续优化策略。

- 📰 **自主市场研究**: 智能检索和过滤市场新闻、分析师报告和财务数据
- 💡 **独立决策引擎**: 多维度分析驱动完全自主的买卖执行
- 📝 **全面交易记录**: 自动记录交易理由、执行细节和投资组合变化
- 🔄 **自适应策略演进**: 基于市场表现反馈自我优化的算法

---

### 🏁 竞赛规则
所有AI模型在相同条件下竞争，使用相同的资金、数据访问、工具和评估指标，确保公平比较。

- 💰 **起始资金**: $10,000美元或100,000¥人民币初始投资
- 📊 **数据访问**: 统一的市场数据和信息源
- ⏰ **运行时间**: 同步的交易时间窗口
- 📈 **性能指标**: 所有模型的标准评估标准
- 🛠️ **工具访问**: 所有参与者使用相同的MCP工具链

🎯 **目标**: 确定哪个AI模型通过纯自主操作获得卓越的投资回报！

### 🚫 零人工干预
AI代理完全自主运行，在没有任何人工编程、指导或干预的情况下制定所有交易决策和策略调整。

- ❌ **无预编程**: 零预设交易策略或算法规则
- ❌ **无人工输入**: 完全依赖内在的AI推理能力
- ❌ **无手动覆盖**: 交易期间绝对禁止人工干预
- ✅ **纯工具执行**: 所有操作仅通过标准化工具调用执行
- ✅ **自适应学习**: 基于市场表现反馈的独立策略优化

---

## ⏰ 历史回放架构

AI-Trader Bench的核心创新是其**完全可重放**的交易环境，确保AI代理在历史市场数据上的性能评估具有科学严谨性和可重复性。

### 🔄 时间控制框架

#### 📅 灵活的时间设置
```json
{
  "date_range": {
    "init_date": "2025-01-01",  // 任意开始日期
    "end_date": "2025-01-31"    // 任意结束日期
  }
}
```
---

### 🛡️ 防前瞻数据控制
AI只能访问当前时间及之前的数据。不允许未来信息。

- 📊 **价格数据边界**: 市场数据访问限制在模拟时间戳和历史记录
- 📰 **新闻时间线执行**: 实时过滤防止访问未来日期的新闻和公告
- 📈 **财务报告时间线**: 信息限制在模拟当前日期的官方发布数据
- 🔍 **历史情报范围**: 市场分析限制在时间上适当的数据可用性

### 🎯 重放优势

#### 🔬 实证研究框架
- 📊 **市场效率研究**: 评估AI在不同市场条件和波动制度下的表现
- 🧠 **决策一致性分析**: 检查AI交易逻辑的时间稳定性和行为模式
- 📈 **风险管理评估**: 验证AI驱动的风险缓解策略的有效性

#### 🎯 公平竞赛框架
- 🏆 **平等信息访问**: 所有AI模型使用相同的历史数据集运行
- 📊 **标准化评估**: 使用统一数据源计算的性能指标
- 🔍 **完全可重复性**: 具有可验证结果的完整实验透明度

---

## 📁 项目架构

```
AI-Trader Bench/
├── 🤖 核心系统
│   ├── main.py                    # 🎯 主程序入口
│   ├── agent/
│   │   └── base_agent_astock/     # 🇨🇳 A股专用交易代理
│   │       ├── base_agent_astock.py  # A股日线代理类
│   │       ├── base_agent_astock_hour.py # A股小时级代理类
│   │       └── __init__.py
│   └── configs/                   # ⚙️ 配置文件
│
├── 🛠️ MCP工具链
│   ├── agent_tools/
│   │   ├── tool_trade.py          # 💰 交易执行（A股专用）
│   │   ├── tool_get_price_local.py # 📊 价格查询（A股）
│   │   ├── tool_jina_search.py   # 🔍 信息搜索
│   │   ├── tool_math.py           # 🧮 数学计算
│   │   └── start_mcp_services.py  # 🚀 MCP服务启动脚本
│   └── tools/                     # 🔧 辅助工具
│
├── 📊 数据系统
│   ├── data/
│   │   ├── A_stock/               # 🇨🇳 A股市场数据
│   │   │   ├── A_stock_data/              # 📁 A股数据存储目录
│   │   │   │   ├── sse_50_weight.csv          # 📋 上证50成分股权重
│   │   │   │   ├── daily_prices_sse_50.csv    # 📈 日线价格数据（CSV）
│   │   │   │   ├── A_stock_hourly.csv         # ⏰ 60分钟K线数据（CSV）
│   │   │   │   └── index_daily_sse_50.json    # 📊 上证50指数基准数据
│   │   │   ├── merged.jsonl               # 🔄 A股日线统一数据格式
│   │   │   ├── merged_hourly.jsonl        # ⏰ A股小时级统一数据格式
│   │   │   ├── get_daily_price_tushare.py # 📥 A股日线数据获取（Tushare API）
│   │   │   ├── get_daily_price_alphavantage.py # 📥 A股日线数据获取（Alpha Vantage API）
│   │   │   ├── get_interdaily_price_astock.py # ⏰ A股小时级数据获取（efinance）
│   │   │   ├── merge_jsonl_tushare.py     # 🔄 A股日线数据格式转换（Tushare）
│   │   │   ├── merge_jsonl_alphavantage.py # 🔄 A股日线数据格式转换（Alpha Vantage）
│   │   │   └── merge_jsonl_hourly.py      # ⏰ A股小时级数据格式转换
│   │   ├── agent_data_astock/     # 📝 A股AI交易记录
│   │   │   ├── deepseek-chat-v3.1/       # DeepSeek V3.2 交易记录
│   │   │   │   ├── position/             # 📊 持仓记录
│   │   │   │   └── log/                  # 📝 日志记录（JSONL格式）
│   │   │   │       └── YYYY-MM-DD/
│   │   │   │           └── log.jsonl     # 每日详细日志
│   │   │   └── MiniMax-M2/               # MiniMax M2 交易记录
│   │   │       ├── position/             # 📊 持仓记录
│   │   │       └── log/                  # 📝 日志记录（JSONL格式）
│   │   └── agent_data_astock_hour/  # ⏰ A股AI小时级交易记录
│   │       ├── deepseek-chat-v3.1-astock-hour/   # DeepSeek V3.2 小时级记录
│   │       └── MiniMax-M2-astock-hour/           # MiniMax M2 小时级记录
│   └── calculate_performance.py   # 📈 性能分析
│
├── 💬 提示词系统
│   └── prompts/
│       └── agent_prompt_astock.py # 🇨🇳 A股专用交易提示词
│
├── 🎨 前端界面（docs/）
│   ├── index.html                 # 🏠 资产演变页面
│   ├── portfolio.html             # 💼 投资组合页面
│   ├── ai-reasoning.html          # 🧠 AI思考全过程页面
│   ├── assets/
│   │   ├── css/
│   │   │   └── styles.css         # 🎨 样式文件
│   │   └── js/
│   │       ├── config-loader.js   # ⚙️ 配置加载器
│   │       ├── cache-manager.js   # 💾 缓存管理器
│   │       ├── data-loader.js     # 📊 数据加载器
│   │       ├── asset-chart.js     # 📈 资产图表
│   │       ├── transaction-loader.js # 💰 交易数据加载
│   │       └── ai-reasoning.js    # 🧠 AI推理过程展示
│   └── config.yaml                # 📋 前端配置文件
│
├── 📚 高级功能模块
│   ├── ml/                        # 🤖 机器学习模块
│   │   ├── simplified_technical_indicators.py  # 技术指标分析
│   │   └── prediction_model.py    # 预测模型
│   ├── rl/                        # 🎮 强化学习模块
│   │   └── simplified_trading_env.py  # A股交易环境
│   ├── nlg/                       # 📝 自然语言生成
│   │   └── trading_report_generator.py  # 交易报告生成
│   └── monitoring/                # ⚠️ 实时监控
│       └── real_time_monitor.py   # 实时监控告警
│
├── 📋 配置与文档
│   ├── configs/                   # ⚙️ 系统配置
│   │   └── astock_config.json     # A股配置示例
│   └── calc_perf.sh              # 🚀 性能计算脚本
│
└── 🚀 快速启动脚本
    └── scripts/                   # 🛠️ 便捷启动脚本
        ├── main_a_stock_step1.sh  # A股：数据准备
        ├── main_a_stock_step2.sh  # A股：启动MCP服务
        ├── main_a_stock_step3.sh  # A股：运行交易代理
        └── start_ui.sh            # 启动Web界面（docs/）
```

### 🧠 AI思考全过程页面详解

**AI思考全过程**是AI-Trader的核心创新功能，实现了AI决策过程的100%透明化。该页面允许用户深入了解AI代理的完整思考链路。

#### 📊 数据获取机制

**1. 数据源**
- **位置**: `data/agent_data_astock/{agent_name}/log/{YYYY-MM-DD}/log.jsonl`
- **格式**: JSONL（JSON Lines），每行一个完整的日志记录
- **编码**: UTF-8，支持中文字符

**2. 数据结构**
```json
{
  "type": "market_analysis",  // 日志类型：market_analysis/decision/trade/research
  "timestamp": "2025-10-31 14:30:00",
  "summary": "市场分析摘要",
  "analysis": {
    "indicators": {
      "RSI": "65.4",
      "MACD": "金叉信号"
    },
    "sentiment": "市场情绪偏乐观"
  }
}
```

**3. 日志分类**
- 🔍 **market_analysis**: 市场数据分析（技术指标、情绪分析）
- 💡 **decision**: 决策推理（买卖决策、理由说明）
- 💹 **trade**: 交易行动（具体交易操作、持仓变化）
- 📚 **research**: 研究记录（市场调研、新闻分析）

#### 🎨 前端展示机制

**1. 页面结构 (`docs/ai-reasoning.html`)**
```html
<!-- 代理选择器 -->
<select id="agentSelect">
  <option value="">请选择代理...</option>
</select>

<!-- 日期选择器 -->
<select id="dateSelect" disabled>
  <option value="">请先选择代理...</option>
</select>

<!-- 推理容器 -->
<div id="reasoningContainer">
  <!-- 动态加载的推理内容 -->
</div>
```

**2. 数据处理流程 (`docs/assets/js/ai-reasoning.js`)**
```javascript
class AIReasoningViewer {
    // 1. 加载可用代理列表
    async loadAvailableAgents() {
        const agents = await this.dataLoader.loadAgentList();
        // 从 agent_data_astock 目录读取
    }

    // 2. 加载可用日期
    async loadAvailableDates(agent) {
        // 扫描 log/ 目录获取所有日期
        const response = await fetch(`./data/agent_data_astock/${agent}/log/`);
        // 解析HTML目录列表，提取日期
    }

    // 3. 加载并解析JSONL数据
    async loadReasoningData() {
        const response = await fetch(
            `./data/agent_data_astock/${agent}/log/${date}/log.jsonl`
        );
        const text = await response.text();
        const logs = text.trim().split('\n').map(line => JSON.parse(line));
        // 按 type 字段分组：market_analysis, decision, trade, research
    }

    // 4. 分组展示
    displayReasoningData(logs) {
        const marketAnalysis = logs.filter(log => log.type === 'market_analysis');
        const decisions = logs.filter(log => log.type === 'decision');
        const trades = logs.filter(log => log.type === 'trade');
        const research = logs.filter(log => log.type === 'research');

        // 渲染可折叠的分类展示
        this.renderSection('🔍 市场分析', marketAnalysis);
        this.renderSection('💡 决策推理', decisions);
        this.renderSection('💹 交易行动', trades);
        this.renderSection('📚 研究记录', research);
    }
}
```

**3. 样式与交互**
- **可折叠设计**: 每个分类可独立展开/收起，节省空间
- **时间排序**: 按时间戳倒序（最新在前）
- **统计概览**: 顶部显示各类型记录的数量统计
- **滚动优化**: 自动滚动到顶部按钮

#### 🔄 实时更新机制

**1. 数据获取**
- 用户切换代理或日期时触发
- 使用 `fetch()` API 异步加载JSONL文件
- 错误处理：加载失败显示友好提示

**2. 数据解析**
```javascript
// 解析JSONL格式
const lines = text.trim().split('\n').filter(line => line.trim() !== '');
const logs = lines.map(line => {
    try {
        return JSON.parse(line);
    } catch (e) {
        console.error('解析失败:', line, e);
        return null;
    }
}).filter(log => log !== null);
```

**3. 缓存机制**
- 浏览器本地存储缓存（localStorage）
- 避免重复加载相同数据
- 缓存过期时间：7天（可配置）

#### 📱 用户交互流程

**步骤1: 选择AI代理**
- 从下拉列表选择：MiniMax M2 或 DeepSeek V3.2
- 自动加载该代理的可用日期列表

**步骤2: 选择日期**
- 显示代理的所有交易日
- 按时间倒序排列（最新在前）
- 点击加载按钮获取数据

**步骤3: 查看推理过程**
- 默认显示所有分类概览
- 点击分类标题展开详细内容
- 支持快速跳转到特定类型

#### 🎯 核心特性

- ✅ **完整透明**: 100%还原AI的思考过程
- ✅ **分类清晰**: 按决策阶段分类展示
- ✅ **时间有序**: 完整的决策时间线
- ✅ **交互友好**: 可折叠、响应式设计
- ✅ **实时加载**: 按需加载，无性能负担
- ✅ **数据可追溯**: 每条记录都可追溯到具体时间和操作

### 🔧 核心组件详解

#### 🎯 主程序 (`main.py`)
- **多模型并发**: 同时运行多个AI模型进行交易
- **动态代理加载**: 基于配置文件自动加载对应的代理类型
- **配置管理**: 支持JSON配置文件和环境变量
- **日期管理**: 灵活的交易日历和日期范围设置
- **错误处理**: 完善的异常处理和重试机制

#### 🤖 AI代理系统

**当前支持**: A股市场专用交易系统

| 代理类型 | 模块路径 | 适用场景 | 特性 |
|---------|---------|---------|------|
| **BaseAgentAStock** | `agent.base_agent_astock.base_agent_astock` | A股日线交易 | 内置A股规则，上证50默认池，中文提示词，T+1规则 |
| **BaseAgentAStock_Hour** | `agent.base_agent_astock.base_agent_astock_hour` | A股小时级交易 | A股小时级数据（10:30/11:30/14:00/15:00），T+1规则 |

**支持的AI模型**:
1. **DeepSeek V3.2** (`deepseek-chat-v3.1`)
   - 国产大模型，擅长逻辑推理
   - 优化的中文交易提示词
   - 高效的工具调用能力

2. **MiniMax M2** (`MiniMax-M2`)
   - MiniMax公司最新模型
   - 出色的数据分析能力
   - 快速响应与决策

**架构优势**：
- 🎯 **A股专用**: 深度适配A股交易规则（T+1、涨跌停、100股整数倍）
- 🇨🇳 **本土优化**: 中文提示词，更适合中国投资者习惯
- ⚡ **双模式**: 支持日线交易和小时级交易
- 🧠 **决策透明**: 完整记录AI推理过程，100%可追溯
- 🔌 **易于扩展**: 模块化设计，可轻松添加新模型

#### 🛠️ MCP工具链
| 工具 | 功能 | 市场支持 | API |
|------|------|---------|-----|
| **交易工具** | 买入/卖出A股，持仓管理 | 🇨🇳 A股 | `buy_astock()`, `sell_astock()` |
| **价格工具** | 实时和历史价格查询 | 🇨🇳 A股 | `get_price_local()` |
| **搜索工具** | 市场信息搜索 | 全球市场 | `get_information()` |
| **数学工具** | 财务计算和分析 | 通用 | 基础数学运算 |

**工具特性**：
- 🎯 **A股专用**: 深度适配A股交易规则（100股整数倍、T+1、涨跌停10%限制）
- 📏 **规则适配**: 自动应用A股交易规则（.SH/.SZ后缀识别）
- 🇨🇳 **本土化**: 支持人民币计价，中文提示词
- 📊 **多数据源**: 支持Tushare、Alpha Vantage、efinance多源数据

#### 📊 数据系统
- **📈 价格数据**:
  - 🇨🇳 A股市场数据（上证50指数）通过Tushare API
  - ⏰ A股小时级数据（10:30/11:30/14:00/15:00）通过efinance
  - 📁 统一JSONL格式，便于高效读取
- **📝 交易记录**:
  - 每个AI模型的详细交易历史和推理过程
  - 📊 日线数据：`data/agent_data_astock/{model}/`
  - ⏰ 小时级数据：`data/agent_data_astock_hour/{model}/`
  - 🔍 推理日志：`data/agent_data_astock/{model}/log/{YYYY-MM-DD}/log.jsonl`
- **📊 性能指标**:
  - 夏普比率、最大回撤、年化收益等
  - 支持两模型对比分析
- **🔄 数据同步**:
  - 自动化的数据获取和更新机制
  - 独立的数据获取脚本，支持增量更新
- **🧠 AI推理数据**:
  - JSONL格式的详细推理日志
  - 按类型分类：market_analysis/decision/trade/research
  - 完整时间戳和决策链记录

## 🚀 快速开始

### 📋 前置要求

- **Python 3.10+**
- **API密钥**:
  - DeepSeek/MiniMax（用于AI模型）
  - Alpha Vantage / Tushare（用于A股数据）
  - Jina AI（用于市场信息搜索）


### ⚡ 一键安装

```bash
# 1. 克隆项目
git clone https://github.com/HKUDS/AI-Trader.git
cd AI-Trader

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入你的API密钥
```

### 🔑 环境配置

创建 `.env` 文件并配置以下变量：

```bash
# 🤖 AI模型API配置
DEEPSEEK_API_KEY=your_deepseek_key
MINIMAX_API_KEY=your_minimax_key

# 📊 数据源配置
ALPHAADVANTAGE_API_KEY=your_alpha_vantage_key  # 用于A股数据（备选）
TUSHARE_TOKEN=your_tushare_token               # 用于A股数据（推荐）
JINA_API_KEY=your_jina_api_key

# ⚙️ 系统配置
RUNTIME_ENV_PATH=./runtime_env.json #推荐使用绝对路径

# 🌐 服务端口配置
MATH_HTTP_PORT=8000
SEARCH_HTTP_PORT=8001
TRADE_HTTP_PORT=8002
GETPRICE_HTTP_PORT=8003

# 🧠 AI代理配置
AGENT_MAX_STEP=30             # 最大推理步数
```

### 📦 依赖包

```bash
# 安装生产环境依赖
pip install -r requirements.txt

# 或手动安装核心依赖
pip install langchain langchain-openai langchain-mcp-adapters fastmcp python-dotenv requests numpy pandas tushare efinance
```

## 🎮 运行指南

### 🚀 使用脚本快速启动

我们在 `scripts/` 目录中提供了便捷的启动脚本：

#### 🇨🇳 A股市场（上证50）
```bash
# 分步运行：
bash scripts/main_a_stock_step1.sh  # 步骤1: 准备A股数据
bash scripts/main_a_stock_step2.sh  # 步骤2: 启动MCP服务
bash scripts/main_a_stock_step3.sh  # 步骤3: 运行A股交易代理
```

#### 🌐 Web界面
```bash
# 启动Web界面
bash scripts/start_ui.sh
# 访问: http://localhost:8000
```

---

### 📋 手动运行指南

如果您更喜欢手动执行命令，请按照以下步骤操作：

### 📊 步骤1: A股数据准备

#### 🇨🇳 A股市场数据（上证50）

```bash
cd data/A_stock

# 📈 方法1：使用 Tushare API 获取日线数据（推荐）
python get_daily_price_tushare.py
python merge_jsonl_tushare.py

# 📈 方法2：使用 Alpha Vantage API 获取日线数据（备选）
python get_daily_price_alphavantage.py
python merge_jsonl_alphavantage.py

# 📊 日线数据将保存至: data/A_stock/merged.jsonl

# ⏰ 获取60分钟K线数据（小时级交易）
python get_interdaily_price_astock.py
python merge_jsonl_hourly.py

# 📊 小时数据将保存至: data/A_stock/merged_hourly.jsonl
```


### 🛠️ 步骤2: 启动MCP服务

```bash
cd ./agent_tools
python start_mcp_services.py
```

### 🚀 步骤3: 启动AI竞技场

#### A股交易（上证50）：
```bash
# 🎯 运行A股交易
python main.py configs/astock_config.json
```

### ⏰ 时间设置示例

#### 📅 A股日线配置示例 (使用 BaseAgentAStock)
```json
{
  "agent_type": "BaseAgentAStock",  // A股日线专用代理
  "market": "cn",                   // 市场类型："cn" A股（可选，会被忽略，始终使用cn）
  "date_range": {
    "init_date": "2025-10-09",      // 回测开始日期
    "end_date": "2025-10-31"         // 回测结束日期
  },
  "models": [
    {
      "name": "claude-3.7-sonnet",
      "basemodel": "anthropic/claude-3.7-sonnet",
      "signature": "claude-3.7-sonnet",
      "enabled": true
    }
  ],
  "agent_config": {
    "initial_cash": 100000.0        // 初始资金：¥100,000人民币
  },
  "log_config": {
    "log_path": "./data/agent_data_astock"  // A股日线数据路径
  }
}
```

#### 📅 A股小时级配置示例 (使用 BaseAgentAStock_Hour)
```json
{
  "agent_type": "BaseAgentAStock_Hour",  // A股小时级专用代理
  "market": "cn",                        // 市场类型："cn" A股（可选，会被忽略，始终使用cn）
  "date_range": {
    "init_date": "2025-10-09 10:30:00",  // 回测开始时间（小时级）
    "end_date": "2025-10-31 15:00:00"    // 回测结束时间（小时级）
  },
  "models": [
    {
      "name": "claude-3.7-sonnet",
      "basemodel": "anthropic/claude-3.7-sonnet",
      "signature": "claude-3.7-sonnet-astock-hour",
      "enabled": true
    }
  ],
  "agent_config": {
    "initial_cash": 100000.0        // 初始资金：¥100,000人民币
  },
  "log_config": {
    "log_path": "./data/agent_data_astock_hour"  // A股小时级数据路径
  }
}
```

> 💡 **提示**: A股小时级交易时间点为：10:30、11:30、14:00、15:00（每天4个时间点）

> 💡 **提示**: 使用 `BaseAgentAStock` 时，`market` 参数会被自动设置为 `"cn"`，无需手动指定。

### 📈 启动Web界面

```bash
cd docs
python3 -m http.server 8000
# 访问 http://localhost:8000
```

或者使用启动脚本：

```bash
# 启动Web界面
bash scripts/start_ui.sh
# 访问: http://localhost:8888
```

---

## 📈 性能分析

### 🏆 竞技规则

| 规则项 | A股（中国） |
|--------|------------|
| **💰 初始资金** | ¥100,000 |
| **📈 交易标的** | 上证50 |
| **🌍 市场** | 中国A股市场 |
| **⏰ 交易时间** | 工作日 |
| **💲 价格基准** | 开盘价 |
| **📝 记录方式** | JSONL格式 |
| **🤖 AI模型** | DeepSeek V3.2 vs MiniMax M2 |
| **⏰ 时间粒度** | 日线 / 小时级（10:30/11:30/14:00/15:00） |
| **🧠 决策透明** | 100%推理过程可视化 |

## ⚙️ 配置指南

### 📋 配置文件结构

```json
{
  "agent_type": "BaseAgent",
  "market": "us",
  "date_range": {
    "init_date": "2025-01-01",
    "end_date": "2025-01-31"
  },
  "models": [
    {
      "name": "claude-3.7-sonnet",
      "basemodel": "anthropic/claude-3.7-sonnet",
      "signature": "claude-3.7-sonnet",
      "enabled": true
    }
  ],
  "agent_config": {
    "max_steps": 30,
    "max_retries": 3,
    "base_delay": 1.0,
    "initial_cash": 10000.0
  },
  "log_config": {
    "log_path": "./data/agent_data"
  }
}
```

### 🔧 配置参数说明

| 参数 | 说明 | 可选值 | 默认值 |
|------|------|--------|--------|
| `agent_type` | AI代理类型 | "BaseAgentAStock"（A股日线）<br>"BaseAgentAStock_Hour"（A股小时级） | "BaseAgentAStock" |
| `market` | 市场类型 | "cn"（A股）<br>注：会自动设置为"cn"，无需手动指定 | "cn" |
| `max_steps` | 最大推理步数 | 正整数 | 30 |
| `max_retries` | 最大重试次数 | 正整数 | 3 |
| `base_delay` | 操作延迟(秒) | 浮点数 | 1.0 |
| `initial_cash` | 初始资金 | 浮点数 | ¥100,000（A股） |

#### 📋 代理类型说明

| 代理类型 | 适用市场 | 交易频率 | 特点 |
|---------|---------|---------|------|
| **BaseAgentAStock** | A股 | 日线 | • 专为A股日线优化<br>• 内置A股交易规则（一手100股、T+1）<br>• 默认上证50股票池<br>• 人民币计价<br>• 支持DeepSeek V3.2和MiniMax M2 |
| **BaseAgentAStock_Hour** | A股 | 小时级 | • A股小时级交易（10:30/11:30/14:00/15:00）<br>• 支持盘中4个时间点交易<br>• 继承所有A股交易规则<br>• 数据源：merged_hourly.jsonl |

#### 🧠 AI模型支持

**当前支持两个AI模型**：

1. **DeepSeek V3.2** (`deepseek-chat-v3.1`)
   - 国产大模型，逻辑推理能力强
   - 优化的中文交易提示词
   - 适合复杂市场分析

2. **MiniMax M2** (`MiniMax-M2`)
   - MiniMax公司最新模型
   - 出色的数据分析能力
   - 快速响应与决策

**模型切换方法**：
在配置文件的 `models` 数组中修改对应的模型名称和API密钥即可。

### 📊 数据格式

#### 💰 持仓记录 (position.jsonl)
```json
{
  "date": "2025-01-20",
  "id": 1,
  "this_action": {
    "action": "buy",
    "symbol": "AAPL", 
    "amount": 10
  },
  "positions": {
    "AAPL": 10,
    "MSFT": 0,
    "CASH": 9737.6
  }
}
```

#### 📈 价格数据 (merged.jsonl)
```json
{
  "Meta Data": {
    "2. Symbol": "AAPL",
    "3. Last Refreshed": "2025-01-20"
  },
  "Time Series (Daily)": {
    "2025-01-20": {
      "1. buy price": "255.8850",
      "2. high": "264.3750", 
      "3. low": "255.6300",
      "4. sell price": "262.2400",
      "5. volume": "90483029"
    }
  }
}
```

### 📁 文件结构

```
data/agent_data_astock/              # A股日线数据
├── deepseek-chat-v3.1/              # DeepSeek V3.2
│   ├── position/
│   │   └── position.jsonl           # 📝 持仓记录
│   └── log/
│       └── 2025-10-31/
│           └── log.jsonl            # 🧠 AI推理日志（JSONL格式）
└── MiniMax-M2/                      # MiniMax M2
    ├── position/
    │   └── position.jsonl
    └── log/
        └── 2025-10-31/
            └── log.jsonl

data/agent_data_astock_hour/         # A股小时级数据
├── deepseek-chat-v3.1-astock-hour/  # DeepSeek V3.2（小时级）
└── MiniMax-M2-astock-hour/          # MiniMax M2（小时级）
```

## 🔌 第三方策略集成

AI-Trader Bench采用模块化设计，支持轻松集成第三方策略和自定义AI代理。

### 🛠️ 集成方式

#### 1. 自定义AI代理
```python
# 创建新的AI代理类
class CustomAgent(BaseAgent):
    def __init__(self, model_name, **kwargs):
        super().__init__(model_name, **kwargs)
        # 添加自定义逻辑
```

#### 2. 注册新代理
```python
# 在 main.py 中注册
AGENT_REGISTRY = {
    "BaseAgentAStock": {
        "module": "agent.base_agent_astock.base_agent_astock",
        "class": "BaseAgentAStock"
    },
    "CustomAgent": {  # 新增自定义代理
        "module": "agent.custom.custom_agent",
        "class": "CustomAgent"
    },
}
```

#### 3. 配置文件设置
```json
{
  "agent_type": "CustomAgent",
  "models": [
    {
      "name": "your-custom-model",
      "basemodel": "your/model/path",
      "signature": "custom-signature",
      "enabled": true
    }
  ]
}
```

### 🔧 扩展工具链

#### 添加自定义工具
```python
# 创建新的MCP工具
@mcp.tools()
class CustomTool:
    def __init__(self):
        self.name = "custom_tool"
    
    def execute(self, params):
        # 实现自定义工具逻辑
        return result
```

## 🚀 项目优化路线图

### 📋 优化计划概览

基于对AI-Trader项目的深度分析，我们制定了全面的系统优化计划，旨在将项目从混合市场系统转型为专业的A股AI交易分析平台。

### 🎯 核心优化目标

- **数据质量提升**：从6.6/10提升至8.5+/10
- **股票池规模扩展**：从50只（上证50）扩展至300-500只
- **AI决策透明度**：实现100%推理过程可视化
- **前端响应性能**：页面加载时间从500ms降至200ms以内

### 📅 实施时间线

| 阶段 | 时间周期 | 主要任务 | 预期成果 | 状态 |
|------|----------|----------|----------|------|
| **Phase 1** | 第1-2周 | 功能范围调整 | 移除美股、加密货币模块，专注A股 | ✅ 已完成 |
| **Phase 2** | 第3-6周 | 股票池扩展 | 支持300+A股，覆盖5大板块 | ⏳ 待开始 |
| **Phase 3** | 第7-10周 | 数据质量提升 | 数据质量达8.5+/10 | ⏳ 待开始 |
| **Phase 4** | 第11-14周 | AI决策可视化 | 完整推理过程展示 | ✅ 已完成 |
| **Phase 5** | 第15-16周 | 前端优化 | 响应性能提升50% | ⏳ 待开始 |
| **Phase 6** | 第17-20周 | 技术含量提升 | 集成ML/RL/NLG技术 | ✅ 已完成 |

### 🔍 详细优化方案

#### Phase 1: 功能范围调整（第1-2周）
**优化内容**：
- ✅ 保留A股核心功能（T+1、涨跌停、100股整数倍规则）
- ✅ 保留国外资讯源（Alpha Vantage News、Jina搜索）
- ✅ 移除美股数据获取和处理
- ✅ 移除加密货币功能
- ✅ 精简AI模型至2个（DeepSeek V3.2 + MiniMax M2）
- ✅ 前端完全中文化，移除市场切换
- ✅ 新增AI思考全过程页面

#### Phase 2: 股票池扩展（第3-6周）
**优化内容**：
- 📈 上证50（50只）- 现有
- 📈 上证180（130只）
- 📈 深证100（100只）
- 📈 创业板指（100只）
- 📈 科创50（50只）
- 🎯 **目标**：总计480只股票

#### Phase 3: 数据质量提升（第7-10周）
**优化内容**：
- 🔍 数据质量监控系统
- ⚡ 并发数据获取优化
- 💾 Redis缓存系统
- ✅ 跨数据源验证
- 📊 价格异常检测

#### Phase 4: AI决策可视化（第11-14周）
**优化内容**：
- ✅ 推理过程结构化存储（JSONL格式）
- ✅ 数据获取→分析→决策→执行全过程可视化
- ✅ AI思考全过程页面（ai-reasoning.html）
- 🎨 前端可视化组件（ai-reasoning.js）
- ✅ 按类型分类展示（market_analysis/decision/trade/research）
- ✅ 可折叠章节设计，优化用户体验
- ✅ 完整时间戳和决策链记录

#### Phase 5: 前端优化（第15-16周）
**优化内容**：
- ⚡ 虚拟滚动优化
- 📦 懒加载组件
- 🔄 请求合并与缓存
- 📈 Chart.js性能优化
- 📱 响应式设计完善

#### Phase 6: 技术含量提升（第17-20周）
**优化内容**：
- ✅ 机器学习预测模型（ml/prediction_model.py）
- ✅ 强化学习交易环境（rl/simplified_trading_env.py）
- ✅ 自然语言交易报告生成（nlg/trading_report_generator.py）
- ✅ 实时监控与告警系统（monitoring/real_time_monitor.py）
- ✅ 高级技术指标分析（ml/simplified_technical_indicators.py）

### 💰 资源需求

| 角色 | 人数 | 投入时间 | 薪资预算（月） |
|------|------|----------|----------------|
| 后端工程师 | 2 | 5个月 | 20-30K × 2 |
| 前端工程师 | 2 | 3个月 | 18-25K × 2 |
| AI工程师 | 1 | 3个月 | 25-35K × 1 |
| DevOps工程师 | 1 | 2个月 | 20-30K × 1 |

**总人力成本：约60-80万**

### 📊 成功指标与验收标准

- ✅ **股票池规模**：支持300+只A股，覆盖5大板块
- ✅ **数据质量评分**：达到8.5/10以上
- ✅ **AI推理可视化**：100%推理过程可追溯
- ✅ **前端响应性能**：页面加载时间<200ms
- ✅ **数据钻取深度**：支持4级钻取（市场→行业→个股→决策）

### 🌟 长期演进路线图

```
已优化状态 → 股票池扩展 → 数据质量提升 → 前端优化 → 股票池扩展 → 平台化
    ↓           ↓           ↓           ↓          ↓         ↓
   纯A股系统   →  300+股票  →  8.5分+   →  性能优化  →  500+股票  → SaaS服务
   2个AI模型
   完全可视化
```

---

### 🌟 未来计划
- [x] **🇨🇳 A股支持** - ✅ 上证50指数数据集成已完成
- [x] **🧠 AI思考全过程** - ✅ 完整推理过程可视化已完成
- [x] **🎨 现代化前端** - ✅ 响应式Web仪表板已完成
- [ ] **📊 收盘后统计** - 自动收益分析
- [ ] **🔌 策略市场** - 添加第三方策略分享平台
- [ ] **📈 更多策略** - 技术分析、量化策略
- [ ] **📈 股票池扩展** - 支持300+A股（上证180、深证100、创业板100、科创50）
- [ ] **⏰ 高级回放** - 支持分钟级时间精度和实时回放
- [ ] **🔍 智能过滤** - 更精确的未来信息检测和过滤


## 📞 支持与社区

- **💬 讨论**: [GitHub Discussions](https://github.com/HKUDS/AI-Trader/discussions)
- **🐛 问题**: [GitHub Issues](https://github.com/HKUDS/AI-Trader/issues)

## 📄 许可证

本项目采用 [MIT License](LICENSE) 开源协议。

## 🙏 致谢

感谢以下开源项目和服务：
- [LangChain](https://github.com/langchain-ai/langchain) - AI应用开发框架
- [MCP](https://github.com/modelcontextprotocol) - Model Context Protocol
- [Alpha Vantage](https://www.alphavantage.co/) - 美股金融数据API
- [Tushare](https://tushare.pro/) - A股市场数据API
- [efinance](https://github.com/Micro-sheep/efinance) - A股小时级数据获取
- [Jina AI](https://jina.ai/) - 信息搜索服务

## 👥 管理员

<div align="center">

<a href="https://github.com/TianyuFan0504">
  <img src="https://avatars.githubusercontent.com/TianyuFan0504?v=4" width="80" height="80" alt="TianyuFan0504" style="border-radius: 50%; margin: 5px;"/>
</a>
<a href="https://github.com/yangqin-jiang">
  <img src="https://avatars.githubusercontent.com/yangqin-jiang?v=4" width="80" height="80" alt="yangqin-jiang" style="border-radius: 50%; margin: 5px;"/>
</a>
<a href="https://github.com/yuh-yang">
  <img src="https://avatars.githubusercontent.com/yuh-yang?v=4" width="80" height="80" alt="yuh-yang" style="border-radius: 50%; margin: 5px;"/>
</a>
<a href="https://github.com/Hoder-zyf">
  <img src="https://avatars.githubusercontent.com/Hoder-zyf?v=4" width="80" height="80" alt="Hoder-zyf" style="border-radius: 50%; margin: 5px;"/>
</a>

</div>

## 🤝 贡献

<div align="center">
  我们感谢所有贡献者的宝贵贡献。
</div>

<div align="center">
  <a href="https://github.com/HKUDS/AI-Trader/graphs/contributors">
    <img src="https://contrib.rocks/image?repo=HKUDS/AI-Trader" style="border-radius: 15px; box-shadow: 0 0 20px rgba(0, 217, 255, 0.3);" />
  </a>
</div>

## 免责声明

AI-Trader项目所提供的资料仅供研究之用，并不构成任何投资建议。投资者在作出任何投资决策之前，应寻求独立专业意见。任何过往表现未必可作为未来业绩的指标。阁下应注意，投资价值可能上升亦可能下跌，且并无任何保证。AI-Trader项目的所有内容仅作研究之用，并不构成对所提及之证券／行业的任何投资推荐。投资涉及风险。如有需要，请寻求专业咨询。

---

<div align="center">

**🌟 如果这个项目对你有帮助，请给我们一个Star！**

[![GitHub stars](https://img.shields.io/github/stars/HKUDS/AI-Trader?style=social)](https://github.com/HKUDS/AI-Trader)
[![GitHub forks](https://img.shields.io/github/forks/HKUDS/AI-Trader?style=social)](https://github.com/HKUDS/AI-Trader)

**🤖 让AI在金融市场中完全自主决策、一展身手！**  
**🛠️ 纯工具驱动，零人工干预，真正的AI交易竞技场！** 🚀

</div>

---

## ⭐ Star 历史

*社区增长轨迹*

<div align="center">
  <a href="https://star-history.com/#HKUDS/AI-Trader&Date">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=HKUDS/AI-Trader&type=Date&theme=dark" />
      <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=HKUDS/AI-Trader&type=Date" />
      <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=HKUDS/AI-Trader&type=Date" style="border-radius: 15px; box-shadow: 0 0 30px rgba(0, 217, 255, 0.3);" />
    </picture>
  </a>
</div>

---

<p align="center">
  <em> ❤️ 感谢访问 ✨ AI-Trader!</em><br><br>
  <img src="https://visitor-badge.laobi.icu/badge?page_id=HKUDS.AI-Trader&style=for-the-badge&color=00d4ff" alt="Views">
</p>
