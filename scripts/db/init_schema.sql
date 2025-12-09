-- AI-Trader PostgreSQL 数据库初始化脚本
-- 版本: PostgreSQL 17 + TimescaleDB
-- 创建时间: 2025-12-10

-- 创建TimescaleDB扩展
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- 创建枚举类型
CREATE TYPE trade_action_type AS ENUM ('buy', 'sell', 'hold');
CREATE TYPE log_type_enum AS ENUM ('market_analysis', 'decision', 'trade', 'research');

-- 1. 股票价格表（核心表，使用TimescaleDB超表）
CREATE TABLE stock_prices (
    id BIGSERIAL,
    symbol VARCHAR(20) NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    open_price NUMERIC(12,4) NOT NULL,
    high_price NUMERIC(12,4) NOT NULL,
    low_price NUMERIC(12,4) NOT NULL,
    close_price NUMERIC(12,4) NOT NULL,
    volume BIGINT DEFAULT 0,
    turnover NUMERIC(20,2) DEFAULT 0,
    change_pct NUMERIC(8,4) DEFAULT 0,
    meta_data JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (symbol, timestamp)
);

-- 创建超表（自动按时间分区）
SELECT create_hypertable('stock_prices', 'timestamp', if_not_exists => TRUE);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_stock_prices_symbol ON stock_prices(symbol);
CREATE INDEX IF NOT EXISTS idx_stock_prices_timestamp ON stock_prices(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_stock_prices_symbol_timestamp ON stock_prices(symbol, timestamp DESC);

-- 2. 持仓历史表
CREATE TABLE position_history (
    id BIGSERIAL PRIMARY KEY,
    agent_name VARCHAR(100) NOT NULL,
    trade_date DATE NOT NULL,
    trade_time TIMESTAMPTZ,
    action trade_action_type NOT NULL,
    symbol VARCHAR(20),
    amount INTEGER DEFAULT 0,
    price NUMERIC(12,4) DEFAULT 0,
    cash NUMERIC(14,2) NOT NULL,
    total_value NUMERIC(14,2) NOT NULL,
    positions JSONB NOT NULL,
    reasoning TEXT,
    meta_data JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_position_agent ON position_history(agent_name);
CREATE INDEX IF NOT EXISTS idx_position_date ON position_history(trade_date DESC);
CREATE INDEX IF NOT EXISTS idx_position_agent_date ON position_history(agent_name, trade_date DESC);

-- 3. AI推理日志表
CREATE TABLE trade_logs (
    id BIGSERIAL PRIMARY KEY,
    agent_name VARCHAR(100) NOT NULL,
    log_timestamp TIMESTAMPTZ NOT NULL,
    log_date DATE NOT NULL,
    log_type log_type_enum NOT NULL,
    summary TEXT,
    content JSONB NOT NULL,
    tokens_used INTEGER DEFAULT 0,
    processing_time_ms INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_logs_agent ON trade_logs(agent_name);
CREATE INDEX IF NOT EXISTS idx_logs_timestamp ON trade_logs(log_timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_logs_type ON trade_logs(log_type);
CREATE INDEX IF NOT EXISTS idx_logs_agent_timestamp ON trade_logs(agent_name, log_timestamp DESC);

-- 4. 用户表（配合登录功能）
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(100),
    full_name VARCHAR(100),
    role VARCHAR(20) DEFAULT 'user',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_login TIMESTAMPTZ,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- 5. 股票池配置表
CREATE TABLE stock_pools (
    id BIGSERIAL PRIMARY KEY,
    pool_name VARCHAR(50) NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    stock_name VARCHAR(100),
    market VARCHAR(10) DEFAULT 'CN',
    weight NUMERIC(5,4) DEFAULT 1.0000,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(pool_name, symbol)
);

CREATE INDEX IF NOT EXISTS idx_stock_pools_name ON stock_pools(pool_name);
CREATE索引 IF NOT EXISTS idx_stock_pools_symbol ON stock_pools(symbol);

-- 6. 基准指数表
CREATE TABLE benchmark_indices (
    id BIGSERIAL PRIMARY KEY,
    index_code VARCHAR(20) UNIQUE NOT NULL,
    index_name VARCHAR(100) NOT NULL,
    market VARCHAR(10) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_benchmark_code ON benchmark_indices(index_code);
CREATE INDEX IF NOT EXISTS idx_benchmark_market ON benchmark_indices(market);

-- 7. 指数价格表（基准指数历史数据）
CREATE TABLE index_prices (
    id BIGSERIAL,
    index_code VARCHAR(20) NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    open_price NUMERIC(12,4),
    high_price NUMERIC(12,4),
    low_price NUMERIC(12,4),
    close_price NUMERIC(12,4) NOT NULL,
    volume BIGINT DEFAULT 0,
    change_pct NUMERIC(8,4) DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (index_code, timestamp)
);

-- 创建超表
SELECT create_hypertable('index_prices', 'timestamp', if_not_exists => TRUE);

CREATE INDEX IF NOT EXISTS idx_index_prices_code ON index_prices(index_code);
CREATE INDEX IF NOT EXISTS idx_index_prices_timestamp ON index_prices(timestamp DESC);

-- 创建视图：当前持仓快照
CREATE OR REPLACE VIEW current_positions AS
SELECT DISTINCT ON (agent_name, symbol)
    agent_name,
    symbol,
    positions->symbol->>'amount' as amount,
    positions->symbol->>'avg_price' as avg_price,
    positions->symbol->>'market_value' as market_value,
    cash,
    total_value,
    trade_date
FROM position_history
ORDER BY agent_name, symbol, trade_date DESC;

-- 创建视图：代理性能统计
CREATE OR REPLACE VIEW agent_performance AS
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
ORDER BY total_return_pct DESC;

-- 创建连续聚合视图：周线数据
CREATE MATERIALIZED VIEW weekly_stock_prices
WITH (timescaledb.continuous) AS
SELECT
    symbol,
    time_bucket('1 week', timestamp) AS week,
    first(open_price, timestamp) AS open_price,
    max(high_price) AS high_price,
    min(low_price) AS low_price,
    last(close_price, timestamp) AS close_price,
    sum(volume) AS volume,
    avg(close_price) AS avg_price
FROM stock_prices
GROUP BY symbol, week
ORDER BY symbol, week;

CREATE INDEX IF NOT EXISTS idx_weekly_stock_symbol ON weekly_stock_prices(symbol);
CREATE INDEX IF NOT EXISTS idx_weekly_stock_week ON weekly_stock_prices(week DESC);

-- 创建连续聚合视图：月线数据
CREATE MATERIALIZED VIEW monthly_stock_prices
WITH (timescaledb.continuous) AS
SELECT
    symbol,
    time_bucket('1 month', timestamp) AS month,
    first(open_price, timestamp) AS open_price,
    max(high_price) AS high_price,
    min(low_price) AS low_price,
    last(close_price, timestamp) AS close_price,
    sum(volume) AS volume,
    avg(close_price) AS avg_price
FROM stock_prices
GROUP BY symbol, month
ORDER BY symbol, month;

CREATE INDEX IF NOT EXISTS idx_monthly_stock_symbol ON monthly_stock_prices(symbol);
CREATE INDEX IF NOT EXISTS idx_monthly_stock_month ON monthly_stock_prices(month DESC);

-- 创建连续聚合视图：指数周线
CREATE MATERIALIZED VIEW weekly_index_prices
WITH (timescaledb.continuous) AS
SELECT
    index_code,
    time_bucket('1 week', timestamp) AS week,
    first(open_price, timestamp) AS open_price,
    max(high_price) AS high_price,
    min(low_price) AS low_price,
    last(close_price, timestamp) AS close_price,
    sum(volume) AS volume
FROM index_prices
GROUP BY index_code, week
ORDER BY index_code, week;

-- 创建连续聚合视图：指数月线
CREATE MATERIALIZED VIEW monthly_index_prices
WITH (timescaledb.continuous) AS
SELECT
    index_code,
    time_bucket('1 month', timestamp) AS month,
    first(open_price, timestamp) AS open_price,
    max(high_price) AS high_price,
    min(low_price) AS low_price,
    last(close_price, timestamp) AS close_price,
    sum(volume) AS volume
FROM index_prices
GROUP BY index_code, month
ORDER BY index_code, month;

-- 插入默认基准指数数据
INSERT INTO benchmark_indices (index_code, index_name, market, description) VALUES
('000001.SH', '上证指数', 'CN', '上海证券交易所综合指数'),
('000016.SH', '上证50', 'CN', '上海证券交易所50只最具代表性股票'),
('000300.SH', '沪深300', 'CN', '沪深300指数'),
('399001.SZ', '深证成指', 'CN', '深圳成份股价指数'),
('399006.SZ', '创业板指', 'CN', '创业板指数'),
('000688.SH', '科创50', 'CN', '科创板50指数'),
('899050.BJ', '北证50', 'CN', '北京证券交易所50指数')
ON CONFLICT (index_code) DO NOTHING;

-- 插入默认股票池数据（上证50）
INSERT INTO stock_pools (pool_name, symbol, stock_name, market, weight) VALUES
('SSE50', '600000.SH', '浦发银行', 'CN', 0.0200),
('SSE50', '600036.SH', '招商银行', 'CN', 0.0200),
('SSE50', '600519.SH', '贵州茅台', 'CN', 0.0200),
('SSE50', '600887.SH', '伊利股份', 'CN', 0.0200),
('SSE50', '601318.SH', '中国平安', 'CN', 0.0200),
('SSE50', '601398.SH', '工商银行', 'CN', 0.0200),
('SSE50', '601857.SH', '中国石油', 'CN', 0.0200),
('SSE50', '601988.SH', '中国银行', 'CN', 0.0200)
ON CONFLICT (pool_name, symbol) DO NOTHING;

-- 创建函数：计算累计收益
CREATE OR REPLACE FUNCTION calculate_cumulative_returns(agent_name_param VARCHAR)
RETURNS TABLE (
    trade_date DATE,
    total_value NUMERIC,
    cumulative_return NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        ph.trade_date,
        ph.total_value,
        ((ph.total_value - initial_cash) / initial_cash * 100) as cumulative_return
    FROM position_history ph
    CROSS JOIN (
        SELECT MIN(total_value) as initial_cash
        FROM position_history
        WHERE agent_name = agent_name_param
    ) init
    WHERE ph.agent_name = agent_name_param
    ORDER BY ph.trade_date;
END;
$$ LANGUAGE plpgsql;

-- 创建触发器：自动更新updated_at字段
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_stock_pools_updated_at
    BEFORE UPDATE ON stock_pools
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_benchmark_indices_updated_at
    BEFORE UPDATE ON benchmark_indices
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- 设置压缩策略（TimescaleDB）
-- 压缩超过7天的数据
SELECT add_compression_policy('stock_prices', INTERVAL '7 days');
SELECT add_compression_policy('index_prices', INTERVAL '7 days');

-- 设置数据保留策略（保留2年数据）
SELECT add_retention_policy('stock_prices', INTERVAL '2 years');
SELECT add_retention_policy('position_history', INTERVAL '2 years');
SELECT add_retention_policy('trade_logs', INTERVAL '2 years');
SELECT add_retention_policy('index_prices', INTERVAL '2 years');

-- 刷新连续聚合视图
SELECT refresh_continuous_aggregate('weekly_stock_prices', NOW() - INTERVAL '1 year', NOW());
SELECT refresh_continuous_aggregate('monthly_stock_prices', NOW() - INTERVAL '2 years', NOW());
SELECT refresh_continuous_aggregate('weekly_index_prices', NOW() - INTERVAL '1 year', NOW());
SELECT refresh_continuous_aggregate('monthly_index_prices', NOW() - INTERVAL '2 years', NOW());

-- 授予权限（根据需要调整）
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;

-- 显示创建结果
SELECT 'Database schema initialized successfully!' as message;
SELECT 'Tables created: ' || count(*) as table_count
FROM information_schema.tables
WHERE table_schema = 'public' AND table_type = 'BASE TABLE';

SELECT 'Hypertables created: ' || count(*) as hypertable_count
FROM timescaledb.hypertable;

SELECT 'Continuous aggregates created: ' || count(*) as ca_count
FROM timescaledb.continuous_aggregate;
