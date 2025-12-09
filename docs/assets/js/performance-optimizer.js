/**
 * 前端性能优化组件
 * 实现虚拟滚动、懒加载、请求合并等功能
 */

class PerformanceOptimizer {
    constructor() {
        this.cache = new Map();
        this.requestQueue = new Map();
        this.maxConcurrentRequests = 5;
        this.currentRequests = 0;
        this.performanceMetrics = {
            renderTime: 0,
            loadTime: 0,
            cacheHitRate: 0,
            requestsOptimized: 0
        };
    }

    // ==================== 虚拟滚动 ====================

    enableVirtualScrolling(containerId, options = {}) {
        const container = document.getElementById(containerId);
        if (!container) {
            console.error(`Container ${containerId} not found`);
            return;
        }

        const config = {
            itemHeight: options.itemHeight || 50,
            bufferSize: options.bufferSize || 10,
            threshold: options.threshold || 5,
            ...options
        };

        const items = Array.from(container.children);
        const totalItems = items.length;
        const visibleCount = Math.ceil(container.clientHeight / config.itemHeight);
        let startIndex = 0;
        let endIndex = visibleCount;

        // 隐藏所有项目
        items.forEach(item => {
            item.style.display = 'none';
        });

        // 渲染可见项目
        const renderVisibleItems = () => {
            const scrollTop = container.scrollTop;
            startIndex = Math.floor(scrollTop / config.itemHeight);
            endIndex = Math.min(
                startIndex + visibleCount + config.bufferSize,
                totalItems
            );
            startIndex = Math.max(0, startIndex - config.bufferSize);

            // 设置容器高度
            container.style.height = `${totalItems * config.itemHeight}px`;
            container.style.position = 'relative';

            // 渲染项目
            items.forEach((item, index) => {
                if (index >= startIndex && index <= endIndex) {
                    item.style.display = '';
                    item.style.position = 'absolute';
                    item.style.top = `${index * config.itemHeight}px`;
                    item.style.left = '0';
                    item.style.width = '100%';
                    item.style.height = `${config.itemHeight}px`;
                } else {
                    item.style.display = 'none';
                }
            });
        };

        // 监听滚动事件
        container.addEventListener('scroll', throttle(renderVisibleItems, 16));

        // 初始渲染
        renderVisibleItems();

        return {
            update: renderVisibleItems,
            destroy: () => {
                container.removeEventListener('scroll', renderVisibleItems);
                items.forEach(item => {
                    item.style.display = '';
                    item.style.position = '';
                    item.style.top = '';
                    item.style.left = '';
                    item.style.width = '';
                    item.style.height = '';
                });
                container.style.height = '';
                container.style.position = '';
            }
        };
    }

    // ==================== 懒加载 ====================

    lazyLoadComponent(selector, loader, options = {}) {
        const config = {
            rootMargin: options.rootMargin || '50px',
            threshold: options.threshold || 0.1,
            ...options
        };

        const elements = document.querySelectorAll(selector);

        if (!('IntersectionObserver' in window)) {
            // 降级方案：直接加载所有
            elements.forEach(el => loader(el));
            return;
        }

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    loader(entry.target);
                    observer.unobserve(entry.target);
                }
            });
        }, config);

        elements.forEach(el => observer.observe(el));

        return {
            disconnect: () => observer.disconnect(),
            observe: (el) => observer.observe(el),
            unobserve: (el) => observer.unobserve(el)
        };
    }

    lazyLoadImages(containerId = 'body', options = {}) {
        const config = {
            selector: 'img[data-src]',
            placeholder: options.placeholder || 'data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7',
            ...options
        };

        const loadImage = (img) => {
            const src = img.getAttribute('data-src');
            if (src) {
                img.src = src;
                img.removeAttribute('data-src');
                img.classList.add('loaded');
            }
        };

        return this.lazyLoadComponent(config.selector, loadImage);
    }

    // ==================== 请求优化 ====================

    async batchRequest(urls, options = {}) {
        const config = {
            batchSize: options.batchSize || 10,
            delay: options.delay || 100,
            ...options
        };

        const cacheKey = urls.sort().join(',');
        const cached = this.getFromCache(cacheKey);
        if (cached) {
            this.performanceMetrics.cacheHitRate++;
            return cached;
        }

        const results = [];
        const batches = [];

        // 分批处理
        for (let i = 0; i < urls.length; i += config.batchSize) {
            batches.push(urls.slice(i, i + config.batchSize));
        }

        // 逐批执行
        for (const batch of batches) {
            const batchResults = await Promise.allSettled(
                batch.map(url => this.fetchWithQueue(url))
            );

            batchResults.forEach((result, index) => {
                if (result.status === 'fulfilled') {
                    results[index] = result.value;
                } else {
                    console.error(`Request failed for ${batch[index]}:`, result.reason);
                    results[index] = null;
                }
            });

            // 批次间延迟
            if (config.delay > 0) {
                await this.delay(config.delay);
            }
        }

        this.setCache(cacheKey, results);
        this.performanceMetrics.requestsOptimized += urls.length;

        return results;
    }

    async fetchWithQueue(url) {
        // 等待可用请求槽
        while (this.currentRequests >= this.maxConcurrentRequests) {
            await this.delay(10);
        }

        this.currentRequests++;

        try {
            const response = await fetch(url);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            return await response.json();
        } finally {
            this.currentRequests--;
        }
    }

    // ==================== 缓存管理 ====================

    getFromCache(key) {
        const cached = this.cache.get(key);
        if (cached && cached.expires > Date.now()) {
            return cached.data;
        }
        if (cached) {
            this.cache.delete(key);
        }
        return null;
    }

    setCache(key, data, ttl = 300000) { // 默认5分钟
        this.cache.set(key, {
            data,
            expires: Date.now() + ttl
        });
    }

    clearCache() {
        this.cache.clear();
    }

    // ==================== 性能监控 ====================

    startMeasure(name) {
        performance.mark(`${name}-start`);
    }

    endMeasure(name) {
        performance.mark(`${name}-end`);
        performance.measure(name, `${name}-start`, `${name}-end`);

        const measure = performance.getEntriesByName(name)[0];
        const duration = measure.duration;

        performance.clearMarks(`${name}-start`);
        performance.clearMarks(`${name}-end`);
        performance.clearMeasures(name);

        return duration;
    }

    measureRenderTime(fn) {
        const start = performance.now();
        const result = fn();
        const end = performance.now();

        this.performanceMetrics.renderTime = end - start;
        return result;
    }

    // ==================== DOM优化 ====================

    batchDOMUpdates(updates) {
        // 使用DocumentFragment批量更新
        const fragment = document.createDocumentFragment();

        updates.forEach(update => {
            const element = typeof update.selector === 'string'
                ? document.querySelector(update.selector)
                : update.selector;

            if (element) {
                if (update.action === 'text') {
                    element.textContent = update.value;
                } else if (update.action === 'html') {
                    element.innerHTML = update.value;
                } else if (update.action === 'style') {
                    Object.assign(element.style, update.styles);
                } else if (update.action === 'class') {
                    element.className = update.value;
                }
            }
        });

        return fragment;
    }

    // ==================== 资源预加载 ====================

    preloadResource(url, type = 'fetch') {
        const link = document.createElement('link');

        if (type === 'fetch') {
            link.rel = 'prefetch';
            link.href = url;
        } else if (type === 'script') {
            link.rel = 'preload';
            link.as = 'script';
            link.href = url;
        } else if (type === 'style') {
            link.rel = 'preload';
            link.as = 'style';
            link.href = url;
        }

        document.head.appendChild(link);
    }

    // ==================== 工具方法 ====================

    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    getPerformanceMetrics() {
        const totalRequests = this.performanceMetrics.requestsOptimized;
        const cacheHitRate = totalRequests > 0
            ? (this.performanceMetrics.cacheHitRate / totalRequests * 100).toFixed(2)
            : 0;

        return {
            ...this.performanceMetrics,
            cacheHitRate: `${cacheHitRate}%`,
            cacheSize: this.cache.size,
            activeRequests: this.currentRequests
        };
    }

    printMetrics() {
        const metrics = this.getPerformanceMetrics();
        console.group('Performance Metrics');
        console.table(metrics);
        console.groupEnd();
    }
}

// ==================== 辅助函数 ====================

function throttle(func, limit) {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// ==================== 使用示例 ====================

// 示例1: 虚拟滚动
function setupVirtualList(listId) {
    const optimizer = new PerformanceOptimizer();
    return optimizer.enableVirtualScrolling(listId, {
        itemHeight: 60,
        bufferSize: 10
    });
}

// 示例2: 图片懒加载
function setupLazyLoad() {
    const optimizer = new PerformanceOptimizer();
    return optimizer.lazyLoadImages();
}

// 示例3: 批量请求优化
async function fetchStockData(stockCodes) {
    const optimizer = new PerformanceOptimizer();
    const urls = stockCodes.map(code => `/api/stocks/${code}`);
    return optimizer.batchRequest(urls);
}

// 示例4: 性能监控
function measureFunctionPerformance(fnName, fn) {
    const optimizer = new PerformanceOptimizer();
    optimizer.startMeasure(fnName);
    const result = optimizer.measureRenderTime(fn);
    optimizer.endMeasure(fnName);
    return result;
}

// 自动初始化
document.addEventListener('DOMContentLoaded', () => {
    // 创建全局实例
    window.performanceOptimizer = new PerformanceOptimizer();

    // 自动设置图片懒加载
    if (document.querySelector('img[data-src]')) {
        window.performanceOptimizer.lazyLoadImages();
    }

    // 监听性能指标
    window.addEventListener('load', () => {
        setTimeout(() => {
            window.performanceOptimizer.printMetrics();
        }, 1000);
    });
});

// 导出类
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PerformanceOptimizer;
}
