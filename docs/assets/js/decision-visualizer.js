/**
 * AI决策推理过程可视化组件
 * 展示完整的AI决策链，包括数据获取、分析、推理和交易执行
 */

class DecisionVisualizer {
    constructor(containerId = 'decision-visualizer') {
        this.container = document.getElementById(containerId);
        this.decisionTree = [];
        this.currentStage = 0;
        this.animationSpeed = 1000; // 1秒
        this.isPlaying = false;
        this.playbackSpeed = 1.0;

        this.stageDefinitions = {
            data_acquisition: {
                title: '📊 数据获取阶段',
                icon: '📊',
                color: '#4CAF50'
            },
            data_analysis: {
                title: '🔍 数据分析阶段',
                icon: '🔍',
                color: '#2196F3'
            },
            decision_reasoning: {
                title: '🧠 AI决策推理',
                icon: '🧠',
                color: '#9C27B0'
            },
            trade_execution: {
                title: '💹 交易执行',
                icon: '💹',
                color: '#FF9800'
            }
        };

        this.init();
    }

    init() {
        if (!this.container) {
            console.error('DecisionVisualizer: Container not found');
            return;
        }

        this.createUI();
        this.attachEventListeners();
    }

    createUI() {
        this.container.innerHTML = `
            <div class="decision-visualizer-container">
                <!-- 控制栏 -->
                <div class="control-panel">
                    <div class="control-buttons">
                        <button id="play-pause-btn" class="control-btn">
                            <span class="btn-icon">▶️</span>
                            <span class="btn-text">播放</span>
                        </button>
                        <button id="reset-btn" class="control-btn">
                            <span class="btn-icon">⏹️</span>
                            <span class="btn-text">重置</span>
                        </button>
                        <button id="step-forward-btn" class="control-btn">
                            <span class="btn-icon">⏭️</span>
                            <span class="btn-text">下一步</span>
                        </button>
                    </div>
                    <div class="speed-control">
                        <label for="speed-slider">播放速度:</label>
                        <input type="range" id="speed-slider" min="0.5" max="3" step="0.5" value="1">
                        <span id="speed-value">1.0x</span>
                    </div>
                </div>

                <!-- 阶段指示器 -->
                <div class="stage-indicators">
                    <div class="stage-progress">
                        <div class="progress-bar">
                            <div class="progress-fill" id="progress-fill"></div>
                        </div>
                        <div class="stage-labels">
                            <span class="stage-label" data-stage="0">数据获取</span>
                            <span class="stage-label" data-stage="1">数据分析</span>
                            <span class="stage-label" data-stage="2">决策推理</span>
                            <span class="stage-label" data-stage="3">交易执行</span>
                        </div>
                    </div>
                </div>

                <!-- 主内容区域 -->
                <div class="main-content">
                    <div class="stage-content" id="stage-content">
                        <!-- 动态内容将在这里渲染 -->
                    </div>
                </div>

                <!-- 决策链时间线 -->
                <div class="timeline-container">
                    <h3 class="timeline-title">决策过程时间线</h3>
                    <div class="timeline" id="decision-timeline">
                        <!-- 时间线项目将在这里渲染 -->
                    </div>
                </div>

                <!-- 详细信息面板 -->
                <div class="detail-panel" id="detail-panel">
                    <div class="detail-header">
                        <h4>详细信息</h4>
                        <button class="close-btn" id="close-detail-btn">×</button>
                    </div>
                    <div class="detail-content" id="detail-content">
                        <!-- 详细信息将在这里渲染 -->
                    </div>
                </div>
            </div>
        `;

        this.injectStyles();
    }

    injectStyles() {
        if (document.getElementById('decision-visualizer-styles')) return;

        const styles = `
            <style id="decision-visualizer-styles">
                .decision-visualizer-container {
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    padding: 20px;
                    background: #f5f5f5;
                    border-radius: 8px;
                }

                .control-panel {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 20px;
                    padding: 15px;
                    background: white;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }

                .control-buttons {
                    display: flex;
                    gap: 10px;
                }

                .control-btn {
                    padding: 10px 20px;
                    border: none;
                    border-radius: 5px;
                    background: #2196F3;
                    color: white;
                    cursor: pointer;
                    display: flex;
                    align-items: center;
                    gap: 8px;
                    font-size: 14px;
                    transition: all 0.3s;
                }

                .control-btn:hover {
                    background: #1976D2;
                    transform: translateY(-2px);
                }

                .control-btn:disabled {
                    background: #ccc;
                    cursor: not-allowed;
                    transform: none;
                }

                .speed-control {
                    display: flex;
                    align-items: center;
                    gap: 10px;
                }

                #speed-slider {
                    width: 150px;
                }

                .stage-indicators {
                    margin-bottom: 20px;
                }

                .stage-progress {
                    background: white;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }

                .progress-bar {
                    width: 100%;
                    height: 8px;
                    background: #e0e0e0;
                    border-radius: 4px;
                    overflow: hidden;
                    margin-bottom: 15px;
                }

                .progress-fill {
                    height: 100%;
                    background: linear-gradient(90deg, #4CAF50, #2196F3);
                    transition: width 0.5s ease;
                    width: 0%;
                }

                .stage-labels {
                    display: flex;
                    justify-content: space-between;
                }

                .stage-label {
                    font-size: 14px;
                    color: #666;
                    cursor: pointer;
                    padding: 5px 10px;
                    border-radius: 4px;
                    transition: all 0.3s;
                }

                .stage-label:hover {
                    background: #f0f0f0;
                }

                .stage-label.active {
                    background: #2196F3;
                    color: white;
                }

                .main-content {
                    background: white;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    margin-bottom: 20px;
                    min-height: 400px;
                }

                .stage-content {
                    padding: 30px;
                }

                .timeline-container {
                    background: white;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    padding: 20px;
                }

                .timeline-title {
                    margin-bottom: 15px;
                    color: #333;
                }

                .timeline {
                    position: relative;
                    padding-left: 40px;
                }

                .timeline::before {
                    content: '';
                    position: absolute;
                    left: 15px;
                    top: 0;
                    bottom: 0;
                    width: 3px;
                    background: linear-gradient(180deg, #4CAF50, #2196F3, #9C27B0, #FF9800);
                }

                .timeline-item {
                    position: relative;
                    margin-bottom: 25px;
                    padding: 15px;
                    background: #f9f9f9;
                    border-radius: 8px;
                    cursor: pointer;
                    transition: all 0.3s;
                }

                .timeline-item:hover {
                    background: #f0f0f0;
                    transform: translateX(5px);
                }

                .timeline-item::before {
                    content: '';
                    position: absolute;
                    left: -32px;
                    top: 20px;
                    width: 15px;
                    height: 15px;
                    background: white;
                    border: 3px solid #2196F3;
                    border-radius: 50%;
                }

                .timeline-item.active::before {
                    background: #2196F3;
                    box-shadow: 0 0 0 4px rgba(33, 150, 243, 0.2);
                }

                .timeline-item-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 8px;
                }

                .timeline-item-type {
                    font-weight: 600;
                    color: #2196F3;
                }

                .timeline-item-time {
                    font-size: 12px;
                    color: #999;
                }

                .timeline-item-description {
                    color: #666;
                    font-size: 14px;
                }

                .detail-panel {
                    position: fixed;
                    right: -400px;
                    top: 0;
                    width: 400px;
                    height: 100vh;
                    background: white;
                    box-shadow: -2px 0 10px rgba(0,0,0,0.1);
                    transition: right 0.3s ease;
                    z-index: 1000;
                }

                .detail-panel.open {
                    right: 0;
                }

                .detail-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    padding: 20px;
                    border-bottom: 1px solid #e0e0e0;
                }

                .detail-content {
                    padding: 20px;
                    overflow-y: auto;
                    height: calc(100vh - 80px);
                }

                .close-btn {
                    background: none;
                    border: none;
                    font-size: 24px;
                    cursor: pointer;
                    color: #999;
                }

                .stage-card {
                    border-left: 4px solid;
                    padding: 20px;
                    background: #f9f9f9;
                    border-radius: 8px;
                    margin-bottom: 15px;
                }

                .stage-card h3 {
                    margin: 0 0 15px 0;
                    display: flex;
                    align-items: center;
                    gap: 10px;
                }

                .stage-metrics {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                    gap: 15px;
                    margin: 15px 0;
                }

                .metric-card {
                    padding: 15px;
                    background: white;
                    border-radius: 6px;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                }

                .metric-label {
                    font-size: 12px;
                    color: #999;
                    margin-bottom: 5px;
                }

                .metric-value {
                    font-size: 24px;
                    font-weight: 600;
                    color: #333;
                }

                .metric-trend {
                    font-size: 12px;
                    margin-top: 5px;
                }

                .metric-trend.up {
                    color: #4CAF50;
                }

                .metric-trend.down {
                    color: #f44336;
                }
            </style>
        `;

        document.head.insertAdjacentHTML('beforeend', styles);
    }

    attachEventListeners() {
        // 播放/暂停按钮
        const playPauseBtn = document.getElementById('play-pause-btn');
        if (playPauseBtn) {
            playPauseBtn.addEventListener('click', () => this.togglePlayback());
        }

        // 重置按钮
        const resetBtn = document.getElementById('reset-btn');
        if (resetBtn) {
            resetBtn.addEventListener('click', () => this.reset());
        }

        // 下一步按钮
        const stepForwardBtn = document.getElementById('step-forward-btn');
        if (stepForwardBtn) {
            stepForwardBtn.addEventListener('click', () => this.stepForward());
        }

        // 速度控制
        const speedSlider = document.getElementById('speed-slider');
        if (speedSlider) {
            speedSlider.addEventListener('input', (e) => {
                this.playbackSpeed = parseFloat(e.target.value);
                document.getElementById('speed-value').textContent = `${this.playbackSpeed.toFixed(1)}x`;
            });
        }

        // 关闭详情面板
        const closeDetailBtn = document.getElementById('close-detail-btn');
        if (closeDetailBtn) {
            closeDetailBtn.addEventListener('click', () => this.closeDetailPanel());
        }

        // 点击阶段标签跳转
        document.querySelectorAll('.stage-label').forEach(label => {
            label.addEventListener('click', (e) => {
                const stage = parseInt(e.target.dataset.stage);
                this.jumpToStage(stage);
            });
        });
    }

    async loadDecisionData(agentName, date) {
        // 从log.jsonl加载推理过程
        try {
            const response = await fetch(`/api/logs/${agentName}/${date}/log.jsonl`);
            const text = await response.text();
            const lines = text.trim().split('\n');

            this.decisionTree = lines.map(line => JSON.parse(line));

            this.renderTimeline();
            this.renderStage(0);
            this.updateProgress();

            console.log(`Loaded ${this.decisionTree.length} decision steps`);
        } catch (error) {
            console.error('Failed to load decision data:', error);
            this.loadMockData(); // 加载模拟数据
        }
    }

    loadMockData() {
        // 模拟数据
        this.decisionTree = [
            {
                stage: 'data_acquisition',
                timestamp: '2025-12-09 09:30:00',
                type: 'fetch_stock_data',
                description: '获取股票数据',
                data: {
                    sources: ['Tushare', 'efinance'],
                    quality_score: 92,
                    stocks_count: 50
                }
            },
            {
                stage: 'data_analysis',
                timestamp: '2025-12-09 09:30:05',
                type: 'technical_analysis',
                description: '技术指标分析',
                data: {
                    indicators: ['RSI', 'MACD', '布林带'],
                    signals: ['买入', '持有', '卖出']
                }
            },
            {
                stage: 'decision_reasoning',
                timestamp: '2025-12-09 09:30:10',
                type: 'ai_reasoning',
                description: 'AI决策推理',
                data: {
                    confidence: 0.85,
                    reasoning_steps: ['价格突破', '成交量放大', '技术指标向好']
                }
            },
            {
                stage: 'trade_execution',
                timestamp: '2025-12-09 09:30:15',
                type: 'place_order',
                description: '执行交易',
                data: {
                    action: 'buy',
                    symbol: '600519.SH',
                    amount: 1000,
                    price: 1800.50
                }
            }
        ];

        this.renderTimeline();
        this.renderStage(0);
        this.updateProgress();
    }

    renderTimeline() {
        const timeline = document.getElementById('decision-timeline');
        if (!timeline) return;

        timeline.innerHTML = this.decisionTree.map((step, index) => `
            <div class="timeline-item ${index === this.currentStage ? 'active' : ''}"
                 data-index="${index}">
                <div class="timeline-item-header">
                    <span class="timeline-item-type">${step.type}</span>
                    <span class="timeline-item-time">${step.timestamp}</span>
                </div>
                <div class="timeline-item-description">${step.description}</div>
            </div>
        `).join('');

        // 添加点击事件
        timeline.querySelectorAll('.timeline-item').forEach(item => {
            item.addEventListener('click', (e) => {
                const index = parseInt(e.currentTarget.dataset.index);
                this.jumpToStage(index);
            });
        });
    }

    renderStage(stageIndex) {
        const stageContent = document.getElementById('stage-content');
        if (!stageContent || !this.decisionTree[stageIndex]) return;

        const stage = this.decisionTree[stageIndex];
        const stageDef = this.stageDefinitions[stage.stage];

        stageContent.innerHTML = `
            <div class="stage-card" style="border-color: ${stageDef.color}">
                <h3>
                    <span style="font-size: 32px;">${stageDef.icon}</span>
                    ${stageDef.title}
                </h3>
                <p>${stage.description}</p>

                <div class="stage-metrics">
                    ${this.renderMetrics(stage)}
                </div>

                <div class="stage-details">
                    ${this.renderStageDetails(stage)}
                </div>
            </div>
        `;

        // 更新阶段标签状态
        document.querySelectorAll('.stage-label').forEach((label, index) => {
            label.classList.toggle('active', index === stageIndex);
        });
    }

    renderMetrics(stage) {
        if (!stage.data) return '';

        return Object.entries(stage.data).map(([key, value]) => `
            <div class="metric-card">
                <div class="metric-label">${this.formatLabel(key)}</div>
                <div class="metric-value">${this.formatValue(value)}</div>
            </div>
        `).join('');
    }

    renderStageDetails(stage) {
        // 根据阶段类型渲染不同的详细信息
        switch (stage.stage) {
            case 'data_acquisition':
                return this.renderDataAcquisitionDetails(stage.data);
            case 'data_analysis':
                return this.renderDataAnalysisDetails(stage.data);
            case 'decision_reasoning':
                return this.renderDecisionReasoningDetails(stage.data);
            case 'trade_execution':
                return this.renderTradeExecutionDetails(stage.data);
            default:
                return '';
        }
    }

    renderDataAcquisitionDetails(data) {
        if (!data) return '';

        return `
            <div class="detail-section">
                <h4>数据源</h4>
                <ul>
                    ${(data.sources || []).map(source => `<li>${source}</li>`).join('')}
                </ul>

                <h4>数据质量评估</h4>
                <p>质量分数: ${data.quality_score || 0}/100</p>
            </div>
        `;
    }

    renderDataAnalysisDetails(data) {
        if (!data) return '';

        return `
            <div class="detail-section">
                <h4>技术指标</h4>
                <ul>
                    ${(data.indicators || []).map(indicator => `<li>${indicator}</li>`).join('')}
                </ul>

                <h4>信号分析</h4>
                <ul>
                    ${(data.signals || []).map(signal => `<li>${signal}</li>`).join('')}
                </ul>
            </div>
        `;
    }

    renderDecisionReasoningDetails(data) {
        if (!data) return '';

        return `
            <div class="detail-section">
                <h4>置信度</h4>
                <div class="confidence-bar">
                    <div class="confidence-fill" style="width: ${(data.confidence * 100)}%"></div>
                </div>
                <p>${(data.confidence * 100).toFixed(1)}%</p>

                <h4>推理步骤</h4>
                <ol>
                    ${(data.reasoning_steps || []).map(step => `<li>${step}</li>`).join('')}
                </ol>
            </div>
        `;
    }

    renderTradeExecutionDetails(data) {
        if (!data) return '';

        return `
            <div class="detail-section">
                <h4>交易详情</h4>
                <table>
                    <tr><td>操作:</td><td>${data.action}</td></tr>
                    <tr><td>股票:</td><td>${data.symbol}</td></tr>
                    <tr><td>数量:</td><td>${data.amount}股</td></tr>
                    <tr><td>价格:</td><td>¥${data.price}</td></tr>
                </table>
            </div>
        `;
    }

    formatLabel(key) {
        return key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    }

    formatValue(value) {
        if (typeof value === 'number') {
            return value.toLocaleString();
        }
        if (Array.isArray(value)) {
            return value.length;
        }
        return value;
    }

    updateProgress() {
        const progressFill = document.getElementById('progress-fill');
        if (progressFill) {
            const progress = (this.currentStage / (this.decisionTree.length - 1)) * 100;
            progressFill.style.width = `${progress}%`;
        }
    }

    async play() {
        if (this.isPlaying) return;

        this.isPlaying = true;
        const playPauseBtn = document.getElementById('play-pause-btn');
        playPauseBtn.querySelector('.btn-text').textContent = '暂停';
        playPauseBtn.querySelector('.btn-icon').textContent = '⏸️';

        while (this.isPlaying && this.currentStage < this.decisionTree.length - 1) {
            await this.delay(this.animationSpeed / this.playbackSpeed);
            this.stepForward();
        }

        this.pause();
    }

    pause() {
        this.isPlaying = false;
        const playPauseBtn = document.getElementById('play-pause-btn');
        playPauseBtn.querySelector('.btn-text').textContent = '播放';
        playPauseBtn.querySelector('.btn-icon').textContent = '▶️';
    }

    togglePlayback() {
        if (this.isPlaying) {
            this.pause();
        } else {
            this.play();
        }
    }

    reset() {
        this.pause();
        this.currentStage = 0;
        this.renderStage(0);
        this.renderTimeline();
        this.updateProgress();
    }

    stepForward() {
        if (this.currentStage < this.decisionTree.length - 1) {
            this.currentStage++;
            this.renderStage(this.currentStage);
            this.renderTimeline();
            this.updateProgress();
        }
    }

    jumpToStage(stageIndex) {
        if (stageIndex >= 0 && stageIndex < this.decisionTree.length) {
            this.currentStage = stageIndex;
            this.renderStage(stageIndex);
            this.renderTimeline();
            this.updateProgress();
        }
    }

    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    openDetailPanel(step) {
        const detailPanel = document.getElementById('detail-panel');
        const detailContent = document.getElementById('detail-content');

        detailContent.innerHTML = `
            <h3>${step.type}</h3>
            <p><strong>时间:</strong> ${step.timestamp}</p>
            <p><strong>描述:</strong> ${step.description}</p>
            <pre>${JSON.stringify(step.data, null, 2)}</pre>
        `;

        detailPanel.classList.add('open');
    }

    closeDetailPanel() {
        const detailPanel = document.getElementById('detail-panel');
        detailPanel.classList.remove('open');
    }
}

// 自动初始化
document.addEventListener('DOMContentLoaded', () => {
    // 如果页面中有decision-visualizer容器，则初始化
    if (document.getElementById('decision-visualizer')) {
        window.decisionVisualizer = new DecisionVisualizer();
    }
});

// 导出类
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DecisionVisualizer;
}
