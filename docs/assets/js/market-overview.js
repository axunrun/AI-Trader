/**
 * A股大盘展示功能模块
 * 提供指数概览、实时数据等功能
 */

class MarketOverview {
    constructor() {
        this.indices = [];
        this.currentIndex = '000001.SH';
        this.currentPeriod = 'daily';
        this.realtimeTimer = null;
        this.chart = null;

        this.init();
    }

    async init() {
        try {
            // 加载指数列表
            await this.loadIndices();

            // 初始化指数概览卡片
            this.initOverviewCards();

            // 初始化图表
            this.initChart();

            // 绑定事件
            this.bindEvents();

            console.log('✅ 大盘功能模块初始化完成');
        } catch (error) {
            console.error('❌ 大盘功能模块初始化失败:', error);
            showError('初始化失败: ' + error.message);
        }
    }

    async loadIndices() {
        // 模拟API调用（实际应调用后端API）
        const response = await fetch('/api/indices/list/available');
        if (!response.ok) {
            throw new Error('获取指数列表失败');
        }

        const result = await response.json();
        if (result.success) {
            this.indices = result.data.indices;
        } else {
            // 使用默认指数列表
            this.indices = this.getDefaultIndices();
        }
    }

    getDefaultIndices() {
        return [
            { code: '000001.SH', name: '上证指数', market: '上证', description: '上海证券交易所综合指数' },
            { code: '000016.SH', name: '上证50', market: '上证', description: '上海证券交易所50只最具代表性股票' },
            { code: '000300.SH', name: '沪深300', market: '沪深', description: '沪深300指数' },
            { code: '399001.SZ', name: '深证成指', market: '深证', description: '深圳成份股价指数' },
            { code: '399006.SZ', name: '创业板指', market: '深证', description: '创业板指数' },
            { code: '000688.SH', name: '科创50', market: '上证', description: '科创板50指数' },
            { code: '899050.BJ', name: '北证50', market: '北证', description: '北京证券交易所50指数' }
        ];
    }

    initOverviewCards() {
        const container = document.getElementById('overviewCards');
        if (!container) return;

        container.innerHTML = this.indices.map(index => this.createIndexCard(index)).join('');

        // 绑定卡片点击事件
        this.bindCardEvents();
    }

    createIndexCard(index) {
        return `
            <div class="overview-card" data-index="${index.code}">
                <div class="card-header">
                    <h4 class="index-name">${index.name}</h4>
                    <span class="index-code">${index.code}</span>
                </div>
                <div class="card-body">
                    <div class="index-price" id="price-${index.code}">--</div>
                    <div class="index-change" id="change-${index.code}">
                        <span class="change-value">--</span>
                        <span class="change-percent">--</span>
                    </div>
                    <div class="index-volume" id="volume-${index.code}">
                        成交量: <span class="volume-value">--</span>
                    </div>
                </div>
                <div class="card-footer">
                    <span class="last-update" id="update-${index.code}">--</span>
                </div>
            </div>
        `;
    }

    bindCardEvents() {
        const cards = document.querySelectorAll('.overview-card');
        cards.forEach(card => {
            card.addEventListener('click', () => {
                const indexCode = card.dataset.index;
                this.selectIndex(indexCode);

                // 更新选择器
                const select = document.getElementById('indexSelect');
                if (select) {
                    select.value = indexCode;
                }
            });
        });
    }

    selectIndex(indexCode) {
        this.currentIndex = indexCode;

        // 更新卡片状态
        document.querySelectorAll('.overview-card').forEach(card => {
            card.classList.remove('active');
            if (card.dataset.index === indexCode) {
                card.classList.add('active');
            }
        });

        // 更新图表
        if (window.klineChart) {
            window.klineChart.updateSymbol(indexCode);
        }

        // 更新图表标题
        const chartTitle = document.getElementById('chartTitle');
        if (chartTitle) {
            const index = this.indices.find(i => i.code === indexCode);
            chartTitle.textContent = `${index.name} - ${this.getPeriodName(this.currentPeriod)}`;
        }
    }

    getPeriodName(period) {
        const names = {
            'daily': '日线图',
            'weekly': '周线图',
            'monthly': '月线图',
            'yearly': '年线图',
            'realtime': '实时图'
        };
        return names[period] || '日线图';
    }

    initChart() {
        // 图表初始化已在kline-chart.js中完成
    }

    bindEvents() {
        // 指数选择器事件
        const indexSelect = document.getElementById('indexSelect');
        if (indexSelect) {
            indexSelect.addEventListener('change', (e) => {
                this.selectIndex(e.target.value);
            });
        }

        // 周期选择器事件
        const periodBtns = document.querySelectorAll('.period-btn');
        periodBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                periodBtns.forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');
                this.updatePeriod(e.target.dataset.period);
            });
        });

        // 刷新按钮事件
        const refreshBtn = document.getElementById('refreshBtn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                this.refreshData();
            });
        }

        // 滚动到顶部按钮
        const scrollToTopBtn = document.getElementById('scrollToTop');
        if (scrollToTopBtn) {
            window.addEventListener('scroll', () => {
                if (window.pageYOffset > 300) {
                    scrollToTopBtn.style.display = 'block';
                } else {
                    scrollToTopBtn.style.display = 'none';
                }
            });

            scrollToTopBtn.addEventListener('click', () => {
                window.scrollTo({ top: 0, behavior: 'smooth' });
            });
        }
    }

    updatePeriod(period) {
        this.currentPeriod = period;

        // 更新图表
        if (window.klineChart) {
            window.klineChart.updatePeriod(period);
        }

        // 更新图表标题
        const chartTitle = document.getElementById('chartTitle');
        if (chartTitle) {
            const index = this.indices.find(i => i.code === this.currentIndex);
            chartTitle.textContent = `${index.name} - ${this.getPeriodName(period)}`;
        }

        // 如果是实时模式，启动实时更新
        if (period === 'realtime') {
            this.startRealtimeUpdate();
        } else {
            this.stopRealtimeUpdate();
        }
    }

    startRealtimeUpdate() {
        const indicator = document.getElementById('realtimeIndicator');
        if (indicator) {
            indicator.style.display = 'flex';
        }

        this.realtimeTimer = setInterval(() => {
            this.updateRealtimeData();
        }, 5000); // 每5秒更新一次
    }

    stopRealtimeUpdate() {
        const indicator = document.getElementById('realtimeIndicator');
        if (indicator) {
            indicator.style.display = 'none';
        }

        if (this.realtimeTimer) {
            clearInterval(this.realtimeTimer);
            this.realtimeTimer = null;
        }
    }

    async updateRealtimeData() {
        try {
            // 模拟实时数据更新
            await this.loadIndexData(this.currentIndex, 'realtime');

            // 更新时间戳
            const lastUpdateTime = document.getElementById('lastUpdateTime');
            if (lastUpdateTime) {
                lastUpdateTime.textContent = new Date().toLocaleTimeString();
            }
        } catch (error) {
            console.error('实时数据更新失败:', error);
        }
    }

    async refreshData() {
        const refreshBtn = document.getElementById('refreshBtn');
        if (refreshBtn) {
            refreshBtn.disabled = true;
            refreshBtn.innerHTML = '<span class="loading-spinner"></span>刷新中...';
        }

        try {
            await this.loadIndexData(this.currentIndex, this.currentPeriod);
            showSuccess('数据刷新成功');
        } catch (error) {
            console.error('刷新数据失败:', error);
            showError('刷新数据失败: ' + error.message);
        } finally {
            if (refreshBtn) {
                refreshBtn.disabled = false;
                refreshBtn.textContent = '刷新数据';
            }
        }
    }

    async loadIndexData(indexCode, period) {
        // 模拟API调用（实际应调用后端API）
        await new Promise(resolve => setTimeout(resolve, 300));

        // 更新指数卡片数据
        this.updateIndexCard(indexCode);
    }

    updateIndexCard(indexCode) {
        // 生成模拟数据
        const price = (Math.random() * 1000 + 2000).toFixed(2);
        const change = (Math.random() - 0.5) * 100;
        const changePercent = (change / (parseFloat(price) - change) * 100).toFixed(2);
        const volume = Math.floor(Math.random() * 1000000000);
        const now = new Date().toLocaleTimeString();

        // 更新卡片显示
        const priceEl = document.getElementById(`price-${indexCode}`);
        const changeEl = document.getElementById(`change-${indexCode}`);
        const volumeEl = document.getElementById(`volume-${indexCode}`);
        const updateEl = document.getElementById(`update-${indexCode}`);

        if (priceEl) {
            priceEl.textContent = price;
        }

        if (changeEl) {
            const valueEl = changeEl.querySelector('.change-value');
            const percentEl = changeEl.querySelector('.change-percent');

            if (valueEl) {
                valueEl.textContent = (change >= 0 ? '+' : '') + change.toFixed(2);
                valueEl.className = 'change-value ' + (change >= 0 ? 'up' : 'down');
            }

            if (percentEl) {
                percentEl.textContent = (change >= 0 ? '+' : '') + changePercent + '%';
                percentEl.className = 'change-percent ' + (change >= 0 ? 'up' : 'down');
            }
        }

        if (volumeEl) {
            const volumeValueEl = volumeEl.querySelector('.volume-value');
            if (volumeValueEl) {
                volumeValueEl.textContent = this.formatVolume(volume);
            }
        }

        if (updateEl) {
            updateEl.textContent = now;
        }
    }

    formatVolume(volume) {
        if (volume >= 1e8) {
            return (volume / 1e8).toFixed(2) + '亿';
        } else if (volume >= 1e4) {
            return (volume / 1e4).toFixed(2) + '万';
        }
        return volume.toString();
    }

    // 获取市场概览数据
    async getMarketSummary() {
        try {
            const response = await fetch('/api/indices/realtime/all');
            if (!response.ok) {
                throw new Error('获取市场概览失败');
            }

            const result = await response.json();
            return result.data;
        } catch (error) {
            console.error('获取市场概览失败:', error);
            return null;
        }
    }

    // 对比多个指数
    async compareIndices(indexCodes) {
        try {
            const indicesParam = indexCodes.join(',');
            const response = await fetch(`/api/indices/comparison?indices=${indicesParam}&period=${this.currentPeriod}`);
            if (!response.ok) {
                throw new Error('指数对比失败');
            }

            const result = await response.json();
            return result.data;
        } catch (error) {
            console.error('指数对比失败:', error);
            return null;
        }
    }

    destroy() {
        this.stopRealtimeUpdate();
        if (this.chart) {
            this.chart.destroy();
        }
    }
}

// 全局变量
let marketOverview = null;

// 初始化大盘功能
document.addEventListener('DOMContentLoaded', () => {
    marketOverview = new MarketOverview();

    // 将实例挂载到全局，方便其他脚本访问
    window.marketOverview = marketOverview;
});

// 工具函数：显示加载状态
function showLoading(show) {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.style.display = show ? 'flex' : 'none';
    }
}

// 工具函数：显示错误
function showError(message) {
    const toast = document.getElementById('errorToast');
    const messageEl = document.getElementById('errorMessage');
    if (toast && messageEl) {
        messageEl.textContent = message;
        toast.style.display = 'block';
        setTimeout(() => {
            toast.style.display = 'none';
        }, 5000);
    }
    console.error(message);
}

// 工具函数：隐藏错误
function hideError() {
    const toast = document.getElementById('errorToast');
    if (toast) {
        toast.style.display = 'none';
    }
}

// 工具函数：显示成功消息
function showSuccess(message) {
    // 可以扩展为显示成功提示
    console.log('✅', message);
}
