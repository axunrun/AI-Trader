// AI Reasoning Viewer
// Displays AI agent's complete reasoning process

class AIReasoningViewer {
    constructor() {
        this.dataLoader = null;
        this.currentAgent = null;
        this.currentDate = null;
        this.reasoningData = null;
    }

    async initialize() {
        // Initialize config and data loader
        window.configLoader = new ConfigLoader();
        this.dataLoader = new DataLoader();
        await this.dataLoader.initialize();

        // Set up event listeners
        this.setupEventListeners();

        // Load available agents
        await this.loadAvailableAgents();

        // Set up scroll to top button
        this.setupScrollToTop();
    }

    setupEventListeners() {
        const agentSelect = document.getElementById('agentSelect');
        const dateSelect = document.getElementById('dateSelect');
        const loadBtn = document.getElementById('loadReasoningBtn');

        agentSelect.addEventListener('change', (e) => this.onAgentChange(e));
        dateSelect.addEventListener('change', (e) => this.onDateChange(e));
        loadBtn.addEventListener('click', () => this.loadReasoningData());
    }

    async loadAvailableAgents() {
        try {
            const agents = await this.dataLoader.loadAgentList();
            const agentSelect = document.getElementById('agentSelect');

            // Clear existing options
            agentSelect.innerHTML = '<option value="">请选择代理...</option>';

            // Add agent options
            agents.forEach(agent => {
                const config = window.configLoader.getAgentConfig(agent, 'cn');
                const displayName = config ? config.display_name : agent;
                const option = document.createElement('option');
                option.value = agent;
                option.textContent = displayName;
                agentSelect.appendChild(option);
            });

            console.log(`Loaded ${agents.length} agents`);
        } catch (error) {
            console.error('Error loading agents:', error);
        }
    }

    async onAgentChange(event) {
        const agent = event.target.value;
        const dateSelect = document.getElementById('dateSelect');
        const loadBtn = document.getElementById('loadReasoningBtn');

        if (!agent) {
            dateSelect.innerHTML = '<option value="">请先选择代理...</option>';
            dateSelect.disabled = true;
            loadBtn.disabled = true;
            return;
        }

        this.currentAgent = agent;
        await this.loadAvailableDates(agent);

        dateSelect.disabled = false;
        loadBtn.disabled = true;
    }

    async loadAvailableDates(agent) {
        try {
            const dateSelect = document.getElementById('dateSelect');
            dateSelect.innerHTML = '<option value="">请选择日期...</option>';

            // Load log directory for this agent
            const response = await fetch(`./data/agent_data_astock/${agent}/log/`);
            if (!response.ok) {
                dateSelect.innerHTML = '<option value="">无日志数据</option>';
                return;
            }

            const html = await response.text();
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            const links = doc.querySelectorAll('a[href]');

            const dates = [];
            links.forEach(link => {
                const href = link.getAttribute('href');
                if (href && href.includes('/') && href !== '../') {
                    const date = href.replace('/', '').trim();
                    if (date.match(/^\d{4}-\d{2}-\d{2}/)) {
                        dates.push(date);
                    }
                }
            });

            // Sort dates in descending order (newest first)
            dates.sort((a, b) => b.localeCompare(a));

            dates.forEach(date => {
                const option = document.createElement('option');
                option.value = date;
                option.textContent = date;
                dateSelect.appendChild(option);
            });

            console.log(`Loaded ${dates.length} dates for ${agent}`);
        } catch (error) {
            console.error('Error loading dates:', error);
            document.getElementById('dateSelect').innerHTML =
                '<option value="">加载失败</option>';
        }
    }

    onDateChange(event) {
        const date = event.target.value;
        const loadBtn = document.getElementById('loadReasoningBtn');

        if (!date) {
            loadBtn.disabled = true;
            return;
        }

        this.currentDate = date;
        loadBtn.disabled = false;
    }

    async loadReasoningData() {
        if (!this.currentAgent || !this.currentDate) {
            alert('请选择代理和日期');
            return;
        }

        const container = document.getElementById('reasoningContainer');
        const loadingOverlay = document.getElementById('loadingOverlay');

        // Show loading
        loadingOverlay.style.display = 'flex';
        container.style.display = 'none';

        try {
            const response = await fetch(
                `./data/agent_data_astock/${this.currentAgent}/log/${this.currentDate}/log.jsonl`
            );

            if (!response.ok) {
                throw new Error(`Failed to load log file: ${response.status}`);
            }

            const text = await response.text();
            const lines = text.trim().split('\n').filter(line => line.trim() !== '');

            const logs = lines.map(line => {
                try {
                    return JSON.parse(line);
                } catch (e) {
                    console.error('Error parsing line:', line, e);
                    return null;
                }
            }).filter(log => log !== null);

            this.reasoningData = logs;
            this.displayReasoningData(logs);

            // Hide loading and show content
            loadingOverlay.style.display = 'none';
            container.style.display = 'block';

        } catch (error) {
            console.error('Error loading reasoning data:', error);
            loadingOverlay.style.display = 'none';
            container.innerHTML = `
                <div class="error-message">
                    <h3>加载失败</h3>
                    <p>${error.message}</p>
                </div>
            `;
            container.style.display = 'block';
        }
    }

    displayReasoningData(logs) {
        const container = document.getElementById('reasoningContainer');

        if (!logs || logs.length === 0) {
            container.innerHTML = '<div class="no-data">暂无分析记录</div>';
            return;
        }

        // Group logs by type
        const marketAnalysis = logs.filter(log => log.type === 'market_analysis');
        const tradingActions = logs.filter(log => log.type === 'trade');
        const decisions = logs.filter(log => log.type === 'decision');
        const research = logs.filter(log => log.type === 'research');

        container.innerHTML = `
            <div class="reasoning-summary">
                <div class="summary-card">
                    <h3>📊 分析记录概览</h3>
                    <div class="summary-stats">
                        <div class="stat-item">
                            <span class="stat-label">市场分析</span>
                            <span class="stat-value">${marketAnalysis.length}</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">交易行动</span>
                            <span class="stat-value">${tradingActions.length}</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">决策记录</span>
                            <span class="stat-value">${decisions.length}</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">研究记录</span>
                            <span class="stat-value">${research.length}</span>
                        </div>
                    </div>
                </div>
            </div>

            <div class="reasoning-sections">
                ${this.renderSection('🔍 市场分析', marketAnalysis, 'market-analysis')}
                ${this.renderSection('💡 决策推理', decisions, 'decisions')}
                ${this.renderSection('💹 交易行动', tradingActions, 'trading')}
                ${this.renderSection('📚 研究记录', research, 'research')}
            </div>
        `;

        // Add event listeners for expandable sections
        container.querySelectorAll('.section-header').forEach(header => {
            header.addEventListener('click', (e) => {
                const section = e.currentTarget.nextElementSibling;
                section.classList.toggle('collapsed');
                e.currentTarget.querySelector('.toggle-icon').textContent =
                    section.classList.contains('collapsed') ? '▼' : '▲';
            });
        });
    }

    renderSection(title, items, className) {
        if (!items || items.length === 0) {
            return `
                <div class="reasoning-section ${className}">
                    <div class="section-header">
                        <h3>${title}</h3>
                        <span class="toggle-icon">▼</span>
                    </div>
                    <div class="section-content collapsed">
                        <div class="no-items">暂无记录</div>
                    </div>
                </div>
            `;
        }

        const itemsHtml = items.map(item => this.renderLogItem(item)).join('');

        return `
            <div class="reasoning-section ${className}">
                <div class="section-header">
                    <h3>${title} <span class="count">(${items.length})</span></h3>
                    <span class="toggle-icon">▲</span>
                </div>
                <div class="section-content">
                    ${itemsHtml}
                </div>
            </div>
        `;
    }

    renderLogItem(log) {
        const timestamp = new Date(log.timestamp || Date.now()).toLocaleString('zh-CN');
        const type = log.type || 'unknown';

        let content = '';
        switch (type) {
            case 'market_analysis':
                content = this.renderMarketAnalysis(log);
                break;
            case 'decision':
                content = this.renderDecision(log);
                break;
            case 'trade':
                content = this.renderTrade(log);
                break;
            case 'research':
                content = this.renderResearch(log);
                break;
            default:
                content = this.renderGenericLog(log);
        }

        return `
            <div class="log-item" data-type="${type}">
                <div class="log-header">
                    <span class="log-type">${this.getLogTypeLabel(type)}</span>
                    <span class="log-timestamp">${timestamp}</span>
                </div>
                <div class="log-content">
                    ${content}
                </div>
            </div>
        `;
    }

    renderMarketAnalysis(log) {
        const analysis = log.analysis || {};
        return `
            <div class="analysis-summary">
                <div class="summary-text">${log.summary || '市场分析摘要'}</div>
                ${analysis.indicators ? `
                    <div class="indicators">
                        <h4>技术指标</h4>
                        <ul>
                            ${Object.entries(analysis.indicators).map(([key, value]) =>
                                `<li><strong>${key}:</strong> ${value}</li>`
                            ).join('')}
                        </ul>
                    </div>
                ` : ''}
                ${analysis.sentiment ? `
                    <div class="sentiment">
                        <h4>市场情绪</h4>
                        <p>${analysis.sentiment}</p>
                    </div>
                ` : ''}
            </div>
        `;
    }

    renderDecision(log) {
        const decision = log.decision || {};
        return `
            <div class="decision-summary">
                <div class="decision-text">${log.summary || '决策摘要'}</div>
                <div class="decision-details">
                    ${decision.action ? `<div class="decision-action"><strong>行动:</strong> ${decision.action}</div>` : ''}
                    ${decision.reasoning ? `<div class="decision-reasoning"><strong>推理:</strong> ${decision.reasoning}</div>` : ''}
                    ${decision.confidence ? `<div class="decision-confidence"><strong>置信度:</strong> ${(decision.confidence * 100).toFixed(1)}%</div>` : ''}
                </div>
            </div>
        `;
    }

    renderTrade(log) {
        const trade = log.trade || {};
        return `
            <div class="trade-summary">
                <div class="trade-action ${trade.action}">
                    <strong>${trade.action?.toUpperCase() || 'UNKNOWN'}</strong>
                    ${trade.symbol ? `<span class="trade-symbol">${trade.symbol}</span>` : ''}
                </div>
                <div class="trade-details">
                    ${trade.amount ? `<div class="trade-amount"><strong>数量:</strong> ${trade.amount}</div>` : ''}
                    ${trade.price ? `<div class="trade-price"><strong>价格:</strong> ¥${trade.price}</div>` : ''}
                    ${trade.reasoning ? `<div class="trade-reasoning"><strong>理由:</strong> ${trade.reasoning}</div>` : ''}
                </div>
            </div>
        `;
    }

    renderResearch(log) {
        return `
            <div class="research-summary">
                <div class="research-text">${log.summary || '研究摘要'}</div>
                ${log.findings ? `
                    <div class="findings">
                        <h4>研究发现</h4>
                        <ul>
                            ${log.findings.map(finding => `<li>${finding}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}
            </div>
        `;
    }

    renderGenericLog(log) {
        return `
            <div class="generic-log">
                <pre>${JSON.stringify(log, null, 2)}</pre>
            </div>
        `;
    }

    getLogTypeLabel(type) {
        const labels = {
            'market_analysis': '市场分析',
            'decision': '决策',
            'trade': '交易',
            'research': '研究',
            'unknown': '未知'
        };
        return labels[type] || type;
    }

    setupScrollToTop() {
        const scrollBtn = document.getElementById('scrollToTop');
        scrollBtn.addEventListener('click', () => {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });

        window.addEventListener('scroll', () => {
            if (window.scrollY > 300) {
                scrollBtn.style.display = 'block';
            } else {
                scrollBtn.style.display = 'none';
            }
        });
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', async () => {
    const viewer = new AIReasoningViewer();
    await viewer.initialize();
});
