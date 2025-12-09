#!/usr/bin/env python3
"""
简化版A股交易强化学习环境
不依赖gymnasium，纯Python实现
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
from enum import Enum


class Action(Enum):
    """交易动作"""
    HOLD = 0
    BUY = 1
    SELL = 2


class SimplifiedTradingEnv:
    """简化版A股交易环境"""

    def __init__(self,
                 stock_data: pd.DataFrame,
                 initial_balance: float = 100000,
                 transaction_fee: float = 0.0003,
                 tax_rate: float = 0.001,
                 max_position: float = 0.95,
                 stop_loss: float = 0.10,
                 take_profit: float = 0.20):

        self.stock_data = stock_data.reset_index(drop=True)
        self.n_steps = len(stock_data)

        # 环境参数
        self.initial_balance = initial_balance
        self.transaction_fee = transaction_fee
        self.tax_rate = tax_rate
        self.max_position = max_position
        self.stop_loss = stop_loss
        self.take_profit = take_profit

        # 状态变量
        self.reset()

    def reset(self) -> np.ndarray:
        """重置环境"""
        self.current_step = 0
        self.balance = self.initial_balance
        self.position = 0.0  # 当前仓位 (0-1)
        self.entry_price = 0.0
        self.max_portfolio_value = self.initial_balance
        self.total_fees = 0.0
        self.total_taxes = 0.0
        self.trades = []
        self.prev_portfolio_value = self.initial_balance

        return self._get_observation()

    def step(self, action: int) -> Tuple[np.ndarray, float, bool, Dict[str, Any]]:
        """执行动作"""
        if action not in [0, 1, 2]:
            raise ValueError(f"Invalid action: {action}")

        current_price = self.stock_data.iloc[self.current_step]['close']
        done = self.current_step >= self.n_steps - 1

        # 执行动作
        if action == Action.BUY.value:
            self._execute_buy(current_price)
        elif action == Action.SELL.value:
            self._execute_sell(current_price)
        # action == 0: 持有，什么都不做

        # 计算奖励
        reward = self._calculate_reward(current_price)

        # 检查止盈止损
        if self.position > 0:
            pnl_pct = (current_price - self.entry_price) / self.entry_price
            if pnl_pct <= -self.stop_loss:
                self._execute_sell(current_price)
                reward += 50  # 止损奖励
            elif pnl_pct >= self.take_profit:
                self._execute_sell(current_price)
                reward += 100  # 止盈奖励

        # 更新最大组合价值
        portfolio_value = self._get_portfolio_value(current_price)
        self.max_portfolio_value = max(self.max_portfolio_value, portfolio_value)

        # 移动到下一步
        self.current_step += 1

        # 判断是否结束
        if done or self.balance <= 0:
            done = True

        info = {
            'portfolio_value': portfolio_value,
            'balance': self.balance,
            'position': self.position,
            'total_trades': len(self.trades),
            'total_fees': self.total_fees,
            'total_taxes': self.total_taxes
        }

        return self._get_observation(), reward, done, info

    def _execute_buy(self, price: float):
        """执行买入操作"""
        if self.position >= self.max_position:
            return

        available_cash = self.balance * (self.max_position - self.position)
        max_shares = int(available_cash / price)

        if max_shares <= 0:
            return

        # 买入一半可用资金
        buy_amount = available_cash * 0.5
        shares_to_buy = int(buy_amount / price)

        if shares_to_buy <= 0:
            return

        cost = shares_to_buy * price
        fee = cost * self.transaction_fee
        total_cost = cost + fee

        if total_cost <= self.balance:
            self.balance -= total_cost
            self.position += (shares_to_buy * price) / self.initial_balance
            self.entry_price = price
            self.total_fees += fee

            self.trades.append({
                'step': self.current_step,
                'action': 'buy',
                'shares': shares_to_buy,
                'price': price,
                'cost': total_cost,
                'fee': fee
            })

    def _execute_sell(self, price: float):
        """执行卖出操作"""
        if self.position <= 0:
            return

        sell_ratio = 0.5
        sell_value = self.initial_balance * self.position * sell_ratio
        shares_to_sell = int(sell_value / price)

        if shares_to_sell <= 0:
            return

        proceeds = shares_to_sell * price
        fee = proceeds * self.transaction_fee
        tax = proceeds * self.tax_rate if proceeds > self.initial_balance * self.position else 0
        net_proceeds = proceeds - fee - tax

        self.balance += net_proceeds
        self.position -= (shares_to_sell * price) / self.initial_balance
        self.total_fees += fee
        self.total_taxes += tax

        self.trades.append({
            'step': self.current_step,
            'action': 'sell',
            'shares': shares_to_sell,
            'price': price,
            'proceeds': net_proceeds,
            'fee': fee,
            'tax': tax
        })

        if self.position < 0.01:
            self.position = 0
            self.entry_price = 0

    def _calculate_reward(self, current_price: float) -> float:
        """计算奖励"""
        portfolio_value = self._get_portfolio_value(current_price)
        prev_value = self.prev_portfolio_value

        # 基础奖励：组合价值变化
        reward = (portfolio_value - prev_value) / prev_value * 1000

        # 持仓奖励
        if 0.1 < self.position < 0.8:
            reward += 1

        # 手续费惩罚
        reward -= self.total_fees * 0.01

        self.prev_portfolio_value = portfolio_value
        return reward

    def _get_portfolio_value(self, current_price: float) -> float:
        """获取组合总价值"""
        stock_value = self.initial_balance * self.position * (current_price / self.entry_price) if self.entry_price > 0 else 0
        return self.balance + stock_value

    def _get_observation(self) -> np.ndarray:
        """获取当前观察"""
        if self.current_step >= self.n_steps:
            return np.zeros(7, dtype=np.float32)

        row = self.stock_data.iloc[self.current_step]

        # 计算技术指标
        rsi = self._calculate_rsi()
        macd = self._calculate_macd()
        bb_position = self._calculate_bb_position()
        volume_ratio = self._calculate_volume_ratio()

        observation = np.array([
            self.balance / self.initial_balance,
            self.position,
            row['close'] / 100.0,
            rsi / 100.0,
            macd,
            bb_position,
            volume_ratio
        ], dtype=np.float32)

        return observation

    def _calculate_rsi(self, period: int = 14) -> float:
        """计算RSI"""
        if self.current_step < period:
            return 50.0

        prices = self.stock_data['close'].iloc[self.current_step - period:self.current_step]
        deltas = prices.diff()
        gains = deltas.where(deltas > 0, 0).mean()
        losses = -deltas.where(deltas < 0, 0).mean()

        if losses == 0:
            return 100.0

        rs = gains / losses
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def _calculate_macd(self, fast: int = 12, slow: int = 26, signal: int = 9) -> float:
        """计算MACD"""
        if self.current_step < slow:
            return 0.0

        prices = self.stock_data['close'].iloc[:self.current_step]
        exp1 = prices.ewm(span=fast).mean()
        exp2 = prices.ewm(span=slow).mean()
        macd = exp1.iloc[-1] - exp2.iloc[-1]

        # 计算信号线
        prices_series = pd.Series([macd], index=[self.current_step - 1])
        signal_line = prices_series.ewm(span=signal).mean().iloc[-1] if self.current_step > signal else macd

        return (macd - signal_line) / 100.0

    def _calculate_bb_position(self, period: int = 20, std: float = 2) -> float:
        """计算布林带位置"""
        if self.current_step < period:
            return 0.5

        prices = self.stock_data['close'].iloc[self.current_step - period:self.current_step]
        sma = prices.mean()
        std_dev = prices.std()

        upper = sma + std_dev * std
        lower = sma - std_dev * std
        current_price = self.stock_data.iloc[self.current_step]['close']

        bb_position = (current_price - lower) / (upper - lower)
        return max(0, min(1, bb_position))

    def _calculate_volume_ratio(self, period: int = 20) -> float:
        """计算成交量比率"""
        if self.current_step < period:
            return 1.0

        volumes = self.stock_data['volume'].iloc[self.current_step - period:self.current_step]
        current_volume = self.stock_data.iloc[self.current_step]['volume']
        avg_volume = volumes.mean()

        return min(5.0, current_volume / avg_volume)

    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        current_price = self.stock_data.iloc[min(self.current_step, self.n_steps - 1)]['close']
        portfolio_value = self._get_portfolio_value(current_price)

        return {
            'total_return': (portfolio_value / self.initial_balance - 1) * 100,
            'total_trades': len(self.trades),
            'win_rate': self._calculate_win_rate(),
            'max_drawdown': self._calculate_max_drawdown(),
            'sharpe_ratio': self._calculate_sharpe_ratio(portfolio_value),
            'total_fees': self.total_fees,
            'total_taxes': self.total_taxes
        }

    def _calculate_win_rate(self) -> float:
        """计算胜率"""
        if not self.trades:
            return 0.0

        profitable_trades = 0
        buy_trades = [t for t in self.trades if t.get('action') == 'buy']
        sell_trades = [t for t in self.trades if t.get('action') == 'sell']

        for i in range(min(len(buy_trades), len(sell_trades))):
            if i < len(buy_trades) and i < len(sell_trades):
                buy_trade = buy_trades[i]
                sell_trade = sell_trades[i]
                if sell_trade.get('proceeds', 0) > buy_trade.get('cost', 0):
                    profitable_trades += 1

        return (profitable_trades / max(len(buy_trades), 1)) * 100

    def _calculate_max_drawdown(self) -> float:
        """计算最大回撤"""
        portfolio_values = []
        for i in range(self.n_steps):
            if i < self.current_step:
                price = self.stock_data.iloc[i]['close']
                value = self._get_portfolio_value(price)
                portfolio_values.append(value)

        if not portfolio_values:
            return 0.0

        peak = np.maximum.accumulate(portfolio_values)
        drawdown = (np.array(portfolio_values) - peak) / peak
        return np.min(drawdown) * 100

    def _calculate_sharpe_ratio(self, final_value: float, risk_free_rate: float = 0.03) -> float:
        """计算夏普比率"""
        total_return = (final_value / self.initial_balance - 1)
        trading_days = self.current_step
        annual_return = (1 + total_return) ** (252 / trading_days) - 1
        volatility = 0.15

        return (annual_return - risk_free_rate) / volatility if volatility > 0 else 0


class SimplifiedMultiStockEnv:
    """简化版多股票交易环境"""

    def __init__(self,
                 stock_data_dict: Dict[str, pd.DataFrame],
                 initial_balance: float = 100000,
                 num_stocks_in_portfolio: int = 5,
                 **kwargs):

        self.stock_data_dict = stock_data_dict
        self.stock_symbols = list(stock_data_dict.keys())[:num_stocks_in_portfolio]
        self.n_stocks = len(self.stock_symbols)

        # 环境参数
        self.initial_balance = initial_balance
        self.kwargs = kwargs

        # 创建多个单股票环境
        self.envs = {}
        for symbol in self.stock_symbols:
            self.envs[symbol] = SimplifiedTradingEnv(
                stock_data_dict[symbol],
                initial_balance=initial_balance / num_stocks_in_portfolio,
                **kwargs
            )

        self.observations = {}
        self.reset()

    def reset(self) -> np.ndarray:
        """重置环境"""
        self.observations = {}
        for symbol in self.stock_symbols:
            obs = self.envs[symbol].reset()
            self.observations[symbol] = obs

        return self._get_observation()

    def step(self, actions: List[int]) -> Tuple[np.ndarray, float, bool, Dict[str, Any]]:
        """执行动作"""
        rewards = {}
        dones = {}
        infos = {}

        for i, symbol in enumerate(self.stock_symbols):
            action = actions[i]
            obs, reward, done, info = self.envs[symbol].step(action)
            self.observations[symbol] = obs
            rewards[symbol] = reward
            dones[symbol] = done
            infos[symbol] = info

        # 检查是否所有环境都结束
        done = all(dones.values())

        # 总奖励
        total_reward = sum(rewards.values())

        # 组合信息
        portfolio_info = {
            'total_value': sum(info['portfolio_value'] for info in infos.values()),
            'total_balance': sum(info['balance'] for info in infos.values()),
            'total_trades': sum(info['total_trades'] for info in infos.values())
        }

        return self._get_observation(), total_reward, done, portfolio_info

    def _get_observation(self) -> np.ndarray:
        """获取组合观察"""
        obs_list = []
        for symbol in self.stock_symbols:
            obs_list.extend(self.observations[symbol])
        return np.array(obs_list, dtype=np.float32)


if __name__ == "__main__":
    # 测试代码
    # 生成模拟数据
    dates = pd.date_range('2025-01-01', periods=200, freq='D')
    np.random.seed(42)

    price = 100.0
    prices = []
    for _ in range(200):
        change = np.random.normal(0, 0.02)
        price = price * (1 + change)
        prices.append(price)

    df = pd.DataFrame({
        'date': dates,
        'open': [p * (1 + np.random.normal(0, 0.005)) for p in prices],
        'high': [p * (1 + abs(np.random.normal(0, 0.01))) for p in prices],
        'low': [p * (1 - abs(np.random.normal(0, 0.01))) for p in prices],
        'close': prices,
        'volume': [np.random.randint(500000, 5000000) for _ in range(200)]
    })

    df.set_index('date', inplace=True)

    # 测试单股票环境
    env = SimplifiedTradingEnv(df)

    print("="*60)
    print("Simplified RL Trading Environment - Test")
    print("="*60)

    obs = env.reset()
    print(f"Initial observation shape: {obs.shape}")
    print(f"Initial observation: {obs}")

    total_reward = 0
    steps = 0

    # 随机策略测试
    for _ in range(50):
        action = np.random.choice([0, 1, 2])
        obs, reward, done, info = env.step(action)
        total_reward += reward
        steps += 1

        if done:
            break

    stats = env.get_statistics()

    print(f"\nTest completed after {steps} steps")
    print(f"Total reward: {total_reward:.2f}")
    print(f"Average reward per step: {total_reward/steps:.2f}")
    print(f"\nStatistics:")
    print(f"- Total return: {stats['total_return']:.2f}%")
    print(f"- Total trades: {stats['total_trades']}")
    print(f"- Win rate: {stats['win_rate']:.2f}%")
    print(f"- Max drawdown: {stats['max_drawdown']:.2f}%")
    print(f"- Sharpe ratio: {stats['sharpe_ratio']:.2f}")
    print("="*60)
    print("Test completed successfully!")
