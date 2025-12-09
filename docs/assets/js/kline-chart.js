/**
 * K线图组件
 * 使用lightweight-charts库实现专业K线图展示
 */

class KLineChart {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        this.chart = null;
        this.candlestickSeries = null;
        this.volumeSeries = null;
        this.currentPeriod = 'daily';
        this.currentSymbol = '000001.SH';
        this.isLogScale = false;
        this.data = [];

        // 默认配置
        this.defaultOptions = {
            width: this.container.clientWidth,
            height: 400,
            layout: {
                background: { color: 'rgba(26, 26, 46, 0.8)' },
                textColor: '#d1d4dc',
            },
            grid: {
                vertLines: { color: 'rgba(42, 46, 57, 0.5)' },
                horzLines: { color: 'rgba(42, 46, 57, 0.5)' },
            },
            crosshair: {
                mode: LightweightCharts.CrosshairMode.Normal,
            },
            rightPriceScale: {
                borderColor: 'rgba(42, 46, 57, 0.8)',
            },
            timeScale: {
                borderColor: 'rgba(42, 46, 57, 0.8)',
                timeVisible: true,
                secondsVisible: false,
            },
            ...options
        };

        this.init();
    }

    init() {
        // 创建图表
        this.chart = LightweightCharts.createChart(
            this.container,
            this.defaultOptions
        );

        // 创建K线系列
        this.candlestickSeries = this.chart.addCandlestickSeries({
            upColor: '#ef5350',      // 红色上涨（中国股市惯例）
            downColor: '#26a69a',    // 绿色下跌
            borderVisible: false,
            wickUpColor: '#ef5350',
            wickDownColor: '#26a69a',
        });

        // 创建成交量系列
        this.volumeSeries = this.chart.addHistogramSeries({
            color: 'rgba(38, 166, 154, 0.5)',
            priceFormat: {
                type: 'volume',
            },
            priceScaleId: '',
            scaleMargins: {
                top: 0.8,
                bottom: 0,
            },
        });

        // 响应式调整
        window.addEventListener('resize', () => {
            this.chart.applyOptions({
                width: this.container.clientWidth,
            });
        });

        // 添加工具提示
        this.addTooltip();
    }

    addTooltip() {
        const tooltip = document.createElement('div');
        tooltip.className = 'chart-tooltip';
        tooltip.style.cssText = `
            position: absolute;
            display: none;
            padding: 8px 12px;
            background: rgba(0, 0, 0, 0.8);
            color: #fff;
            font-size: 12px;
            border-radius: 4px;
            pointer-events: none;
            z-index: 1000;
        `;
        this.container.appendChild(tooltip);

        this.chart.subscribeCrosshairMove((param) => {
            if (!param || !param.time) {
                tooltip.style.display = 'none';
                return;
            }

            const data = param.seriesData.get(this.candlestickSeries);
            if (!data) {
                tooltip.style.display = 'none';
                return;
            }

            const date = new Date(param.time * 1000);
            tooltip.innerHTML = `
                <div><strong>${date.toLocaleDateString()}</strong></div>
                <div>开盘: ${data.open.toFixed(2)}</div>
                <div>最高: ${data.high.toFixed(2)}</div>
                <div>最低: ${data.low.toFixed(2)}</div>
                <div>收盘: ${data.close.toFixed(2)}</div>
            `;

            tooltip.style.display = 'block';
            tooltip.style.left = param.point.x + 10 + 'px';
            tooltip.style.top = param.point.y + 10 + 'px';
        });
    }

    setData(data) {
        if (!data || data.length === 0) {
            console.warn('K线图数据为空');
            return;
        }

        this.data = data;
        const candlestickData = data.map(item => ({
            time: Math.floor(new Date(item.timestamp).getTime() / 1000),
            open: item.open_price,
            high: item.high_price,
            low: item.low_price,
            close: item.close_price,
        }));

        const volumeData = data.map(item => ({
            time: Math.floor(new Date(item.timestamp).getTime() / 1000),
            value: item.volume,
            color: item.close_price >= item.open_price ?
                'rgba(239, 83, 80, 0.5)' : 'rgba(38, 166, 154, 0.5)'
        }));

        this.candlestickSeries.setData(candlestickData);
        this.volumeSeries.setData(volumeData);

        // 自动缩放到合适范围
        this.chart.timeScale().fitContent();
    }

    async loadData(symbol, period = 'daily', startDate = null, endDate = null) {
        try {
            showLoading(true);

            // 模拟API调用（实际应调用后端API）
            const data = await this.fetchIndexData(symbol, period, startDate, endDate);

            this.setData(data);
            return data;
        } catch (error) {
            console.error('加载K线数据失败:', error);
            showError('加载数据失败: ' + error.message);
            throw error;
        } finally {
            showLoading(false);
        }
    }

    async fetchIndexData(symbol, period, startDate, endDate) {
        // 模拟API调用延迟
        await new Promise(resolve => setTimeout(resolve, 500));

        // 生成模拟数据（实际应调用后端API）
        const mockData = this.generateMockData(symbol, period, startDate, endDate);
        return mockData;
    }

    generateMockData(symbol, period, startDate, endDate) {
        const data = [];
        const now = new Date();
        const start = startDate ? new Date(startDate) : new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
        const end = endDate ? new Date(endDate) : now;

        const basePrice = this.getBasePrice(symbol);
        let currentPrice = basePrice;

        const timeInterval = this.getTimeInterval(period);

        for (let time = start.getTime(); time <= end.getTime(); time += timeInterval) {
            const date = new Date(time);

            // 跳过周末（对于日线数据）
            if (period === 'daily' && (date.getDay() === 0 || date.getDay() === 6)) {
                continue;
            }

            const change = (Math.random() - 0.5) * 0.1; // ±5%波动
            const open = currentPrice;
            const close = currentPrice * (1 + change);
            const high = Math.max(open, close) * (1 + Math.random() * 0.05);
            const low = Math.min(open, close) * (1 - Math.random() * 0.05);
            const volume = Math.floor(Math.random() * 1000000000);

            data.push({
                timestamp: date.toISOString(),
                open_price: parseFloat(open.toFixed(2)),
                high_price: parseFloat(high.toFixed(2)),
                low_price: parseFloat(low.toFixed(2)),
                close_price: parseFloat(close.toFixed(2)),
                volume: volume,
                change_pct: parseFloat(((close - open) / open * 100).toFixed(2))
            });

            currentPrice = close;
        }

        return data.reverse(); // 按时间倒序
    }

    getBasePrice(symbol) {
        const prices = {
            '000001.SH': 3200, // 上证指数
            '000016.SH': 2800, // 上证50
            '000300.SH': 3500, // 沪深300
            '399001.SZ': 10500, // 深证成指
            '399006.SZ': 2200, // 创业板指
            '000688.SH': 900,  // 科创50
            '899050.BJ': 1000  // 北证50
        };
        return prices[symbol] || 1000;
    }

    getTimeInterval(period) {
        const intervals = {
            'daily': 24 * 60 * 60 * 1000,      // 1天
            'weekly': 7 * 24 * 60 * 60 * 1000, // 1周
            'monthly': 30 * 24 * 60 * 60 * 1000, // 1月
            'yearly': 365 * 24 * 60 * 60 * 1000  // 1年
        };
        return intervals[period] || intervals['daily'];
    }

    toggleLogScale() {
        this.isLogScale = !this.isLogScale;
        this.chart.priceScale().applyOptions({
            scaleType: this.isLogScale ?
                LightweightCharts.PriceScaleType.Logarithmic :
                LightweightCharts.PriceScaleType.Normal
        });
    }

    exportData() {
        if (!this.data || this.data.length === 0) {
            showError('没有数据可导出');
            return;
        }

        const csv = this.convertToCSV(this.data);
        const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = `${this.currentSymbol}_${this.currentPeriod}_${new Date().toISOString().split('T')[0]}.csv`;
        link.click();
    }

    convertToCSV(data) {
        const headers = ['日期', '开盘价', '最高价', '最低价', '收盘价', '成交量', '涨跌幅'];
        const rows = data.map(item => [
            item.timestamp.split('T')[0],
            item.open_price,
            item.high_price,
            item.low_price,
            item.close_price,
            item.volume,
            item.change_pct + '%'
        ]);

        return [headers, ...rows].map(row => row.join(',')).join('\n');
    }

    updateSymbol(symbol) {
        this.currentSymbol = symbol;
        this.loadData(symbol, this.currentPeriod);
    }

    updatePeriod(period) {
        this.currentPeriod = period;
        this.loadData(this.currentSymbol, period);
    }

    destroy() {
        if (this.chart) {
            this.chart.remove();
            this.chart = null;
        }
    }
}

// 全局变量
let klineChart = null;

// 初始化K线图
document.addEventListener('DOMContentLoaded', () => {
    klineChart = new KlineChart('klineChart');
    klineChart.loadData('000001.SH', 'daily');

    // 绑定事件
    const indexSelect = document.getElementById('indexSelect');
    if (indexSelect) {
        indexSelect.addEventListener('change', (e) => {
            klineChart.updateSymbol(e.target.value);
        });
    }

    const periodBtns = document.querySelectorAll('.period-btn');
    periodBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            periodBtns.forEach(b => b.classList.remove('active'));
            e.target.classList.add('active');
            klineChart.updatePeriod(e.target.dataset.period);
        });
    });

    const toggleLogBtn = document.getElementById('toggleLog');
    if (toggleLogBtn) {
        toggleLogBtn.addEventListener('click', () => {
            klineChart.toggleLogScale();
            toggleLogBtn.textContent = klineChart.isLogScale ? '对数刻度' : '线性刻度';
        });
    }

    const exportBtn = document.getElementById('exportChart');
    if (exportBtn) {
        exportBtn.addEventListener('click', () => {
            klineChart.exportData();
        });
    }
});
