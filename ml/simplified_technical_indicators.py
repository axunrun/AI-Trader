#!/usr/bin/env python3
"""
简化版高级技术指标分析器
不依赖外部库，纯Python实现
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any
from datetime import datetime


class SimplifiedTechnicalAnalyzer:
    """简化版技术指标分析器"""

    def __init__(self):
        self.indicators_cache = {}

    def calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """计算RSI相对强弱指数"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def calculate_macd(self, prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, pd.Series]:
        """计算MACD指标"""
        exp1 = prices.ewm(span=fast).mean()
        exp2 = prices.ewm(span=slow).mean()
        macd_line = exp1 - exp2
        signal_line = macd_line.ewm(span=signal).mean()
        histogram = macd_line - signal_line

        return {
            'macd': macd_line,
            'signal': signal_line,
            'histogram': histogram
        }

    def calculate_bollinger_bands(self, prices: pd.Series, period: int = 20, std_dev: float = 2) -> Dict[str, pd.Series]:
        """计算布林带"""
        sma = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()

        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        bandwidth = (upper_band - lower_band) / sma

        return {
            'upper': upper_band,
            'middle': sma,
            'lower': lower_band,
            'bandwidth': bandwidth
        }

    def calculate_sma(self, prices: pd.Series, period: int) -> pd.Series:
        """计算简单移动平均线"""
        return prices.rolling(window=period).mean()

    def calculate_ema(self, prices: pd.Series, period: int) -> pd.Series:
        """计算指数移动平均线"""
        return prices.ewm(span=period).mean()

    def calculate_atr(self, high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
        """计算平均真实范围(ATR)"""
        high_low = high - low
        high_close = np.abs(high - close.shift())
        low_close = np.abs(low - close.shift())

        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = true_range.rolling(window=period).mean()

        return atr

    def calculate_obv(self, close: pd.Series, volume: pd.Series) -> pd.Series:
        """计算能量潮指标"""
        obv = pd.Series(index=close.index, dtype=float)
        obv.iloc[0] = volume.iloc[0]

        for i in range(1, len(close)):
            if close.iloc[i] > close.iloc[i-1]:
                obv.iloc[i] = obv.iloc[i-1] + volume.iloc[i]
            elif close.iloc[i] < close.iloc[i-1]:
                obv.iloc[i] = obv.iloc[i-1] - volume.iloc[i]
            else:
                obv.iloc[i] = obv.iloc[i-1]

        return obv

    def calculate_vwap(self, high: pd.Series, low: pd.Series, close: pd.Series, volume: pd.Series) -> pd.Series:
        """计算成交量加权平均价格"""
        typical_price = (high + low + close) / 3
        vwap = (typical_price * volume).cumsum() / volume.cumsum()
        return vwap

    def detect_crossovers(self, series1: pd.Series, series2: pd.Series) -> pd.Series:
        """检测两条线的交叉点"""
        diff = series1 - series2
        crossover = (diff > 0) & (diff.shift(1) <= 0)
        crossunder = (diff < 0) & (diff.shift(1) >= 0)
        return pd.DataFrame({'crossover': crossover, 'crossunder': crossunder})

    def calculate_custom_indicators(self, df: pd.DataFrame) -> Dict[str, Any]:
        """计算自定义技术指标组合"""
        indicators = {}

        # 1. 基础技术指标
        indicators['rsi'] = self.calculate_rsi(df['close'])
        indicators['macd'] = self.calculate_macd(df['close'])
        indicators['bollinger'] = self.calculate_bollinger_bands(df['close'])
        indicators['sma_20'] = self.calculate_sma(df['close'], 20)
        indicators['sma_60'] = self.calculate_sma(df['close'], 60)
        indicators['ema_12'] = self.calculate_ema(df['close'], 12)
        indicators['ema_26'] = self.calculate_ema(df['close'], 26)
        indicators['atr'] = self.calculate_atr(df['high'], df['low'], df['close'])

        # 2. 量价指标
        indicators['obv'] = self.calculate_obv(df['close'], df['volume'])
        indicators['vwap'] = self.calculate_vwap(df['high'], df['low'], df['close'], df['volume'])

        # 3. 价格位置指标
        indicators['price_position'] = (df['close'] - df['close'].rolling(20).min()) / (
            df['close'].rolling(20).max() - df['close'].rolling(20).min()
        )

        # 4. 波动率指标
        indicators['volatility'] = df['close'].pct_change().rolling(20).std() * np.sqrt(252)

        # 5. 成交量指标
        indicators['volume_sma'] = df['volume'].rolling(20).mean()
        indicators['volume_ratio'] = df['volume'] / indicators['volume_sma']

        # 6. 综合信号
        signals = self.generate_trading_signals(df, indicators)
        indicators['signals'] = signals

        # 7. 市场情绪指标
        sentiment = self.calculate_sentiment_indicators(df, indicators)
        indicators['sentiment'] = sentiment

        # 8. 多时间框架分析
        mtf_analysis = self.multi_timeframe_analysis(df)
        indicators['multi_timeframe'] = mtf_analysis

        return indicators

    def generate_trading_signals(self, df: pd.DataFrame, indicators: Dict) -> Dict[str, Any]:
        """生成交易信号"""
        signals = {}

        # RSI信号
        rsi = indicators['rsi']
        signals['rsi_oversold'] = rsi < 30
        signals['rsi_overbought'] = rsi > 70

        # MACD信号
        macd = indicators['macd']
        macd_cross = self.detect_crossovers(macd['macd'], macd['signal'])
        signals['macd_bullish_cross'] = macd_cross['crossover']
        signals['macd_bearish_cross'] = macd_cross['crossunder']

        # 布林带信号
        bb = indicators['bollinger']
        signals['bb_squeeze'] = bb['bandwidth'] < bb['bandwidth'].rolling(50).quantile(0.1)
        signals['bb_upper_break'] = df['close'] > bb['upper']
        signals['bb_lower_break'] = df['close'] < bb['lower']

        # 综合信号
        signals['buy_signal'] = (
            signals['rsi_oversold'] |
            signals['macd_bullish_cross']
        )
        signals['sell_signal'] = (
            signals['rsi_overbought'] |
            signals['macd_bearish_cross']
        )

        # 置信度评分
        signals['confidence'] = self.calculate_signal_confidence(signals)

        return signals

    def calculate_signal_confidence(self, signals: Dict) -> pd.Series:
        """计算信号置信度"""
        confidence = pd.Series(index=signals[list(signals.keys())[0]].index, dtype=float)

        for i in range(len(confidence)):
            score = 0
            if signals['rsi_oversold'].iloc[i]:
                score += 0.3
            if signals['rsi_overbought'].iloc[i]:
                score += 0.3
            if signals['macd_bullish_cross'].iloc[i]:
                score += 0.4
            if signals['macd_bearish_cross'].iloc[i]:
                score += 0.4
            if signals['bb_squeeze'].iloc[i]:
                score += 0.2

            confidence.iloc[i] = min(score, 1.0)

        return confidence

    def calculate_sentiment_indicators(self, df: pd.DataFrame, indicators: Dict) -> Dict[str, Any]:
        """计算市场情绪指标"""
        sentiment = {}

        # 恐慌贪婪指数（简化版）
        rsi = indicators['rsi']
        volatility = indicators['volatility']
        volume_ratio = indicators['volume_ratio']

        # 计算恐慌贪婪指数
        fear_greed = (
            (50 - rsi) * 0.4 +  # RSI反转
            (volatility / volatility.rolling(50).mean() - 1) * 20 * 0.3 +  # 波动率
            (volume_ratio - 1) * 50 * 0.3  # 成交量
        ).fillna(0)

        sentiment['fear_greed_index'] = fear_greed.clip(0, 100)
        sentiment['is_fear'] = sentiment['fear_greed_index'] < 25
        sentiment['is_greed'] = sentiment['fear_greed_index'] > 75

        # 波动率情绪
        sentiment['volatility_regime'] = np.where(
            volatility > volatility.rolling(50).quantile(0.8),
            'high',
            np.where(volatility < volatility.rolling(50).quantile(0.2), 'low', 'normal')
        )

        return sentiment

    def multi_timeframe_analysis(self, df: pd.DataFrame) -> Dict[str, Any]:
        """多时间框架分析"""
        mtf = {}

        # 日线指标
        mtf['daily'] = {
            'sma_20': self.calculate_sma(df['close'], 20),
            'sma_60': self.calculate_sma(df['close'], 60),
            'rsi': self.calculate_rsi(df['close'])
        }

        # 周线指标（通过重采样）
        weekly_df = df.resample('W').agg({
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum'
        })

        mtf['weekly'] = {
            'sma_10': self.calculate_sma(weekly_df['close'], 10),
            'rsi': self.calculate_rsi(weekly_df['close'])
        }

        # 月线指标
        monthly_df = df.resample('M').agg({
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum'
        })

        mtf['monthly'] = {
            'sma_6': self.calculate_sma(monthly_df['close'], 6),
            'rsi': self.calculate_rsi(monthly_df['close'])
        }

        # 时间框架一致性检查
        mtf['alignment'] = self.check_timeframe_alignment(mtf)

        return mtf

    def check_timeframe_alignment(self, mtf: Dict) -> Dict[str, bool]:
        """检查多时间框架一致性"""
        alignment = {}

        # 检查各时间框架的RSI趋势
        daily_rsi_trend = mtf['daily']['rsi'].iloc[-1] - mtf['daily']['rsi'].iloc[-5]
        weekly_rsi_trend = mtf['weekly']['rsi'].iloc[-1] - mtf['weekly']['rsi'].iloc[-5]

        alignment['rsi_aligned'] = (daily_rsi_trend > 0) == (weekly_rsi_trend > 0)

        # 检查移动平均线趋势
        daily_sma_trend = mtf['daily']['sma_20'].iloc[-1] > mtf['daily']['sma_20'].iloc[-5]
        weekly_sma_trend = mtf['weekly']['sma_10'].iloc[-1] > mtf['weekly']['sma_10'].iloc[-5]

        alignment['sma_aligned'] = daily_sma_trend == weekly_sma_trend

        return alignment

    def get_latest_signals(self, indicators: Dict) -> Dict[str, Any]:
        """获取最新交易信号"""
        latest = {}

        signals = indicators['signals']
        sentiment = indicators['sentiment']

        latest['timestamp'] = datetime.now().isoformat()

        # 最新信号
        latest['buy_signal'] = signals['buy_signal'].iloc[-1] if len(signals['buy_signal']) > 0 else False
        latest['sell_signal'] = signals['sell_signal'].iloc[-1] if len(signals['sell_signal']) > 0 else False

        # 置信度
        latest['confidence'] = signals['confidence'].iloc[-1] if len(signals['confidence']) > 0 else 0.0

        # 情绪状态
        latest['fear_greed'] = sentiment['fear_greed_index'].iloc[-1] if len(sentiment['fear_greed_index']) > 0 else 50.0
        latest['sentiment_state'] = 'fear' if sentiment['is_fear'].iloc[-1] else 'greed' if sentiment['is_greed'].iloc[-1] else 'neutral'

        # 技术指标读数
        latest['rsi'] = indicators['rsi'].iloc[-1] if len(indicators['rsi']) > 0 else 50.0
        latest['macd_histogram'] = indicators['macd']['histogram'].iloc[-1] if len(indicators['macd']['histogram']) > 0 else 0.0

        # 支撑阻力位
        bb = indicators['bollinger']
        latest['resistance'] = bb['upper'].iloc[-1] if len(bb['upper']) > 0 else None
        latest['support'] = bb['lower'].iloc[-1] if len(bb['lower']) > 0 else None

        return latest


if __name__ == "__main__":
    # 测试代码
    import matplotlib.pyplot as plt

    # 生成模拟数据
    dates = pd.date_range('2025-01-01', periods=100, freq='D')
    np.random.seed(42)

    price = 100.0
    prices = []
    for _ in range(100):
        change = np.random.normal(0, 0.02)
        price = price * (1 + change)
        prices.append(price)

    df = pd.DataFrame({
        'date': dates,
        'open': [p * (1 + np.random.normal(0, 0.005)) for p in prices],
        'high': [p * (1 + abs(np.random.normal(0, 0.01))) for p in prices],
        'low': [p * (1 - abs(np.random.normal(0, 0.01))) for p in prices],
        'close': prices,
        'volume': [np.random.randint(500000, 5000000) for _ in range(100)]
    })

    df.set_index('date', inplace=True)

    # 创建分析器
    analyzer = SimplifiedTechnicalAnalyzer()

    # 计算指标
    indicators = analyzer.calculate_custom_indicators(df)

    # 获取最新信号
    latest_signals = analyzer.get_latest_signals(indicators)

    # 打印结果
    print("="*60)
    print("Technical Indicators Analysis - Test Results")
    print("="*60)
    print(f"Latest RSI: {latest_signals['rsi']:.2f}")
    print(f"MACD Histogram: {latest_signals['macd_histogram']:.4f}")
    print(f"Fear & Greed Index: {latest_signals['fear_greed']:.2f}")
    print(f"Buy Signal: {latest_signals['buy_signal']}")
    print(f"Sell Signal: {latest_signals['sell_signal']}")
    print(f"Confidence: {latest_signals['confidence']:.2f}")
    print(f"Support Level: {latest_signals['support']:.2f}")
    print(f"Resistance Level: {latest_signals['resistance']:.2f}")
    print("="*60)
    print("Test completed successfully!")
