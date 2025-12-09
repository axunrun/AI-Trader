/**
 * 高级图表组件
 * 基于Chart.js的高级股票图表，支持多指标、技术分析等
 */

class AdvancedChart {
    constructor(canvasId, options = {}) {
        this.canvas = document.getElementById(canvasId);
        if (!this.canvas) {
            console.error(`Canvas ${canvasId} not found`);
            return;
        }

        this.ctx = this.canvas.getContext('2d');
        this.options = {
            responsive: true,
            maintainAspectRatio: false,
            animation: {
                duration: 750,
                easing: 'easeInOutQuart'
            },
            ...options
        };

        this.chart = null;
        this.data = null;
        this.indicators = new Set();
        this.crosshair = {
            enabled: false,
            x: 0,
            y: 0
        };

        this.init();
    }

    init() {
        this.setupCanvas();
        this.attachEventListeners();
    }

    setupCanvas() {
        const rect = this.canvas.getBoundingClientRect();
        this.canvas.width = rect.width * window.devicePixelRatio;
        this.canvas.height = rect.height * window.devicePixelRatio;
        this.ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
    }

    createCandlestickChart(data) {
        this.data = data;

        const config = {
            type: 'candlestick',
            data: {
                datasets: [
                    {
                        label: 'K线',
                        data: data.prices,
                        type: 'candlestick',
                        color: {
                            up: '#4CAF50',
                            down: '#f44336',
                            unchanged: '#999'
                        },
                        borderColor: '#333'
                    },
                    {
                        label: '成交量',
                        data: data.volumes,
                        type: 'bar',
                        backgroundColor: (ctx) => {
                            const value = ctx.raw.v;
                            return value > 0 ? 'rgba(33, 150, 243, 0.6)' : 'rgba(244, 67, 54, 0.6)';
                        },
                        yAxisID: 'volume'
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                        callbacks: {
                            label: (context) => {
                                const dataPoint = context.raw;
                                return `${context.dataset.label}: ${dataPoint.c}`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        type: 'time',
                        time: {
                            unit: 'day'
                        },
                        grid: {
                            display: false
                        }
                    },
                    price: {
                        type: 'linear',
                        position: 'left',
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)'
                        }
                    },
                    volume: {
                        type: 'linear',
                        position: 'right',
                        grid: {
                            display: false
                        }
                    }
                }
            }
        };

        this.chart = new Chart(this.ctx, config);
        return this.chart;
    }

    addTechnicalIndicator(indicatorType, data) {
        let config = null;

        switch (indicatorType) {
            case 'ma':
                config = {
                    label: `MA${data.period}`,
                    data: data.values,
                    type: 'line',
                    borderColor: data.color || '#2196F3',
                    borderWidth: 2,
                    fill: false,
                    yAxisID: 'price',
                    tension: 0.1
                };
                break;

            case 'ema':
                config = {
                    label: `EMA${data.period}`,
                    data: data.values,
                    type: 'line',
                    borderColor: data.color || '#FF9800',
                    borderWidth: 2,
                    fill: false,
                    yAxisID: 'price',
                    tension: 0.1
                };
                break;

            case 'rsi':
                config = {
                    label: `RSI${data.period}`,
                    data: data.values,
                    type: 'line',
                    borderColor: data.color || '#9C27B0',
                    borderWidth: 2,
                    fill: false,
                    yAxisID: 'rsi',
                    tension: 0.1
                };
                break;

            case 'macd':
                config = [
                    {
                        label: 'MACD',
                        data: data.macd,
                        type: 'line',
                        borderColor: '#2196F3',
                        borderWidth: 2,
                        fill: false,
                        yAxisID: 'macd'
                    },
                    {
                        label: 'Signal',
                        data: data.signal,
                        type: 'line',
                        borderColor: '#FF9800',
                        borderWidth: 2,
                        fill: false,
                        yAxisID: 'macd'
                    },
                    {
                        label: 'Histogram',
                        data: data.histogram,
                        type: 'bar',
                        backgroundColor: (ctx) => {
                            const value = ctx.raw;
                            return value >= 0 ? 'rgba(76, 175, 80, 0.6)' : 'rgba(244, 67, 54, 0.6)';
                        },
                        yAxisID: 'macd'
                    }
                ];
                break;

            case 'bollinger':
                config = [
                    {
                        label: 'Upper',
                        data: data.upper,
                        type: 'line',
                        borderColor: '#4CAF50',
                        borderWidth: 1,
                        fill: false,
                        yAxisID: 'price'
                    },
                    {
                        label: 'Middle',
                        data: data.middle,
                        type: 'line',
                        borderColor: '#2196F3',
                        borderWidth: 2,
                        fill: false,
                        yAxisID: 'price'
                    },
                    {
                        label: 'Lower',
                        data: data.lower,
                        type: 'line',
                        borderColor: '#f44336',
                        borderWidth: 1,
                        fill: false,
                        yAxisID: 'price'
                    }
                ];
                break;
        }

        if (config) {
            this.addDataset(config);
            this.indicators.add(indicatorType);
        }

        return config;
    }

    addDataset(dataset) {
        if (Array.isArray(dataset)) {
            dataset.forEach(ds => this.chart.data.datasets.push(ds));
        } else {
            this.chart.data.datasets.push(dataset);
        }
        this.chart.update();
    }

    removeTechnicalIndicator(indicatorType) {
        if (!this.indicators.has(indicatorType)) return;

        const labels = this.getIndicatorLabels(indicatorType);

        this.chart.data.datasets = this.chart.data.datasets.filter(
            dataset => !labels.includes(dataset.label)
        );

        this.indicators.delete(indicatorType);
        this.chart.update();
    }

    getIndicatorLabels(indicatorType) {
        const labelMap = {
            'ma': ['MA5', 'MA10', 'MA20', 'MA30', 'MA60'],
            'ema': ['EMA5', 'EMA10', 'EMA20', 'EMA30', 'EMA60'],
            'rsi': ['RSI6', 'RSI12', 'RSI24'],
            'macd': ['MACD', 'Signal', 'Histogram'],
            'bollinger': ['Upper', 'Middle', 'Lower']
        };

        return labelMap[indicatorType] || [];
    }

    enableCrosshair() {
        this.crosshair.enabled = true;
        this.canvas.addEventListener('mousemove', this.handleMouseMove.bind(this));
        this.canvas.addEventListener('mouseleave', this.handleMouseLeave.bind(this));
    }

    disableCrosshair() {
        this.crosshair.enabled = false;
        this.canvas.removeEventListener('mousemove', this.handleMouseMove.bind(this));
        this.canvas.removeEventListener('mouseleave', this.handleMouseLeave.bind(this));
        this.chart.update();
    }

    handleMouseMove(event) {
        if (!this.crosshair.enabled) return;

        const rect = this.canvas.getBoundingClientRect();
        this.crosshair.x = event.clientX - rect.left;
        this.crosshair.y = event.clientY - rect.top;

        this.chart.update('none');
        this.drawCrosshair();
    }

    handleMouseLeave() {
        this.crosshair.x = 0;
        this.crosshair.y = 0;
        this.chart.update('none');
    }

    drawCrosshair() {
        if (!this.crosshair.enabled) return;

        const ctx = this.ctx;
        ctx.save();
        ctx.strokeStyle = 'rgba(0, 0, 0, 0.5)';
        ctx.lineWidth = 1;
        ctx.setLineDash([5, 5]);

        // 垂直线
        ctx.beginPath();
        ctx.moveTo(this.crosshair.x, 0);
        ctx.lineTo(this.crosshair.x, this.canvas.height);
        ctx.stroke();

        // 水平线
        ctx.beginPath();
        ctx.moveTo(0, this.crosshair.y);
        ctx.lineTo(this.canvas.width, this.crosshair.y);
        ctx.stroke();

        ctx.restore();
    }

    attachEventListeners() {
        window.addEventListener('resize', () => {
            this.setupCanvas();
            if (this.chart) {
                this.chart.resize();
            }
        });

        this.canvas.addEventListener('click', (event) => {
            const rect = this.canvas.getBoundingClientRect();
            const x = event.clientX - rect.left;
            const y = event.clientY - rect.top;

            // 获取点击位置的数据点
            if (this.chart) {
                const points = this.chart.getElementsAtEventForMode(event, 'nearest', { intersect: true }, true);
                if (points.length) {
                    const point = points[0];
                    const dataset = this.chart.data.datasets[point.datasetIndex];
                    const data = dataset.data[point.index];
                    this.showDataPointInfo(data, x, y);
                }
            }
        });
    }

    showDataPointInfo(data, x, y) {
        // 创建或更新提示框
        let tooltip = document.getElementById('chart-tooltip');
        if (!tooltip) {
            tooltip = document.createElement('div');
            tooltip.id = 'chart-tooltip';
            tooltip.style.cssText = `
                position: absolute;
                background: white;
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 10px;
                font-size: 12px;
                pointer-events: none;
                z-index: 1000;
                box-shadow: 0 2px 8px rgba(0,0,0,0.2);
            `;
            document.body.appendChild(tooltip);
        }

        tooltip.innerHTML = `
            <div><strong>开盘:</strong> ${data.o}</div>
            <div><strong>最高:</strong> ${data.h}</div>
            <div><strong>最低:</strong> ${data.l}</div>
            <div><strong>收盘:</strong> ${data.c}</div>
            <div><strong>成交量:</strong> ${data.v}</div>
        `;

        tooltip.style.left = `${x + 10}px`;
        tooltip.style.top = `${y + 10}px`;
        tooltip.style.display = 'block';

        // 3秒后隐藏
        setTimeout(() => {
            tooltip.style.display = 'none';
        }, 3000);
    }

    exportChart(format = 'png') {
        if (!this.chart) return null;

        const url = this.chart.toBase64Image();
        const link = document.createElement('a');
        link.download = `chart.${format}`;
        link.href = url;
        link.click();
    }

    destroy() {
        if (this.chart) {
            this.chart.destroy();
        }
        this.disableCrosshair();
    }
}

// 模拟数据生成器
function generateMockStockData(days = 100) {
    const data = {
        prices: [],
        volumes: []
    };

    let price = 100;
    const now = Date.now();
    const dayMs = 24 * 60 * 60 * 1000;

    for (let i = days; i >= 0; i--) {
        const date = new Date(now - i * dayMs);
        const change = (Math.random() - 0.5) * 5;
        const open = price;
        const close = Math.max(1, price + change);
        const high = Math.max(open, close) + Math.random() * 2;
        const low = Math.min(open, close) - Math.random() * 2;
        const volume = Math.floor(Math.random() * 1000000) + 500000;

        data.prices.push({
            x: date,
            o: open,
            h: high,
            l: low,
            c: close
        });

        data.volumes.push({
            x: date,
            v: volume
        });

        price = close;
    }

    return data;
}

// 自动初始化
document.addEventListener('DOMContentLoaded', () => {
    // 如果页面中有advanced-chart容器，则初始化
    const chartContainers = document.querySelectorAll('.advanced-chart');
    chartContainers.forEach(container => {
        const canvasId = container.querySelector('canvas').id;
        const chart = new AdvancedChart(canvasId);

        // 加载模拟数据
        setTimeout(() => {
            const mockData = generateMockStockData(30);
            chart.createCandlestickChart(mockData);
        }, 100);
    });
});

// 导出类
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AdvancedChart;
}
