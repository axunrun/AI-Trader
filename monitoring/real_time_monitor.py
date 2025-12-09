#!/usr/bin/env python3
"""
实时监控与告警系统
提供全方位的交易监控和智能告警功能
"""

import asyncio
import json
import smtplib
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Callable, Optional, Any
from pathlib import Path
from dataclasses import dataclass, asdict
try:
    from email.mime.text import MimeText
    from email.mime.multipart import MimeMultipart
except ImportError:
    # Windows兼容性问题处理
    MimeText = None
    MimeMultipart = None


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('monitoring.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class AlertRule:
    """告警规则配置"""
    name: str
    condition: Callable
    callback: Callable
    cooldown_minutes: int = 5
    enabled: bool = True
    last_triggered: Optional[datetime] = None
    trigger_count: int = 0
    severity: str = 'medium'  # low, medium, high, critical


@dataclass
class AlertEvent:
    """告警事件"""
    rule_name: str
    timestamp: datetime
    severity: str
    message: str
    data: Dict[str, Any]
    acknowledged: bool = False


class TelegramNotifier:
    """电报通知器"""

    def __init__(self, token: str = None, chat_id: str = None):
        self.token = token
        self.chat_id = chat_id
        self.enabled = token is not None and chat_id is not None

    async def send_message(self, message: str, parse_mode: str = 'HTML') -> bool:
        """发送电报消息"""
        if not self.enabled:
            logger.warning("Telegram notifier not configured")
            return False

        try:
            # 这里使用requests代替aiohttp避免依赖问题
            import requests

            url = f"https://api.telegram.org/bot{self.token}/sendMessage"
            data = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': parse_mode
            }

            response = requests.post(url, data=data, timeout=10)
            if response.status_code == 200:
                logger.info("Telegram notification sent successfully")
                return True
            else:
                logger.error(f"Failed to send Telegram message: {response.text}")
                return False
        except Exception as e:
            logger.error(f"Telegram notification error: {e}")
            return False


class EmailNotifier:
    """邮件通知器"""

    def __init__(self, smtp_server: str, smtp_port: int, username: str, password: str, from_addr: str, to_addrs: List[str]):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.from_addr = from_addr
        self.to_addrs = to_addrs

    async def send_email(self, subject: str, body: str, html_body: str = None) -> bool:
        """发送邮件"""
        if MimeText is None or MimeMultipart is None:
            logger.warning("Email module not available, skipping email notification")
            return False

        try:
            msg = MimeMultipart()
            msg['From'] = self.from_addr
            msg['To'] = ', '.join(self.to_addrs)
            msg['Subject'] = subject

            msg.attach(MimeText(body, 'plain', 'utf-8'))
            if html_body:
                msg.attach(MimeText(html_body, 'html', 'utf-8'))

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)

            logger.info(f"Email notification sent: {subject}")
            return True
        except Exception as e:
            logger.error(f"Email notification error: {e}")
            return False


class RealTimeMonitor:
    """实时监控与告警系统"""

    def __init__(self, config_path: str = None):
        self.alert_rules: Dict[str, AlertRule] = {}
        self.alert_history: List[AlertEvent] = []
        self.is_running = False
        self.notifiers = {
            'telegram': None,
            'email': None
        }

        # 加载配置
        if config_path:
            self.load_config(config_path)

    def load_config(self, config_path: str):
        """加载配置文件"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            # 配置电报
            if 'telegram' in config:
                tg_config = config['telegram']
                self.notifiers['telegram'] = TelegramNotifier(
                    token=tg_config.get('token'),
                    chat_id=tg_config.get('chat_id')
                )

            # 配置邮件
            if 'email' in config:
                email_config = config['email']
                self.notifiers['email'] = EmailNotifier(
                    smtp_server=email_config.get('smtp_server'),
                    smtp_port=email_config.get('smtp_port', 587),
                    username=email_config.get('username'),
                    password=email_config.get('password'),
                    from_addr=email_config.get('from'),
                    to_addrs=email_config.get('to', [])
                )

            logger.info("Monitor configuration loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load config: {e}")

    def add_alert_rule(self, rule: AlertRule):
        """添加告警规则"""
        self.alert_rules[rule.name] = rule
        logger.info(f"Alert rule added: {rule.name}")

    def remove_alert_rule(self, rule_name: str):
        """移除告警规则"""
        if rule_name in self.alert_rules:
            del self.alert_rules[rule_name]
            logger.info(f"Alert rule removed: {rule_name}")

    async def start_monitoring(self):
        """启动实时监控"""
        self.is_running = True
        logger.info("Real-time monitoring started")

        while self.is_running:
            try:
                await self._check_all_rules()
                await asyncio.sleep(60)  # 每分钟检查一次
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                await asyncio.sleep(60)

    async def stop_monitoring(self):
        """停止监控"""
        self.is_running = False
        logger.info("Real-time monitoring stopped")

    async def _check_all_rules(self):
        """检查所有规则"""
        for rule_name, rule in self.alert_rules.items():
            if not rule.enabled:
                continue

            try:
                if rule.condition():
                    await self._trigger_alert(rule)
            except Exception as e:
                logger.error(f"Error checking rule {rule_name}: {e}")

    async def _trigger_alert(self, rule: AlertRule):
        """触发告警"""
        now = datetime.now()

        # 检查冷却时间
        if (rule.last_triggered and
            now - rule.last_triggered < timedelta(minutes=rule.cooldown_minutes)):
            return

        # 更新规则状态
        rule.last_triggered = now
        rule.trigger_count += 1

        # 创建告警事件
        event = AlertEvent(
            rule_name=rule.name,
            timestamp=now,
            severity=rule.severity,
            message=f"Alert triggered: {rule.name}",
            data={'trigger_count': rule.trigger_count}
        )

        self.alert_history.append(event)

        # 执行回调
        try:
            await rule.callback(event)
        except Exception as e:
            logger.error(f"Alert callback error: {e}")

        logger.warning(f"Alert triggered: {rule.name} (count: {rule.trigger_count})")

    async def send_notification(self, channel: str, message: str, subject: str = None) -> bool:
        """发送通知"""
        notifier = self.notifiers.get(channel)
        if not notifier:
            logger.warning(f"Notifier not configured: {channel}")
            return False

        if channel == 'telegram':
            return await notifier.send_message(message)
        elif channel == 'email':
            if subject is None:
                subject = "AI-Trader Alert"
            return await notifier.send_email(subject, message)
        else:
            logger.error(f"Unknown notification channel: {channel}")
            return False

    def get_alert_history(self, hours: int = 24) -> List[AlertEvent]:
        """获取告警历史"""
        cutoff = datetime.now() - timedelta(hours=hours)
        return [event for event in self.alert_history if event.timestamp >= cutoff]

    def get_statistics(self) -> Dict[str, Any]:
        """获取监控统计"""
        total_alerts = len(self.alert_history)
        recent_alerts = len(self.get_alert_history(24))

        severity_counts = {}
        for event in self.alert_history:
            severity_counts[event.severity] = severity_counts.get(event.severity, 0) + 1

        return {
            'total_alerts': total_alerts,
            'recent_alerts_24h': recent_alerts,
            'active_rules': len([r for r in self.alert_rules.values() if r.enabled]),
            'severity_distribution': severity_counts,
            'uptime': datetime.now().isoformat()
        }

    def add_predefined_alerts(self, market_data_getter: Callable):
        """添加预定义告警规则"""
        # 大幅回撤告警
        self.add_alert_rule(AlertRule(
            name='large_drawdown',
            condition=lambda: self._check_large_drawdown(market_data_getter),
            callback=lambda event: self._send_drawdown_alert(event, market_data_getter),
            severity='critical',
            cooldown_minutes=10
        ))

        # 异常交易告警
        self.add_alert_rule(AlertRule(
            name='unusual_trade',
            condition=lambda: self._check_unusual_trades(market_data_getter),
            callback=lambda event: self._send_trade_alert(event),
            severity='high',
            cooldown_minutes=5
        ))

        # 数据质量告警
        self.add_alert_rule(AlertRule(
            name='data_quality',
            condition=lambda: self._check_data_quality(market_data_getter),
            callback=lambda event: self._send_data_quality_alert(event),
            severity='medium',
            cooldown_minutes=30
        ))

        # 高波动率告警
        self.add_alert_rule(AlertRule(
            name='high_volatility',
            condition=lambda: self._check_high_volatility(market_data_getter),
            callback=lambda event: self._send_volatility_alert(event),
            severity='high',
            cooldown_minutes=15
        ))

        # 异常成交量告警
        self.add_alert_rule(AlertRule(
            name='unusual_volume',
            condition=lambda: self._check_unusual_volume(market_data_getter),
            callback=lambda event: self._send_volume_alert(event),
            severity='medium',
            cooldown_minutes=20
        ))

    def _check_large_drawdown(self, market_data_getter: Callable) -> bool:
        """检查大幅回撤"""
        try:
            data = market_data_getter()
            current_value = data.get('portfolio_value', 0)
            peak_value = data.get('peak_value', current_value)

            if peak_value == 0:
                return False

            drawdown_pct = (peak_value - current_value) / peak_value * 100
            return drawdown_pct > 10  # 回撤超过10%
        except Exception as e:
            logger.error(f"Error checking drawdown: {e}")
            return False

    def _check_unusual_trades(self, market_data_getter: Callable) -> bool:
        """检查异常交易"""
        try:
            data = market_data_getter()
            recent_trades = data.get('recent_trades', [])

            # 检查是否有大额交易
            for trade in recent_trades:
                amount = trade.get('amount', 0)
                if amount > 100000:  # 单笔交易超过10万股
                    return True

            return False
        except Exception as e:
            logger.error(f"Error checking unusual trades: {e}")
            return False

    def _check_data_quality(self, market_data_getter: Callable) -> bool:
        """检查数据质量"""
        try:
            data = market_data_getter()
            quality_score = data.get('data_quality_score', 100)

            return quality_score < 80  # 数据质量低于80分
        except Exception as e:
            logger.error(f"Error checking data quality: {e}")
            return False

    def _check_high_volatility(self, market_data_getter: Callable) -> bool:
        """检查高波动率"""
        try:
            data = market_data_getter()
            volatility = data.get('portfolio_volatility', 0)

            return volatility > 25  # 波动率超过25%
        except Exception as e:
            logger.error(f"Error checking volatility: {e}")
            return False

    def _check_unusual_volume(self, market_data_getter: Callable) -> bool:
        """检查异常成交量"""
        try:
            data = market_data_getter()
            current_volume = data.get('current_volume', 0)
            avg_volume = data.get('avg_volume', 0)

            if avg_volume == 0:
                return False

            volume_ratio = current_volume / avg_volume
            return volume_ratio > 3  # 成交量是平均值的3倍以上
        except Exception as e:
            logger.error(f"Error checking volume: {e}")
            return False

    async def _send_drawdown_alert(self, event: AlertEvent, market_data_getter: Callable):
        """发送回撤告警"""
        data = market_data_getter()
        current_drawdown = data.get('drawdown_pct', 0)

        message = f"""
🚨 Large Drawdown Alert

Current Drawdown: {current_drawdown:.2f}%
Trigger Time: {event.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
Rule: {event.rule_name}

建议立即采取风险控制措施。
建议：
1. 减仓至安全水平
2. 评估市场环境
3. 调整投资策略
        """

        await self.send_notification('telegram', message, 'Large Drawdown Alert')

    async def _send_trade_alert(self, event: AlertEvent):
        """发送交易告警"""
        message = f"""
📈 Unusual Trade Alert

Alert: {event.rule_name}
Time: {event.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
Severity: {event.severity.upper()}

检测到异常交易行为，请及时关注。
        """

        await self.send_notification('telegram', message, 'Unusual Trade Alert')

    async def _send_data_quality_alert(self, event: AlertEvent):
        """发送数据质量告警"""
        message = f"""
⚠️ Data Quality Alert

Alert: {event.rule_name}
Time: {event.timestamp.strftime('%Y-%m-%d %H:%M:%S')}

数据质量低于预期，可能影响AI决策准确性。
建议检查数据源和采集系统。
        """

        await self.send_notification('email', message, 'Data Quality Alert')

    async def _send_volatility_alert(self, event: AlertEvent):
        """发送波动率告警"""
        message = f"""
📊 High Volatility Alert

Alert: {event.rule_name}
Time: {event.timestamp.strftime('%Y-%m-%d %H:%M:%S')}

市场波动率异常升高，建议提高风险意识。
        """

        await self.send_notification('telegram', message, 'High Volatility Alert')

    async def _send_volume_alert(self, event: AlertEvent):
        """发送成交量告警"""
        message = f"""
📈 Unusual Volume Alert

Alert: {event.rule_name}
Time: {event.timestamp.strftime('%Y-%m-%d %H:%M:%S')}

成交量异常放量，可能存在重大市场事件。
        """

        await self.send_notification('telegram', message, 'Unusual Volume Alert')


if __name__ == "__main__":
    # 测试代码
    def mock_market_data_getter():
        """模拟市场数据获取器"""
        import random
        return {
            'portfolio_value': 100000 + random.randint(-20000, 20000),
            'peak_value': 120000,
            'drawdown_pct': random.uniform(0, 15),
            'recent_trades': [
                {'amount': 150000, 'symbol': '600519.SH'},
                {'amount': 80000, 'symbol': '000001.SZ'}
            ],
            'data_quality_score': random.uniform(70, 95),
            'portfolio_volatility': random.uniform(15, 35),
            'current_volume': random.randint(500000, 3000000),
            'avg_volume': 1000000
        }

    async def main():
        monitor = RealTimeMonitor()

        # 添加预定义告警
        monitor.add_predefined_alerts(mock_market_data_getter)

        # 启动监控（测试用，只运行1分钟）
        logger.info("Starting monitor test (60 seconds)...")
        monitor_task = asyncio.create_task(monitor.start_monitoring())

        await asyncio.sleep(60)
        await monitor.stop_monitoring()
        monitor_task.cancel()

        # 打印统计信息
        stats = monitor.get_statistics()
        print("\n" + "="*60)
        print("Monitor Statistics:")
        print(json.dumps(stats, indent=2, default=str))
        print("="*60)

    # 运行测试
    asyncio.run(main())
