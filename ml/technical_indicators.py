#!/usr/bin/env python3
"""
高级技术指标分析器
实现多时间框架分析、量价分析、市场情绪指标和机器学习预测信号
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import talib
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import warnings

warnings.filterwarnings('ignore')

class AdvancedTechnicalAnalyzer:
    """高级技术指标分析器"""

    def __init__(self):
        self.custom_indicators = {}
        self.ml_model = None
        self.scaler = StandardScaler()

    def calculate_custom_indicators(self, df: pd.DataFrame) -> Dict:
        """计算自定义技术指标

        Args:
            df: 包含OHLCV数据的DataFrame

        Returns:
            包含所有指标的字典
        """
        indicators = {}

        # 1. 多时间框架分析
        indicators['multi_timeframe'] = self.multi_timeframe_analysis(df)

        # 2. 量价分析
        indicators['volume_analysis'] = self.volume_price_analysis(df)

        # 3. 市场情绪指标
        indicators['sentiment'] = self.calculate_sentiment_indicators(df)

        # 4. 机器学习预测信号
        indicators['ml_signals'] = self.generate_ml_signals(df)

        # 5. 自定义组合指标
        indicators['custom'] = self.calculate_custom_combinations(df)

        return indicators

    def multi_timeframe_analysis(self, df: pd.DataFrame) -> Dict:
        """多时间框架分析"""
        analysis = {}

        # 日线指标
        analysis['daily'] = {
            'rsi': talib.RSI(df['close'].values, timeperiod=14),
            'rsi_fast': talib.RSI(df['close'].values, timeperiod=6),
            'rsi_slow': talib.RSI(df['close'].values, timeperiod=21),
            'macd': talib.MACD(df['close'].values),
            'macd_line': talib.MACD(df['close'].values)[0],
            'macd_signal': talib.MACD(df['close'].values)[1],
            'macd_hist': talib.MACD(df['close'].values)[2],
            'bollinger_upper': talib.BBANDS(df['close'].values)[0],
            'bollinger_middle': talib.BBANDS(df['close'].values)[1],
            'bollinger_lower': talib.BBANDS(df['close'].values)[2],
            'atr': talib.ATR(df['high'].values, df['low'].values, df['close'].values),
            'stoch_k': talib.STOCH(df['high'].values, df['low'].values, df['close'].values)[0],
            'stoch_d': talib.STOCH(df['high'].values, df['low'].values, df['close'].values)[1],
            'williams_r': talib.WILLR(df['high'].values, df['low'].values, df['close'].values),
            'cci': talib.CCI(df['high'].values, df['low'].values, df['close'].values),
            'adx': talib.ADX(df['high'].values, df['low'].values, df['close'].values)
        }

        # 周线指标（使用日线数据聚合）
        weekly_df = df.resample('W').agg({
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum'
        }).dropna()

        if len(weekly_df) > 10:
            analysis['weekly'] = {
                'rsi': talib.RSI(weekly_df['close'].values, timeperiod=14),
                'macd': talib.MACD(weekly_df['close'].values),
                'bollinger': talib.BBANDS(weekly_df['close'].values)
            }

        # 月线指标
        monthly_df = df.resample('M').agg({
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum'
        }).dropna()

        if len(monthly_df) > 5:
            analysis['monthly'] = {
                'rsi': talib.RSI(monthly_df['close'].values, timeperiod=14),
                'macd': talib.MACD(monthly_df['close'].values)
            }

        return analysis

    def volume_price_analysis(self, df: pd.DataFrame) -> Dict:
        """量价分析"""
        # 量价相关性
        price_change = df['close'].pct_change()
        volume_change = df['volume'].pct_change()
        correlation = price_change.corr(volume_change)

        # 成交量趋势
        volume_sma_5 = df['volume'].rolling(window=5).mean()
        volume_sma_20 = df['volume'].rolling(window=20).mean()
        volume_ratio = df['volume'] / volume_sma_20

        # 价格突破量能
        price_change_ma = price_change.rolling(window=20).mean()
        volume_weighted_price = (df['close'] * df['volume']).rolling(window=20).sum() / df['volume'].rolling(window=20).sum()

        # 成交量摆动指标
        volume_oscillator = ((df['volume'] - volume_sma_5) / volume_sma_5 * 100)

        # 量价背离
        price_trend = df['close'].rolling(window=10).apply(lambda x: np.polyfit(range(len(x)), x, 1)[0])
        volume_trend = df['volume'].rolling(window=10).apply(lambda x: np.polyfit(range(len(x)), x, 1)[0])
        volume_price_divergence = (price_trend / volume_trend).fillna(0)

        # OBV (On-Balance Volume)
        obv = (np.sign(df['close'].diff()) * df['volume']).fillna(0).cumsum()

        # VWAP (Volume Weighted Average Price)
        vwap = (df['close'] * df['volume']).cumsum() / df['volume'].cumsum()

        return {
            'volume_price_correlation': correlation,
            'volume_trend': volume_ratio.tolist(),
            'volume_oscillator': volume_oscillator.tolist(),
            'vwap_deviation': ((df['close'] - vwap) / vwap * 100).tolist(),
            'volume_spikes': (volume_ratio > 2).astype(int).tolist(),
            'volume_dry': (volume_ratio < 0.5).astype(int).tolist(),
            'obv': obv.tolist(),
            'price_volume_divergence': volume_price_divergence.tolist()
        }

    def calculate_sentiment_indicators(self, df: pd.DataFrame) -> Dict:
        """市场情绪指标"""
        # 恐慌贪婪指数（简化版）
        rsi = talib.RSI(df['close'].values, timeperiod=14)
        fear_greed = np.where(rsi < 30, '极恐',
                             np.where(rsi < 45, '恐慌',
                                     np.where(rsi < 55, '中性',
                                             np.where(rsi < 70, '贪婪', '极贪'))))

        # 成交量情绪
        volume_mean = df['volume'].rolling(window=20).mean()
        volume_std = df['volume'].rolling(window=20).std()
        volume_zscore = (df['volume'] - volume_mean) / volume_std
        volume_sentiment = np.where(volume_zscore > 2, '极度乐观',
                                   np.where(volume_zscore > 1, '乐观',
                                           np.where(volume_zscore > -1, '中性',
                                                   np.where(volume_zscore > -2, '悲观', '极度悲观'))))

        # 波动率情绪
        returns = df['close'].pct_change()
        volatility = returns.rolling(window=20).std() * np.sqrt(252)
        volatility_sentiment = np.where(volatility > volatility.rolling(window=60).quantile(0.8), '高波动',
                                       np.where(volatility < volatility.rolling(window=60).quantile(0.2), '低波动', '正常波动'))

        return {
            'fear_greed_index': fear_greed.tolist(),
            'volume_sentiment': volume_sentiment.tolist(),
            'volatility_sentiment': volatility_sentiment.tolist(),
            'fear_greed_score': ((100 - rsi) / 100).tolist()  # 0-1之间的分数
        }

    def generate_ml_signals(self, df: pd.DataFrame) -> Dict:
        """机器学习预测信号"""
        if len(df) < 100:
            return {'signals': [], 'confidence': []}

        # 准备特征
        features = self.prepare_ml_features(df)
        target = self.create_prediction_target(df)

        # 去除缺失值
        valid_data = pd.concat([features, target], axis=1).dropna()

        if len(valid_data) < 50:
            return {'signals': [], 'confidence': []}

        X = valid_data.drop(columns=[target.name])
        y = valid_data[target.name]

        # 标准化特征
        X_scaled = self.scaler.fit_transform(X)

        # 训练随机森林模型
        self.ml_model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            class_weight='balanced'
        )

        self.ml_model.fit(X_scaled, y)

        # 预测最新数据点
        latest_features = features.tail(1)
        latest_scaled = self.scaler.transform(latest_features)
        prediction = self.ml_model.predict(latest_scaled)[0]
        probability = self.ml_model.predict_proba(latest_scaled)[0]

        # 生成信号
        signal = 'buy' if prediction == 1 else 'sell'
        confidence = max(probability)

        # 特征重要性
        feature_importance = dict(zip(
            X.columns,
            self.ml_model.feature_importances_
        ))

        return {
            'signal': signal,
            'confidence': confidence,
            'probability_buy': probability[1],
            'probability_sell': probability[0],
            'feature_importance': feature_importance,
            'model_score': self.ml_model.score(X_scaled, y)
        }

    def prepare_ml_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """准备机器学习特征"""
        features = pd.DataFrame(index=df.index)

        # 价格特征
        features['price_change'] = df['close'].pct_change()
        features['price_volatility'] = df['close'].rolling(window=20).std()
        features['high_low_ratio'] = df['high'] / df['low']
        features['close_open_ratio'] = df['close'] / df['open']

        # 技术指标特征
        features['rsi'] = talib.RSI(df['close'].values, timeperiod=14)
        features['rsi_6'] = talib.RSI(df['close'].values, timeperiod=6)
        features['rsi_21'] = talib.RSI(df['close'].values, timeperiod=21)

        macd, macd_signal, macd_hist = talib.MACD(df['close'].values)
        features['macd'] = macd
        features['macd_signal'] = macd_signal
        features['macd_hist'] = macd_hist

        features['bb_upper'], features['bb_middle'], features['bb_lower'] = talib.BBANDS(df['close'].values)
        features['bb_width'] = (features['bb_upper'] - features['bb_lower']) / features['bb_middle']
        features['bb_position'] = (df['close'] - features['bb_lower']) / (features['bb_upper'] - features['bb_lower'])

        # 成交量特征
        features['volume_change'] = df['volume'].pct_change()
        features['volume_sma_ratio'] = df['volume'] / df['volume'].rolling(window=20).mean()
        features['price_volume'] = df['close'] * df['volume']

        # 滞后特征
        for lag in [1, 2, 3, 5]:
            features[f'price_lag_{lag}'] = df['close'].shift(lag)
            features[f'volume_lag_{lag}'] = df['volume'].shift(lag)
            features[f'rsi_lag_{lag}'] = features['rsi'].shift(lag)

        # 趋势特征
        for window in [5, 10, 20]:
            features[f'sma_{window}'] = df['close'].rolling(window=window).mean()
            features[f'price_sma_{window}_ratio'] = df['close'] / features[f'sma_{window}']
            features[f'volume_sma_{window}'] = df['volume'].rolling(window=window).mean()

        return features.fillna(0)

    def create_prediction_target(self, df: pd.DataFrame, forward_days: int = 5) -> pd.Series:
        """创建预测目标（未来N天涨跌）"""
        future_return = df['close'].shift(-forward_days) / df['close'] - 1

        # 三分类：涨(2) / 横盘(1) / 跌(0)
        target = pd.cut(future_return,
                       bins=[-np.inf, -0.02, 0.02, np.inf],
                       labels=[0, 1, 2],
                       include_lowest=True)

        return target.astype(int)

    def calculate_custom_combinations(self, df: pd.DataFrame) -> Dict:
        """自定义组合指标"""
        combinations = {}

        # RSI + MACD 组合信号
        rsi = talib.RSI(df['close'].values, timeperiod=14)
        macd, macd_signal, macd_hist = talib.MACD(df['close'].values)

        rsi_macd_signal = []
        for i in range(len(df)):
            signal = 'neutral'
            if rsi[i] < 30 and macd[i] > macd_signal[i]:
                signal = 'strong_buy'
            elif rsi[i] > 70 and macd[i] < macd_signal[i]:
                signal = 'strong_sell'
            elif rsi[i] < 50 and macd[i] > macd_signal[i]:
                signal = 'buy'
            elif rsi[i] > 50 and macd[i] < macd_signal[i]:
                signal = 'sell'
            rsi_macd_signal.append(signal)

        combinations['rsi_macd_signal'] = rsi_macd_signal

        # 布林带 + 成交量组合
        bb_upper, bb_middle, bb_lower = talib.BBANDS(df['close'].values)
        volume_ma = df['volume'].rolling(window=20).mean()

        bb_volume_signal = []
        for i in range(len(df)):
            signal = 'neutral'
            if df['close'].iloc[i] < bb_lower[i] and df['volume'].iloc[i] > volume_ma.iloc[i] * 1.5:
                signal = 'buy_on_volume'
            elif df['close'].iloc[i] > bb_upper[i] and df['volume'].iloc[i] > volume_ma.iloc[i] * 1.5:
                signal = 'sell_on_volume'
            bb_volume_signal.append(signal)

        combinations['bb_volume_signal'] = bb_volume_signal

        return combinations

    def generate_comprehensive_report(self, df: pd.DataFrame) -> Dict:
        """生成综合技术分析报告"""
        indicators = self.calculate_custom_indicators(df)

        # 计算综合评分
        latest_rsi = indicators['multi_timeframe']['daily']['rsi'][-1]
        latest_macd = indicators['multi_timeframe']['daily']['macd_line'][-1]
        latest_signal = indicators['multi_timeframe']['daily']['macd_signal'][-1]
        latest_bb_position = indicators['custom']['bb_position'][-1] if 'bb_position' in indicators['custom'] else 0.5

        # 评分算法
        score = 50  # 基础分

        # RSI评分 (0-100)
        if latest_rsi < 30:
            score += 20
        elif latest_rsi < 50:
            score += 10
        elif latest_rsi > 70:
            score -= 20
        elif latest_rsi > 50:
            score -= 10

        # MACD评分
        if latest_macd > latest_signal:
            score += 15
        else:
            score -= 15

        # 布林带位置评分
        if latest_bb_position < 0.2:
            score += 10
        elif latest_bb_position > 0.8:
            score -= 10

        # 成交量评分
        volume_ratio = indicators['volume_analysis']['volume_trend'][-1]
        if volume_ratio > 2:
            score += 10
        elif volume_ratio < 0.5:
            score -= 5

        score = max(0, min(100, score))

        # 生成建议
        if score > 70:
            recommendation = 'strong_buy'
        elif score > 60:
            recommendation = 'buy'
        elif score < 30:
            recommendation = 'strong_sell'
        elif score < 40:
            recommendation = 'sell'
        else:
            recommendation = 'hold'

        report = {
            'timestamp': df.index[-1],
            'comprehensive_score': score,
            'recommendation': recommendation,
            'signals': {
                'rsi_signal': 'oversold' if latest_rsi < 30 else 'overbought' if latest_rsi > 70 else 'neutral',
                'macd_signal': 'bullish' if latest_macd > latest_signal else 'bearish',
                'bb_signal': 'lower_band' if latest_bb_position < 0.2 else 'upper_band' if latest_bb_position > 0.8 else 'middle',
                'volume_signal': 'high' if volume_ratio > 2 else 'low' if volume_ratio < 0.5 else 'normal'
            },
            'indicators': indicators,
            'risk_metrics': {
                'volatility': df['close'].pct_change().std() * np.sqrt(252),
                'max_drawdown': self.calculate_max_drawdown(df['close']),
                'sharpe_ratio': self.calculate_sharpe_ratio(df['close'])
            }
        }

        return report

    def calculate_max_drawdown(self, prices: pd.Series) -> float:
        """计算最大回撤"""
        peak = prices.expanding().max()
        drawdown = (prices - peak) / peak
        return drawdown.min()

    def calculate_sharpe_ratio(self, prices: pd.Series, risk_free_rate: float = 0.03) -> float:
        """计算夏普比率"""
        returns = prices.pct_change().dropna()
        excess_returns = returns - risk_free_rate / 252
        return excess_returns.mean() / excess_returns.std() * np.sqrt(252)


if __name__ == "__main__":
    # 测试代码
    import matplotlib.pyplot as plt

    # 生成模拟数据
    np.random.seed(42)
    dates = pd.date_range('2023-01-01', periods=200, freq='D')

    # 模拟股价数据
    price = 100
    prices = []
    volumes = []

    for i in range(200):
        change = np.random.normal(0, 0.02)
        price = price * (1 + change)
        prices.append(price)
        volumes.append(np.random.randint(500000, 5000000))

    df = pd.DataFrame({
        'date': dates,
        'open': [p * (1 + np.random.normal(0, 0.005)) for p in prices],
        'high': [p * (1 + abs(np.random.normal(0, 0.01))) for p in prices],
        'low': [p * (1 - abs(np.random.normal(0, 0.01))) for p in prices],
        'close': prices,
        'volume': volumes
    })

    df.set_index('date', inplace=True)

    # 创建分析器
    analyzer = AdvancedTechnicalAnalyzer()

    # 生成综合报告
    report = analyzer.generate_comprehensive_report(df)

    print("=" * 60)
    print("高级技术分析报告")
    print("=" * 60)
    print(f"综合评分: {report['comprehensive_score']:.1f}/100")
    print(f"投资建议: {report['recommendation']}")
    print(f"风险指标:")
    print(f"  - 波动率: {report['risk_metrics']['volatility']:.2%}")
    print(f"  - 最大回撤: {report['risk_metrics']['max_drawdown']:.2%}")
    print(f"  - 夏普比率: {report['risk_metrics']['sharpe_ratio']:.2f}")

    if 'ml_signals' in report['indicators'] and report['indicators']['ml_signals']:
        ml = report['indicators']['ml_signals']
        print(f"\n机器学习信号:")
        print(f"  - 信号: {ml['signal']}")
        print(f"  - 置信度: {ml['confidence']:.2%}")
