/**
 * AI-Trader 认证管理模块
 * 提供前端模拟登录、会话管理和页面访问控制功能
 */

class AuthManager {
    constructor() {
        this.storageKey = 'ai_trader_auth';
        this.userSessionKey = 'ai_trader_session';
        this.tokenKey = 'ai_trader_token';
        this.sessionTimeout = 24 * 60 * 60 * 1000; // 24小时
    }

    /**
     * 用户登录
     * @param {string} username - 用户名
     * @param {string} password - 密码
     * @returns {Promise<boolean>} 登录是否成功
     */
    async login(username, password) {
        try {
            const config = await this.loadConfig();
            const users = config.users || this.getDefaultUsers();

            const user = users.find(u => u.username === username && u.password === password);

            if (user) {
                const session = {
                    username: user.username,
                    loginTime: Date.now(),
                    lastAccessTime: Date.now(),
                    token: this.generateToken()
                };

                localStorage.setItem(this.storageKey, JSON.stringify(session));
                localStorage.setItem(this.userSessionKey, JSON.stringify({
                    username: user.username,
                    displayName: user.displayName || user.username,
                    avatar: user.avatar || '📊'
                }));
                localStorage.setItem(this.tokenKey, session.token);

                return true;
            }

            return false;
        } catch (error) {
            console.error('登录失败:', error);
            return false;
        }
    }

    /**
     * 用户注销
     */
    logout() {
        localStorage.removeItem(this.storageKey);
        localStorage.removeItem(this.userSessionKey);
        localStorage.removeItem(this.tokenKey);
        window.location.href = 'login.html';
    }

    /**
     * 检查是否已登录
     * @returns {boolean}
     */
    isLoggedIn() {
        const session = this.getSession();
        if (!session) return false;

        const now = Date.now();
        const timeSinceLastAccess = now - session.lastAccessTime;

        if (timeSinceLastAccess > this.sessionTimeout) {
            this.logout();
            return false;
        }

        session.lastAccessTime = now;
        localStorage.setItem(this.storageKey, JSON.stringify(session));

        return true;
    }

    /**
     * 获取当前会话信息
     * @returns {Object|null}
     */
    getSession() {
        try {
            const sessionStr = localStorage.getItem(this.storageKey);
            return sessionStr ? JSON.parse(sessionStr) : null;
        } catch (error) {
            console.error('获取会话信息失败:', error);
            return null;
        }
    }

    /**
     * 获取当前用户信息
     * @returns {Object|null}
     */
    getCurrentUser() {
        try {
            const userStr = localStorage.getItem(this.userSessionKey);
            return userStr ? JSON.parse(userStr) : null;
        } catch (error) {
            console.error('获取用户信息失败:', error);
            return null;
        }
    }

    /**
     * 获取访问令牌
     * @returns {string|null}
     */
    getToken() {
        return localStorage.getItem(this.tokenKey);
    }

    /**
     * 检查页面访问权限
     * 如果未登录则重定向到登录页
     */
    checkAuth() {
        if (!this.isLoggedIn()) {
            window.location.href = 'login.html';
        }
    }

    /**
     * 加载配置文件
     * @returns {Promise<Object>}
     */
    async loadConfig() {
        try {
            const response = await fetch('config.yaml');
            const yamlText = await response.text();

            // 使用js-yaml解析YAML
            if (typeof jsyaml !== 'undefined') {
                return jsyaml.load(yamlText);
            }

            // 如果没有js-yaml，返回默认配置
            return this.getDefaultConfig();
        } catch (error) {
            console.warn('加载配置文件失败，使用默认配置:', error);
            return this.getDefaultConfig();
        }
    }

    /**
     * 获取默认用户列表（调试阶段使用）
     * @returns {Array}
     */
    getDefaultUsers() {
        return [
            {
                username: 'admin',
                password: 'admin123',
                displayName: '管理员'
            },
            {
                username: 'user',
                password: 'user123',
                displayName: '用户'
            },
            {
                username: 'demo',
                password: 'demo123',
                displayName: '演示用户'
            }
        ];
    }

    /**
     * 获取默认配置
     * @returns {Object}
     */
    getDefaultConfig() {
        return {
            users: this.getDefaultUsers()
        };
    }

    /**
     * 生成随机令牌
     * @returns {string}
     */
    generateToken() {
        const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
        let token = '';
        for (let i = 0; i < 32; i++) {
            token += chars.charAt(Math.floor(Math.random() * chars.length));
        }
        return token;
    }

    /**
     * 刷新会话
     */
    refreshSession() {
        const session = this.getSession();
        if (session) {
            session.lastAccessTime = Date.now();
            localStorage.setItem(this.storageKey, JSON.stringify(session));
        }
    }

    /**
     * 获取用户头像
     * @returns {string}
     */
    getUserAvatar() {
        const user = this.getCurrentUser();
        return user?.avatar || '📊';
    }

    /**
     * 获取用户显示名
     * @returns {string}
     */
    getUserDisplayName() {
        const user = this.getCurrentUser();
        return user?.displayName || user?.username || '用户';
    }
}

/**
 * 创建导航栏用户信息显示组件
 * @param {HTMLElement} container - 容器元素
 */
function createUserInfoComponent(container) {
    const authManager = new AuthManager();
    const user = authManager.getCurrentUser();

    if (!user) return;

    container.innerHTML = `
        <div class="user-info-dropdown">
            <button class="user-info-trigger">
                <span class="user-avatar">${user.avatar}</span>
                <span class="user-name">${user.displayName}</span>
                <svg class="dropdown-arrow" width="12" height="12" viewBox="0 0 12 12">
                    <path d="M6 9L1 4h10l-5 5z" fill="currentColor"/>
                </svg>
            </button>
            <div class="user-info-menu">
                <div class="menu-item">
                    <span class="menu-icon">👤</span>
                    <span class="menu-text">${user.displayName}</span>
                </div>
                <div class="menu-divider"></div>
                <button class="menu-item" onclick="authManager.logout()">
                    <span class="menu-icon">🚪</span>
                    <span class="menu-text">退出登录</span>
                </button>
            </div>
        </div>
    `;
}

/**
 * 页面加载完成后初始化认证
 */
document.addEventListener('DOMContentLoaded', () => {
    // 在需要认证的页面检查登录状态
    const currentPage = window.location.pathname.split('/').pop();
    const authRequiredPages = ['index.html', 'portfolio.html', 'ai-reasoning.html', 'market.html'];

    if (authRequiredPages.includes(currentPage) && currentPage !== 'login.html') {
        const authManager = new AuthManager();
        authManager.checkAuth();

        // 每5分钟刷新一次会话
        setInterval(() => {
            authManager.refreshSession();
        }, 5 * 60 * 1000);
    }

    // 如果在登录页且已登录，重定向到主页
    if (currentPage === 'login.html') {
        const authManager = new AuthManager();
        if (authManager.isLoggedIn()) {
            window.location.href = 'index.html';
        }
    }
});

/**
 * 为导航栏添加用户信息
 */
function initNavbarUserInfo() {
    const navbar = document.querySelector('.navbar .nav-container');
    if (!navbar) return;

    let userInfoSection = navbar.querySelector('.user-info-section');
    if (userInfoSection) return;

    userInfoSection = document.createElement('div');
    userInfoSection.className = 'user-info-section';
    createUserInfoComponent(userInfoSection);
    navbar.appendChild(userInfoSection);

    // 添加下拉菜单样式
    const style = document.createElement('style');
    style.textContent = `
        .user-info-section {
            margin-left: auto;
        }

        .user-info-dropdown {
            position: relative;
        }

        .user-info-trigger {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 8px 16px;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            color: #fff;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .user-info-trigger:hover {
            background: rgba(255, 255, 255, 0.1);
        }

        .user-avatar {
            font-size: 20px;
        }

        .user-name {
            font-size: 14px;
        }

        .dropdown-arrow {
            transition: transform 0.3s ease;
        }

        .user-info-dropdown:hover .dropdown-arrow {
            transform: rotate(180deg);
        }

        .user-info-menu {
            position: absolute;
            top: 100%;
            right: 0;
            margin-top: 10px;
            background: rgba(26, 26, 46, 0.95);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            padding: 8px;
            min-width: 180: none;
            box-shadow: px;
            display0 4px 20px rgba(0, 0, 0, 0.3);
        }

        .user-info-dropdown:hover .user-info-menu {
            display: block;
        }

        .menu-item {
            display: flex;
            align-items: center;
            gap: 12px;
            width: 100%;
            padding: 10px 12px;
            background: none;
            border: none;
            color: #fff;
            cursor: pointer;
            border-radius: 8px;
            transition: background 0.2s ease;
        }

        .menu-item:hover {
            background: rgba(255, 255, 255, 0.05);
        }

        .menu-icon {
            font-size: 16px;
        }

        .menu-text {
            font-size: 14px;
        }

        .menu-divider {
            height: 1px;
            background: rgba(255, 255, 255, 0.1);
            margin: 4px 0;
        }
    `;
    document.head.appendChild(style);
}

// 页面加载完成后初始化
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initNavbarUserInfo);
} else {
    initNavbarUserInfo();
}
