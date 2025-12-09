/**
 * 数据钻取组件
 * 支持多层级数据钻取：市场 → 行业 → 个股 → 决策详情
 */

class DataDrillDown {
    constructor(containerId = 'data-drilldown') {
        this.container = document.getElementById(containerId);
        this.currentLevel = 0;
        this.currentData = null;
        this.drillDownLevels = [
            { name: 'market', label: '市场概览', icon: '📊' },
            { name: 'sector', label: '行业分析', icon: '📈' },
            { name: 'stock', label: '个股详情', icon: '💹' },
            { name: 'decision', label: '决策详情', icon: '🧠' }
        ];

        this.dataCache = new Map();
        this.init();
    }

    init() {
        if (!this.container) {
            console.error('DataDrillDown: Container not found');
            return;
        }

        this.createUI();
        this.attachEventListeners();
        this.loadMarketOverview();
    }

    createUI() {
        this.container.innerHTML = `
            <div class="data-drilldown-container">
                <!-- 导航面包屑 -->
                <nav class="breadcrumb-nav">
                    <ol class="breadcrumb">
                        <li class="breadcrumb-item">
                            <button class="breadcrumb-btn" data-level="0">
                                <span class="breadcrumb-icon">🏠</span>
                                <span class="breadcrumb-text">市场</span>
                            </button>
                        </li>
                        <li class="breadcrumb-item">
                            <button class="breadcrumb-btn" data-level="1" disabled>
                                <span class="breadcrumb-icon">📈</span>
                                <span class="breadcrumb-text">行业</span>
                            </button>
                        </li>
                        <li class="breadcrumb-item">
                            <button class="breadcrumb-btn" data-level="2" disabled>
                                <span class="breadcrumb-icon">💹</span>
                                <span class="breadcrumb-text">个股</span>
                            </button>
                        </li>
                        <li class="breadcrumb-item">
                            <button class="breadcrumb-btn" data-level="3" disabled>
                                <span class="breadcrumb-icon">🧠</span>
                                <span class="breadcrumb-text">决策</span>
                            </button>
                        </li>
                    </ol>
                </nav>

                <!-- 内容区域 -->
                <div class="drilldown-content" id="drilldown-content">
                    <!-- 动态内容 -->
                </div>

                <!-- 返回按钮 -->
                <button class="back-btn" id="back-btn" disabled>
                    <span class="back-icon">←</span>
                    <span class="back-text">返回上级</span>
                </button>
            </div>
        `;

        this.injectStyles();
    }

    injectStyles() {
        if (document.getElementById('data-drilldown-styles')) return;

        const styles = `
            <style id="data-drilldown-styles">
                .data-drilldown-container {
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    padding: 20px;
                    background: #f5f5f5;
                    min-height: 100vh;
                }

                .breadcrumb-nav {
                    margin-bottom: 20px;
                }

                .breadcrumb {
                    display: flex;
                    list-style: none;
                    padding: 0;
                    margin: 0;
                    background: white;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    overflow: hidden;
                }

                .breadcrumb-item {
                    position: relative;
                }

                .breadcrumb-item:not(:last-child)::after {
                    content: '›';
                    position: absolute;
                    right: 0;
                    top: 50%;
                    transform: translateY(-50%);
                    color: #ccc;
                    font-size: 20px;
                    z-index: 1;
                }

                .breadcrumb-btn {
                    display: flex;
                    align-items: center;
                    gap: 8px;
                    padding: 15px 25px;
                    border: none;
                    background: none;
                    cursor: pointer;
                    font-size: 14px;
                    color: #666;
                    transition: all 0.3s;
                }

                .breadcrumb-btn:hover:not(:disabled) {
                    background: #f0f0f0;
                    color: #2196F3;
                }

                .breadcrumb-btn:disabled {
                    cursor: not-allowed;
                    opacity: 0.5;
                }

                .breadcrumb-btn.active {
                    background: #2196F3;
                    color: white;
                }

                .breadcrumb-icon {
                    font-size: 18px;
                }

                .drilldown-content {
                    background: white;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    padding: 30px;
                    min-height: 500px;
                }

                .back-btn {
                    margin-top: 20px;
                    padding: 12px 24px;
                    border: none;
                    border-radius: 6px;
                    background: #2196F3;
                    color: white;
                    cursor: pointer;
                    display: flex;
                    align-items: center;
                    gap: 8px;
                    font-size: 14px;
                    transition: all 0.3s;
                }

                .back-btn:hover:not(:disabled) {
                    background: #1976D2;
                    transform: translateX(-5px);
                }

                .back-btn:disabled {
                    background: #ccc;
                    cursor: not-allowed;
                    transform: none;
                }

                .overview-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                    gap: 20px;
                    margin-bottom: 30px;
                }

                .metric-card {
                    padding: 20px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    border-radius: 8px;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                }

                .metric-card h3 {
                    margin: 0 0 10px 0;
                    font-size: 14px;
                    opacity: 0.9;
                }

                .metric-value {
                    font-size: 32px;
                    font-weight: 700;
                    margin-bottom: 5px;
                }

                .metric-trend {
                    font-size: 14px;
                    opacity: 0.8;
                }

                .metric-trend.up::before {
                    content: '↑ ';
                }

                .metric-trend.down::before {
                    content: '↓ ';
                }

                .sector-breakdown {
                    background: #f9f9f9;
                    padding: 20px;
                    border-radius: 8px;
                }

                .sector-breakdown h3 {
                    margin: 0 0 15px 0;
                }

                .sector-list {
                    display: grid;
                    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
                    gap: 15px;
                }

                .sector-item {
                    padding: 15px;
                    background: white;
                    border-radius: 6px;
                    cursor: pointer;
                    transition: all 0.3s;
                    border: 2px solid transparent;
                }

                .sector-item:hover {
                    border-color: #2196F3;
                    transform: translateY(-2px);
                    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                }

                .sector-name {
                    font-weight: 600;
                    margin-bottom: 8px;
                }

                .sector-metrics {
                    font-size: 14px;
                    color: #666;
                }

                .sector-change {
                    font-weight: 600;
                    margin-top: 5px;
                }

                .sector-change.up {
                    color: #4CAF50;
                }

                .sector-change.down {
                    color: #f44336;
                }

                .sector-analysis {
                    padding: 20px;
                }

                .sector: flex;
                   -header {
                    display justify-content: space-between;
                    align-items: center;
                    margin-bottom: 30px;
                    padding-bottom: 20px;
                    border-bottom: 2px solid #e0e0e0;
                }

                .sector-header h2 {
                    margin: 0;
                    display: flex;
                    align-items: center;
                    gap: 10px;
                }

                .sector-metrics {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 20px;
                    margin-bottom: 30px;
                }

                .metric {
                    padding: 20px;
                    background: #f9f9f9;
                    border-radius: 8px;
                }

                .metric label {
                    display: block;
                    font-size: 14px;
                    color: #666;
                    margin-bottom: 8px;
                }

                .metric value {
                    display: block;
                    font-size: 24px;
                    font-weight: 600;
                    color: #333;
                }

                .sector-stocks {
                    background: #f9f9f9;
                    padding: 20px;
                    border-radius: 8px;
                }

                .sector-stocks h3 {
                    margin: 0 0 15px 0;
                }

                .stocks-table {
                    width: 100%;
                    border-collapse: collapse;
                    background: white;
                    border-radius: 8px;
                    overflow: hidden;
                }

                .stocks-table thead {
                    background: #2196F3;
                    color: white;
                }

                .stocks-table th,
                .stocks-table td {
                    padding: 12px;
                    text-align: left;
                }

                .stocks-table tbody tr {
                    border-bottom: 1px solid #e0e0e0;
                    cursor: pointer;
                    transition: background 0.3s;
                }

                .stocks-table tbody tr:hover {
                    background: #f0f0f0;
                }

                .stocks-table td.up {
                    color: #4CAF50;
                    font-weight: 600;
                }

                .stocks-table td.down {
                    color: #f44336;
                    font-weight: 600;
                }

                .stock-analysis {
                    padding: 20px;
                }

                .stock-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 30px;
                    padding-bottom: 20px;
                    border-bottom: 2px solid #e0e0e0;
                }

                .stock-header h2 {
                    margin: 0;
                }

                .stock-chart {
                    margin-bottom: 30px;
                    height: 300px;
                    background: #f9f9f9;
                    border-radius: 8px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: #999;
                }

                .stock-details {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                    gap: 20px;
                }

                .detail-section {
                    background: #f9f9f9;
                    padding: 20px;
                    border-radius: 8px;
                }

                .detail-section h3 {
                    margin: 0 0 15px 0;
                }

                .info-grid {
                    display: grid;
                    gap: 10px;
                }

                .info-item {
                    display: flex;
                    justify-content: space-between;
                    padding: 10px;
                    background: white;
                    border-radius: 4px;
                }

                .info-item label {
                    font-weight: 600;
                    color: #666;
                }

                .info-item value {
                    color: #333;
                }

                .info-item value.up {
                    color: #4CAF50;
                }

                .info-item value.down {
                    color: #f44336;
                }

                .ai-holdings {
                    display: grid;
                    gap: 10px;
                }

                .holding-card {
                    padding: 15px;
                    background: white;
                    border-radius: 6px;
                    border-left: 4px solid #2196F3;
                }

                .holding-card-header {
                    display: flex;
                    justify-content: space-between;
                    margin-bottom: 10px;
                }

                .agent-name {
                    font-weight: 600;
                    color: #2196F3;
                }

                .holding-pnl {
                    font-weight: 600;
                }

                .holding-pnl.up {
                    color: #4CAF50;
                }

                .holding-pnl.down {
                    color: #f44336;
                }

                .holding-details {
                    font-size: 14px;
                    color: #666;
                }

                .drill-down-btn {
                    margin-top: 20px;
                    padding: 12px 24px;
                    border: 2px solid #2196F3;
                    border-radius: 6px;
                    background: white;
                    color: #2196F3;
                    cursor: pointer;
                    font-size: 14px;
                    font-weight: 600;
                    transition: all 0.3s;
                    display: flex;
                    align-items: center;
                    gap: 8px;
                }

                .drill-down-btn:hover {
                    background: #2196F3;
                    color: white;
                }

                .decision-analysis {
                    padding: 20px;
                }

                .decision-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 30px;
                    padding-bottom: 20px;
                    border-bottom: 2px solid #e0e0e0;
                }

                .decision-header h2 {
                    margin: 0;
                }

                .decision-timeline {
                    position: relative;
                    padding-left: 40px;
                }

                .decision-timeline::before {
                    content: '';
                    position: absolute;
                    left: 15px;
                    top: 0;
                    bottom: 0;
                    width: 3px;
                    background: linear-gradient(180deg, #4CAF50, #2196F3, #9C27B0);
                }

                .decision-step {
                    position: relative;
                    margin-bottom: 30px;
                    padding: 20px;
                    background: #f9f9f9;
                    border-radius: 8px;
                }

                .decision-step::before {
                    content: '';
                    position: absolute;
                    left: -32px;
                    top: 25px;
                    width: 15px;
                    height: 15px;
                    background: #2196F3;
                    border-radius: 50%;
                }

                .step-time {
                    font-size: 12px;
                    color: #999;
                    margin-bottom: 8px;
                }

                .step-type {
                    font-weight: 600;
                    color: #2196F3;
                    margin-bottom: 8px;
                }

                .step-description {
                    color: #666;
                    line-height: 1.6;
                }

                .step-details {
                    margin-top: 10px;
                    padding: 10px;
                    background: white;
                    border-radius: 4px;
                    font-family: monospace;
                    font-size: 13px;
                }

                .loading {
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    min-height: 300px;
                    color: #999;
                }

                .spinner {
                    border: 3px solid #f3f3f3;
                    border-top: 3px solid #2196F3;
                    border-radius: 50%;
                    width: 40px;
                    height: 40px;
                    animation: spin 1s linear infinite;
                    margin-right: 15px;
                }

                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
            </style>
        `;

        document.head.insertAdjacentHTML('beforeend', styles);
    }

    attachEventListeners() {
        // 面包屑导航
        document.querySelectorAll('.breadcrumb-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const level = parseInt(e.currentTarget.dataset.level);
                if (!e.currentTarget.disabled) {
                    this.goToLevel(level);
                }
            });
        });

        // 返回按钮
        const backBtn = document.getElementById('back-btn');
        if (backBtn) {
            backBtn.addEventListener('click', () => this.goBack());
        }
    }

    async loadMarketOverview() {
        this.showLoading();
        await this.delay(500); // 模拟加载

        const data = await this.fetchMarketData();
        this.currentData = data;
        this.renderMarketOverview(data);
        this.updateNavigation(0);
    }

    renderMarketOverview(data) {
        const content = document.getElementById('drilldown-content');
        if (!content) return;

        content.innerHTML = `
            <div class="overview-grid">
                <div class="metric-card">
                    <h3>上证指数</h3>
                    <div class="metric-value">${data.index_value}</div>
                    <div class="metric-trend ${data.index_change > 0 ? 'up' : 'down'}">
                        ${data.index_change > 0 ? '+' : ''}${data.index_change}%
                    </div>
                </div>
                <div class="metric-card">
                    <h3>成交量</h3>
                    <div class="metric-value">${data.volume}</div>
                    <div class="metric-trend up">较昨日 +15%</div>
                </div>
                <div class="metric-card">
                    <h3>上涨家数</h3>
                    <div class="metric-value">${data.up_count}</div>
                    <div class="metric-trend up">占比 ${data.up_ratio}%</div>
                </div>
                <div class="metric-card">
                    <h3>下跌家数</h3>
                    <div class="metric-value">${data.down_count}</div>
                    <div class="metric-trend down">占比 ${data.down_ratio}%</div>
                </div>
            </div>

            <div class="sector-breakdown">
                <h3>行业分布</h3>
                <div class="sector-list">
                    ${data.sectors.map(sector => `
                        <div class="sector-item" onclick="dataDrillDown.drillToSector('${sector.name}')">
                            <div class="sector-name">${sector.name}</div>
                            <div class="sector-metrics">
                                <div>股票数: ${sector.stock_count}</div>
                                <div>平均涨跌幅: ${sector.avg_change}%</div>
                            </div>
                            <div class="sector-change ${sector.change > 0 ? 'up' : 'down'}">
                                ${sector.change > 0 ? '+' : ''}${sector.change}%
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    async drillToSector(sectorName) {
        this.showLoading();
        await this.delay(500);

        const data = await this.fetchSectorData(sectorName);
        this.currentData = { ...data, sectorName };
        this.renderSectorAnalysis(data);
        this.updateNavigation(1);
    }

    renderSectorAnalysis(data) {
        const content = document.getElementById('drilldown-content');
        if (!content) return;

        content.innerHTML = `
            <div class="sector-analysis">
                <div class="sector-header">
                    <h2>
                        <span>📈</span>
                        ${data.name}
                    </h2>
                    <button class="drill-down-btn" onclick="dataDrillDown.loadMarketOverview()">
                        <span>←</span>
                        返回市场
                    </button>
                </div>

                <div class="sector-metrics">
                    <div class="metric">
                        <label>平均涨跌幅</label>
                        <value>${data.avg_change}%</value>
                    </div>
                    <div class="metric">
                        <label>领涨股</label>
                        <value>${data.leading_stock}</value>
                    </div>
                    <div class="metric">
                        <label>股票总数</label>
                        <value>${data.stock_count}</value>
                    </div>
                    <div class="metric">
                        <label>成交额</label>
                        <value>${data.turnover}</value>
                    </div>
                </div>

                <div class="sector-stocks">
                    <h3>成分股</h3>
                    <table class="stocks-table">
                        <thead>
                            <tr>
                                <th>股票</th>
                                <th>价格</th>
                                <th>涨跌幅</th>
                                <th>成交量</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${data.stocks.map(stock => `
                                <tr onclick="dataDrillDown.drillToStock('${stock.code}')">
                                    <td>${stock.name}</td>
                                    <td>¥${stock.price}</td>
                                    <td class="${stock.change > 0 ? 'up' : 'down'}">
                                        ${stock.change > 0 ? '+' : ''}${stock.change}%
                                    </td>
                                    <td>${stock.volume}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
        `;
    }

    async drillToStock(stockCode) {
        this.showLoading();
        await this.delay(500);

        const data = await this.fetchStockData(stockCode);
        this.currentData = { ...data, stockCode };
        this.renderStockAnalysis(data);
        this.updateNavigation(2);
    }

    renderStockAnalysis(data) {
        const content = document.getElementById('drilldown-content');
        if (!content) return;

        content.innerHTML = `
            <div class="stock-analysis">
                <div class="stock-header">
                    <h2>${data.name} (${data.code})</h2>
                    <button class="drill-down-btn" onclick="dataDrillDown.goBack()">
                        <span>←</span>
                        返回行业
                    </button>
                </div>

                <div class="stock-chart">
                    <canvas id="stock-price-chart"></canvas>
                </div>

                <div class="stock-details">
                    <div class="detail-section">
                        <h3>基本信息</h3>
                        <div class="info-grid">
                            <div class="info-item">
                                <label>当前价格</label>
                                <value>¥${data.price}</value>
                            </div>
                            <div class="info-item">
                                <label>涨跌幅</label>
                                <value class="${data.change > 0 ? 'up' : 'down'}">
                                    ${data.change > 0 ? '+' : ''}${data.change}%
                                </value>
                            </div>
                            <div class="info-item">
                                <label>成交量</label>
                                <value>${data.volume}</value>
                            </div>
                            <div class="info-item">
                                <label>市值</label>
                                <value>${data.market_cap}</value>
                            </div>
                        </div>
                    </div>

                    <div class="detail-section">
                        <h3>AI持仓</h3>
                        <div class="ai-holdings">
                            ${data.ai_holdings.map(holding => `
                                <div class="holding-card">
                                    <div class="holding-card-header">
                                        <span class="agent-name">${holding.agent}</span>
                                        <span class="holding-pnl ${holding.pnl > 0 ? 'up' : 'down'}">
                                            ${holding.pnl > 0 ? '+' : ''}¥${holding.pnl}
                                        </span>
                                    </div>
                                    <div class="holding-details">
                                        <div>持仓: ${holding.amount}股</div>
                                        <div>成本: ¥${holding.cost}</div>
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                </div>

                <button class="drill-down-btn" onclick="dataDrillDown.drillToDecision('${data.code}')">
                    查看AI决策过程 →
                </button>
            </div>
        `;
    }

    async drillToDecision(stockCode) {
        this.showLoading();
        await this.delay(500);

        const data = await this.fetchDecisionData(stockCode);
        this.currentData = { ...data, stockCode };
        this.renderDecisionAnalysis(data);
        this.updateNavigation(3);
    }

    renderDecisionAnalysis(data) {
        const content = document.getElementById('drilldown-content');
        if (!content) return;

        content.innerHTML = `
            <div class="decision-analysis">
                <div class="decision-header">
                    <h2>AI决策分析: ${data.stockCode}</h2>
                    <button class="drill-down-btn" onclick="dataDrillDown.goBack()">
                        <span>←</span>
                        返回个股
                    </button>
                </div>

                <div class="decision-timeline">
                    ${data.timeline.map(step => `
                        <div class="decision-step">
                            <div class="step-time">${step.timestamp}</div>
                            <div class="step-type">${step.type}</div>
                            <div class="step-description">${step.description}</div>
                            ${step.details ? `<div class="step-details">${step.details}</div>` : ''}
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    updateNavigation(level) {
        this.currentLevel = level;

        // 更新面包屑
        document.querySelectorAll('.breadcrumb-btn').forEach((btn, index) => {
            btn.disabled = index > level;
            btn.classList.toggle('active', index === level);
        });

        // 更新返回按钮
        const backBtn = document.getElementById('back-btn');
        backBtn.disabled = level === 0;
    }

    goToLevel(level) {
        switch (level) {
            case 0:
                this.loadMarketOverview();
                break;
            case 1:
                if (this.currentData?.sectorName) {
                    this.drillToSector(this.currentData.sectorName);
                }
                break;
            case 2:
                if (this.currentData?.stockCode) {
                    this.drillToStock(this.currentData.stockCode);
                }
                break;
            case 3:
                if (this.currentData?.stockCode) {
                    this.drillToDecision(this.currentData.stockCode);
                }
                break;
        }
    }

    goBack() {
        if (this.currentLevel > 0) {
            this.goToLevel(this.currentLevel - 1);
        }
    }

    showLoading() {
        const content = document.getElementById('drilldown-content');
        if (content) {
            content.innerHTML = `
                <div class="loading">
                    <div class="spinner"></div>
                    <span>加载中...</span>
                </div>
            `;
        }
    }

    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    // API调用方法（实际使用时替换为真实API）
    async fetchMarketData() {
        // 模拟API调用
        return {
            index_value: '3,245.67',
            index_change: 1.23,
            volume: '¥1,250亿',
            up_count: 2847,
            down_count: 1853,
            up_ratio: 60.5,
            down_ratio: 39.5,
            sectors: [
                { name: '科技', stock_count: 156, avg_change: 2.3, change: 2.3 },
                { name: '医药', stock_count: 203, avg_change: 1.8, change: 1.8 },
                { name: '金融', stock_count: 189, avg_change: 0.9, change: 0.9 },
                { name: '消费', stock_count: 234, avg_change: -0.5, change: -0.5 }
            ]
        };
    }

    async fetchSectorData(sectorName) {
        return {
            name: sectorName,
            avg_change: 2.3,
            leading_stock: '贵州茅台',
            stock_count: 156,
            turnover: '¥320亿',
            stocks: [
                { code: '600519', name: '贵州茅台', price: 1800.50, change: 3.2, volume: '1250万' },
                { code: '600036', name: '招商银行', price: 42.35, change: 1.8, volume: '890万' },
                { code: '601318', name: '中国平安', price: 58.90, change: 2.1, volume: '756万' }
            ]
        };
    }

    async fetchStockData(stockCode) {
        return {
            code: stockCode,
            name: '贵州茅台',
            price: 1800.50,
            change: 3.2,
            volume: '1250万',
            market_cap: '¥2.26万亿',
            ai_holdings: [
                { agent: 'GPT-5', amount: 1000, cost: 1750.00, pnl: 50500 },
                { agent: 'Claude-3.7', amount: 500, cost: 1780.00, pnl: 10250 }
            ]
        };
    }

    async fetchDecisionData(stockCode) {
        return {
            stockCode: stockCode,
            timeline: [
                {
                    timestamp: '09:30:00',
                    type: '数据获取',
                    description: '获取股票实时数据和技术指标',
                    details: 'RSI: 65, MACD: 金叉, 布林带: 中轨上方'
                },
                {
                    timestamp: '09:30:05',
                    type: '数据分析',
                    description: '分析价格走势和成交量',
                    details: '价格突破前期高点，成交量放大2倍'
                },
                {
                    timestamp: '09:30:10',
                    type: 'AI推理',
                    description: '基于技术指标和基本面进行决策',
                    details: '置信度: 85%, 建议: 买入'
                },
                {
                    timestamp: '09:30:15',
                    type: '交易执行',
                    description: '执行买入订单',
                    details: '买入1000股，价格¥1800.50'
                }
            ]
        };
    }
}

// 自动初始化
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('data-drilldown')) {
        window.dataDrillDown = new DataDrillDown();
    }
});

// 导出类
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DataDrillDown;
}
