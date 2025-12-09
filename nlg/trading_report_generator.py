#!/usr/bin/env python3
"""
自然语言生成交易报告系统
基于AI技术自动生成专业的A股交易分析报告
"""

import json
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path


class TradingReportGenerator:
    """交易报告自然语言生成器"""

    def __init__(self):
        self.templates = self._load_templates()
        self.sentiment_words = self._load_sentiment_words()

    def _load_templates(self) -> Dict[str, str]:
        """加载报告模板"""
        return {
            # 市场概况模板
            'market_overview_up': "今日{market_name}整体呈现上涨态势，主要指数{major_indices}均录得{change_pct}的涨幅。成交额达到{volume}亿元，较昨日{volume_trend}。市场活跃度{activity_level}。",
            'market_overview_down': "今日{market_name}整体呈现下跌态势，主要指数{major_indices}均出现{change_pct}的跌幅。成交额达到{volume}亿元，较昨日{volume_trend}。市场情绪偏向{emotion}。",
            'market_overview_neutral': "今日{market_name}整体呈现横盘整理态势，主要指数{major_indices}涨跌幅均在{change_pct}以内。成交额达到{volume}亿元，市场表现相对平静。",

            # 股票分析模板
            'stock_analysis_up': "{stock_name}({stock_code})今日表现{performance}，当前价格¥{price}，{涨跌幅}，成交量{volume}万股。该股票在{行业}板块中{行业表现}。",
            'stock_analysis_down': "{stock_name}({stock_code})今日表现{performance}，当前价格¥{price}，{涨跌幅}，成交量{volume}万股。技术面上呈现{signal}信号，需关注{support_level}支撑位。",

            # 决策推理模板
            'decision_reasoning_bullish': "基于{indicators}的综合分析，该股票展现出{signal}信号。{technical_analysis}，{fundamental_analysis}，因此建议{action}。置信度为{confidence}%。",
            'decision_reasoning_bearish': "综合{indicators}分析，该股票出现{bearish_signal}特征。{risk_analysis}，考虑到{systematic_risk}，建议{action}以控制风险。",
            'decision_reasoning_neutral': "根据{indicators}分析，该股票呈现{neutral_signal}特征。{market_environment}，建议采取{action}策略，密切关注{monitoring_points}。",

            # 风险评估模板
            'risk_assessment_high': "当前投资组合面临较高的{risk_type}风险，组合波动率达到{volatility}%。{risk_details}，建议采取{mitigation_strategy}措施。",
            'risk_assessment_medium': "当前投资组合面临中等程度的{risk_type}风险，组合波动率为{volatility}%。{risk_details}，建议{recommendation}。",
            'risk_assessment_low': "当前投资组合风险水平{risk_level}，组合波动率为{volatility}%。{risk_details}，建议继续保持当前策略。",

            # 交易执行模板
            'trade_execution_success': "成功执行{action}操作：{amount}股{stock_code}，成交价格¥{price}，{execution_time}。{order_details}。",
            'trade_execution_failed': "尝试执行{action}操作：{amount}股{stock_code}，但因{reason}导致交易失败。建议{alternative_action}。",

            # 组合分析模板
            'portfolio_analysis': "当前投资组合包含{stock_count}只股票，总市值¥{total_value}，今日{performance}。行业分布：{sector_allocation}。风险指标：夏普比率{sharpe}，最大回撤{max_drawdown}%。",
        }

    def _load_sentiment_words(self) -> Dict[str, List[str]]:
        """加载情感词汇"""
        return {
            'positive': ['上涨', '突破', '拉升', '强势', '看涨', '积极', '利好', '创新高', '反弹'],
            'negative': ['下跌', '破位', '回调', '弱势', '看跌', '消极', '利空', '创新低', '回落'],
            'neutral': ['横盘', '震荡', '整理', '平稳', '观望', '谨慎', '平衡', '波动', '稳定']
        }

    def generate_daily_report(self, trading_data: Dict) -> str:
        """生成日报"""
        report_sections = []

        # 报告头部
        report_header = self._generate_report_header(trading_data.get('date'))
        report_sections.append(report_header)

        # 市场概况
        if 'market' in trading_data:
            market_section = self._generate_market_section(trading_data['market'])
            report_sections.append(f"\n## 📊 Market Overview\n\n{market_section}\n")

        # 持仓分析
        if 'holdings' in trading_data:
            holdings_section = self._generate_holdings_section(trading_data['holdings'])
            report_sections.append(f"\n## 💼 Portfolio Analysis\n\n{holdings_section}\n")

        # 交易记录
        if 'trades' in trading_data:
            trades_section = self._generate_trades_section(trading_data['trades'])
            report_sections.append(f"\n## 📈 Trading Records\n\n{trades_section}\n")

        # AI决策分析
        if 'decisions' in trading_data:
            decisions_section = self._generate_decisions_section(trading_data['decisions'])
            report_sections.append(f"\n## 🧠 AI Decision Analysis\n\n{decisions_section}\n")

        # 风险评估
        if 'risk' in trading_data:
            risk_section = self._generate_risk_section(trading_data['risk'])
            report_sections.append(f"\n## ⚠️ Risk Assessment\n\n{risk_section}\n")

        # 市场展望
        outlook_section = self._generate_market_outlook(trading_data)
        report_sections.append(f"\n## 🔮 Market Outlook\n\n{outlook_section}\n")

        return "\n".join(report_sections)

    def _generate_report_header(self, date: str = None) -> str:
        """生成报告头部"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')

        return f"""
# AI-Trader Daily Trading Report

**Date:** {date}
**Generated by:** AI-Trader v2.0
**Report Type:** Daily Summary
**Language:** Chinese/English
"""

    def _generate_market_section(self, market_data: Dict) -> str:
        """生成市场分析段落"""
        # 分析市场趋势
        change = market_data.get('change_pct', 0)
        if change > 1:
            template = self.templates['market_overview_up']
        elif change < -1:
            template = self.templates['market_overview_down']
        else:
            template = self.templates['market_overview_neutral']

        # 生成内容
        section = template.format(
            market_name=market_data.get('name', 'A股市场'),
            major_indices=market_data.get('indices', ['上证指数', '深证成指', '创业板指']),
            change_pct=f"{abs(change):.2f}%" if change != 0 else "小幅",
            volume=market_data.get('volume', 0),
            volume_trend=self._analyze_volume_trend(market_data.get('volume_change', 0)),
            activity_level=self._assess_market_activity(market_data.get('turnover_rate', 0)),
            emotion=market_data.get('sentiment', '谨慎')
        )

        # 添加行业表现
        if 'sectors' in market_data:
            sector_analysis = self._analyze_sector_performance(market_data['sectors'])
            section += f"\n\n**Sector Performance:** {sector_analysis}"

        return section

    def _generate_holdings_section(self, holdings_data: List[Dict]) -> str:
        """生成持仓分析段落"""
        if not holdings_data:
            return "No holdings data available."

        sections = []
        total_value = sum(h.get('current_value', 0) for h in holdings_data)
        total_pnl = sum(h.get('pnl', 0) for h in holdings_data)

        # 总体概览
        overall = f"Current portfolio contains {len(holdings_data)} stocks with total market value ¥{total_value:,.2f}. "
        overall += f"Total P&L: ¥{total_pnl:,.2f} ({total_pnl/total_value*100:.2f}%).\n"
        sections.append(overall)

        # 详细持仓
        sections.append("\n**Individual Holdings:**\n")
        for holding in holdings_data:
            template = self.templates['stock_analysis_up']
            if holding.get('change_pct', 0) < 0:
                template = self.templates['stock_analysis_down']

            pnl_text = f"盈利¥{holding.get('pnl', 0):.2f}" if holding.get('pnl', 0) > 0 else f"亏损¥{abs(holding.get('pnl', 0)):.2f}"

            section = template.format(
                stock_name=holding.get('name', 'Unknown'),
                stock_code=holding.get('code', ''),
                performance=self._get_performance_label(holding.get('change_pct', 0)),
                price=holding.get('price', 0),
                涨跌幅=f"{holding.get('change_pct', 0):+.2f}%",
                volume=holding.get('volume', 0),
                行业=holding.get('sector', '未知'),
                行业表现=holding.get('sector_performance', '表现平稳'),
                signal=holding.get('technical_signal', '中性信号'),
                support_level=holding.get('support_level', '关键支撑位')
            )
            sections.append(f"- {section}\n")

        # 行业分布
        sector_allocation = self._calculate_sector_allocation(holdings_data)
        sections.append(f"\n**Sector Allocation:** {sector_allocation}")

        return "".join(sections)

    def _generate_trades_section(self, trades_data: List[Dict]) -> str:
        """生成交易记录段落"""
        if not trades_data:
            return "No trades executed today."

        sections = []
        for trade in trades_data:
            if trade.get('status') == 'success':
                template = self.templates['trade_execution_success']
            else:
                template = self.templates['trade_execution_failed']

            section = template.format(
                action=trade.get('action', ''),
                amount=trade.get('amount', 0),
                stock_code=trade.get('symbol', ''),
                price=trade.get('price', 0),
                execution_time=trade.get('timestamp', ''),
                order_details=trade.get('details', ''),
                reason=trade.get('error_reason', '未知原因'),
                alternative_action=trade.get('suggested_action', '观望')
            )
            sections.append(f"- {section}\n")

        # 交易统计
        total_trades = len(trades_data)
        successful_trades = sum(1 for t in trades_data if t.get('status') == 'success')
        win_rate = successful_trades / total_trades * 100 if total_trades > 0 else 0

        sections.append(f"\n**Trading Statistics:**")
        sections.append(f"- Total Trades: {total_trades}")
        sections.append(f"- Success Rate: {win_rate:.1f}%")
        sections.append(f"- Total Volume: {sum(t.get('amount', 0) for t in trades_data):,}")

        return "".join(sections)

    def _generate_decisions_section(self, decisions_data: List[Dict]) -> str:
        """生成AI决策分析段落"""
        sections = []

        for decision in decisions_data:
            confidence = decision.get('confidence', 50)
            sentiment = decision.get('sentiment', 'neutral')

            if sentiment == 'bullish':
                template = self.templates['decision_reasoning_bullish']
            elif sentiment == 'bearish':
                template = self.templates['decision_reasoning_bearish']
            else:
                template = self.templates['decision_reasoning_neutral']

            section = template.format(
                indicators=decision.get('indicators_used', ['技术指标', '基本面']),
                signal=decision.get('signal', '中性信号'),
                bullish_signal=decision.get('bearish_signal', '卖出信号'),
                neutral_signal=decision.get('neutral_signal', '观望信号'),
                technical_analysis=decision.get('technical_analysis', '技术面分析显示...'),
                fundamental_analysis=decision.get('fundamental_analysis', '基本面分析表明...'),
                risk_analysis=decision.get('risk_analysis', '风险分析指出...'),
                systematic_risk=decision.get('systematic_risk', '系统性风险'),
                market_environment=decision.get('market_environment', '当前市场环境'),
                action=decision.get('recommended_action', '持有观望'),
                monitoring_points=decision.get('monitoring_points', '关键价位'),
                confidence=f"{confidence:.1f}"
            )

            sections.append(f"\n**Decision for {decision.get('symbol', 'N/A')}:**\n{section}")

        return "\n".join(sections)

    def _generate_risk_section(self, risk_data: Dict) -> str:
        """生成风险评估段落"""
        risk_level = risk_data.get('level', 'medium')
        risk_type = risk_data.get('type', '市场风险')

        if risk_level == 'high':
            template = self.templates['risk_assessment_high']
        elif risk_level == 'low':
            template = self.templates['risk_assessment_low']
        else:
            template = self.templates['risk_assessment_medium']

        section = template.format(
            risk_type=risk_type,
            risk_level=risk_level,
            volatility=risk_data.get('volatility', 0),
            risk_details=risk_data.get('details', ''),
            mitigation_strategy=risk_data.get('mitigation', '分散投资'),
            recommendation=risk_data.get('recommendation', '保持谨慎')
        )

        # 添加风险指标
        if 'metrics' in risk_data:
            metrics = risk_data['metrics']
            section += f"\n\n**Key Risk Metrics:**"
            section += f"\n- Value at Risk (VaR): {metrics.get('var', 'N/A')}"
            section += f"\n- Sharpe Ratio: {metrics.get('sharpe', 'N/A')}"
            section += f"\n- Maximum Drawdown: {metrics.get('max_drawdown', 'N/A')}%"

        return section

    def _generate_market_outlook(self, trading_data: Dict) -> str:
        """生成市场展望"""
        outlook = trading_data.get('outlook', {})
        sentiment = outlook.get('sentiment', 'neutral')
        key_factors = outlook.get('key_factors', [])

        section = f"Based on comprehensive analysis, market outlook is {sentiment}.\n\n"
        section += "**Key Factors to Monitor:**\n"

        for factor in key_factors:
            section += f"- {factor}\n"

        # 添加明日建议
        if 'recommendations' in outlook:
            section += f"\n**Tomorrow's Recommendations:**\n"
            for rec in outlook['recommendations']:
                section += f"- {rec}\n"

        return section

    def _analyze_volume_trend(self, volume_change: float) -> str:
        """分析成交量趋势"""
        if volume_change > 20:
            return "大幅放量"
        elif volume_change > 5:
            return "温和放量"
        elif volume_change < -20:
            return "大幅缩量"
        elif volume_change < -5:
            return "温和缩量"
        else:
            return "基本持平"

    def _assess_market_activity(self, turnover_rate: float) -> str:
        """评估市场活跃度"""
        if turnover_rate > 3:
            return "较高"
        elif turnover_rate > 1:
            return "中等"
        else:
            return "较低"

    def _analyze_sector_performance(self, sectors: List[Dict]) -> str:
        """分析板块表现"""
        if not sectors:
            return "暂无板块数据"

        top_performers = sorted(sectors, key=lambda x: x.get('change_pct', 0), reverse=True)[:3]
        top_str = "、".join([f"{s['name']}({s.get('change_pct', 0):+.2f}%)" for s in top_performers])

        return f"表现突出的板块包括：{top_str}"

    def _get_performance_label(self, change_pct: float) -> str:
        """获取表现标签"""
        if change_pct > 5:
            return "强势上涨"
        elif change_pct > 2:
            return "明显上涨"
        elif change_pct > 0:
            return "小幅上涨"
        elif change_pct > -2:
            return "小幅下跌"
        elif change_pct > -5:
            return "明显下跌"
        else:
            return "大幅下跌"

    def _calculate_sector_allocation(self, holdings_data: List[Dict]) -> str:
        """计算行业分配"""
        sector_values = {}
        total_value = sum(h.get('current_value', 0) for h in holdings_data)

        for holding in holdings_data:
            sector = holding.get('sector', '未知')
            sector_values[sector] = sector_values.get(sector, 0) + holding.get('current_value', 0)

        allocations = []
        for sector, value in sorted(sector_values.items(), key=lambda x: x[1], reverse=True):
            pct = value / total_value * 100 if total_value > 0 else 0
            allocations.append(f"{sector}({pct:.1f}%)")

        return "、".join(allocations[:5])  # 显示前5大行业

    def generate_weekly_report(self, weekly_data: Dict) -> str:
        """生成周报"""
        report = f"\n# Weekly Trading Report\n"
        report += f"**Period:** {weekly_data.get('start_date')} - {weekly_data.get('end_date')}\n\n"

        # 周度表现
        report += "## Performance Summary\n"
        report += f"- Total Return: {weekly_data.get('total_return', 0):.2f}%\n"
        report += f"- Benchmark Return: {weekly_data.get('benchmark_return', 0):.2f}%\n"
        report += f"- Excess Return: {weekly_data.get('excess_return', 0):.2f}%\n\n"

        # 交易统计
        report += "## Trading Statistics\n"
        report += f"- Total Trades: {weekly_data.get('total_trades', 0)}\n"
        report += f"- Win Rate: {weekly_data.get('win_rate', 0):.1f}%\n"
        report += f"- Average Trade: {weekly_data.get('avg_trade_return', 0):.2f}%\n\n"

        # 风险指标
        report += "## Risk Metrics\n"
        report += f"- Volatility: {weekly_data.get('volatility', 0):.2f}%\n"
        report += f"- Sharpe Ratio: {weekly_data.get('sharpe', 0):.2f}\n"
        report += f"- Max Drawdown: {weekly_data.get('max_drawdown', 0):.2f}%\n\n"

        return report

    def generate_monthly_report(self, monthly_data: Dict) -> str:
        """生成月报"""
        report = f"\n# Monthly Trading Report\n"
        report += f"**Period:** {monthly_data.get('month', 'N/A')}\n\n"

        # 月度概览
        report += "## Monthly Overview\n"
        report += f"- Portfolio Return: {monthly_data.get('return', 0):.2f}%\n"
        report += f"- Best Performing Stock: {monthly_data.get('best_stock', 'N/A')}\n"
        report += f"- Worst Performing Stock: {monthly_data.get('worst_stock', 'N/A')}\n\n"

        # 行业分析
        if 'sector_analysis' in monthly_data:
            report += "## Sector Analysis\n"
            for sector, perf in monthly_data['sector_analysis'].items():
                report += f"- {sector}: {perf:.2f}%\n"
            report += "\n"

        # 改进建议
        report += "## Recommendations\n"
        for rec in monthly_data.get('recommendations', []):
            report += f"- {rec}\n"

        return report


if __name__ == "__main__":
    # 测试代码
    generator = TradingReportGenerator()

    # 模拟交易数据
    sample_data = {
        'date': '2025-12-09',
        'market': {
            'name': 'A股市场',
            'change_pct': 1.25,
            'volume': 1200,
            'volume_change': 15.5,
            'turnover_rate': 2.3,
            'sentiment': '积极',
            'indices': ['上证指数', '深证成指', '创业板指'],
            'sectors': [
                {'name': '科技', 'change_pct': 3.5},
                {'name': '医药', 'change_pct': 2.1},
                {'name': '消费', 'change_pct': 1.8}
            ]
        },
        'holdings': [
            {
                'name': '贵州茅台',
                'code': '600519.SH',
                'price': 1650.00,
                'change_pct': 2.5,
                'volume': 125000,
                'sector': '消费',
                'sector_performance': '领涨消费板块',
                'current_value': 165000,
                'pnl': 8500,
                'technical_signal': '突破前期高点'
            },
            {
                'name': '宁德时代',
                'code': '300750.SZ',
                'price': 195.50,
                'change_pct': -1.2,
                'volume': 980000,
                'sector': '新能源',
                'sector_performance': '板块表现疲软',
                'current_value': 97500,
                'pnl': -3250,
                'support_level': '190元'
            }
        ],
        'trades': [
            {
                'action': 'BUY',
                'symbol': '600519.SH',
                'amount': 100,
                'price': 1640.00,
                'timestamp': '10:30:15',
                'status': 'success',
                'details': '部分成交，剩余100股待成交'
            }
        ],
        'decisions': [
            {
                'symbol': '600519.SH',
                'sentiment': 'bullish',
                'confidence': 85.5,
                'indicators_used': ['RSI', 'MACD', '布林带'],
                'signal': '看涨信号',
                'technical_analysis': 'RSI显示超买区域但未形成背离',
                'fundamental_analysis': '业绩稳健，估值合理',
                'recommended_action': '买入持有'
            }
        ],
        'risk': {
            'level': 'medium',
            'type': '市场风险',
            'volatility': 18.5,
            'details': '组合波动率处于中等水平，建议适度分散',
            'recommendation': '保持谨慎乐观',
            'metrics': {
                'var': '¥12,500 (95% confidence)',
                'sharpe': 1.35,
                'max_drawdown': -5.2
            }
        },
        'outlook': {
            'sentiment': '谨慎乐观',
            'key_factors': [
                '关注美联储政策变化',
                '监控A股成交量变化',
                '关注科技板块轮动机会'
            ],
            'recommendations': [
                '适度加仓优质成长股',
                '控制仓位在80%以内',
                '设置止损位'
            ]
        }
    }

    # 生成报告
    report = generator.generate_daily_report(sample_data)
    print(report)

    print("\n" + "="*60)
    print("Report Generated Successfully!")
    print("="*60)
