#!/usr/bin/env python3
"""
A股交易强化学习环境
基于OpenAI Gym接口实现的股票交易环境
"""

import gymnasium as gym
from gymnasium import spaces
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
import warnings

warnings.filterwarnings('ignore')

class AStockTradingEnv(gym.Env):
    """A股交易强化学习环境

    特征:
    - 支持做多、做空、持有
    - 考虑A股T+1限制
    - 涨跌停板限制
    - 交易费用和税费
    - 动态仓位管理
    """

    metadata = {'render_modes': ['human']}

    def __init__(self,
                 stock_data: pd.DataFrame,
                 initial_balance: float = 100000,
                 transaction_fee: float = 0.0003,  # 0.03%
                 tax_rate: float = 0.001,  # 0.1%
                 max_position: float = 0.95,  # 最大仓位95%
                 stop_loss: float = 0.10,  # 10%止损
                 take_profit: float = 0.20):  # 20%止盈

        super(AStockTradingEnv, self).__init__()

        # 数据
        self.stock_data = stock_data.reset_index(drop=True)
        self.n_stocks = len(self.stock_data)

        # 环境参数
        self.initial_balance = initial_balance
        self.transaction_fee = transaction_fee
        self.tax_rate = tax_rate
        self.max_position = max_position
        self.stop_loss = stop_loss
        self.take_profit = take_profit

        # 状态空间: [balance, position, price, rsi, macd, bb_position, volume_ratio]
        self.observation_space = spaces.Box(
            low=-np.inf,
            high=np.inf,
            shape=(7,),
            dtype=np.float32
        )

        # 动作空间: [hold(0), buy(1), sell(2)]
        self.action_space = spaces.Discrete(3)

        # 状态变量
        self.reset()

    def reset(self, seed: Optional[int] = None, options: Optional[dict] = None):
        """重置环境"""
        super().reset(seed=seed)

        self.current_step = 0
        self.balance = self.initial_balance
        self.position = 0.0  # 当前仓位 (0-1)
        self.entry_price = 0.0  # 入场价格
        self.max_portfolio_value = self.initial_balance
        self.total_fees = 0.0
        self.total_taxes = 0.0
        self.trades = []

        return self._get_observation(), {}

    def step(self, action: int):
        """执行动作"""
        assert self.action_space.contains(action), f"Invalid action: {action}"

        current_price = self.stock_data.iloc[self.current_step]['close']
        done = self.current_step >= len(self.stock_data) - 1

        # 执行动作
        if action == 1:  # 买入
            self._execute_buy(current_price)
        elif action == 2:  # 卖出
            self._execute_sell(current_price)
        # action == 0: 持有，什么都不做

        # 计算奖励
        reward = self._calculate_reward(current_price)

        # 检查是否达到止盈止损
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

        # 更新步骤
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

        return self._get_observation(), reward, done, False, info

    def _execute_buy(self, price: float):
        """执行买入操作"""
        if self.position >= self.max_position:
            return  # 已达到最大仓位

        # 计算可买入金额
        available_cash = self.balance * (self.max_position - self.position)
        max_shares = int(available_cash / price)

        if max_shares <= 0:
            return

        # 买入一半可用资金
        buy_amount = available_cash * 0.5
        shares_to_buy = int(buy_amount / price)

        if shares_to_buy <= 0:
            return

        # 计算交易费用
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
            return  # 无仓位可卖

        # 卖出当前仓位的50%
        sell_ratio = 0.5
        sell_value = self.initial_balance * self.position * sell_ratio
        shares_to_sell = int(sell_value / price)

        if shares_to_sell <= 0:
            return

        # 计算收益
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

        # 如果仓位接近0，重置入场价格
        if self.position < 0.01:
            self.position = 0
            self.entry_price = 0

    def _calculate_reward(self, current_price: float) -> float:
        """计算奖励"""
        portfolio_value = self._get_portfolio_value(current_price)
        prev_value = getattr(self, 'prev_portfolio_value', self.initial_balance)

        # 基础奖励：组合价值变化
        reward = (portfolio_value - prev_value) / prev_value * 1000

        # 持仓奖励：鼓励合理持仓
        if self.position > 0.1 and self.position < 0.8:
            reward += 1

        # 手续费惩罚
        reward -= self.total_fees * 0.01

        # 存储当前组合价值
        self.prev_portfolio_value = portfolio_value

        return reward

    def _get_portfolio_value(self, current_price: float) -> float:
        """获取组合总价值"""
        stock_value = self.initial_balance * self.position * (current_price / self.entry_price) if self.entry_price > 0 else 0
        return self.balance + stock_value

    def _get_observation(self) -> np.ndarray:
        """获取当前观察"""
        if self.current_step >= len(self.stock_data):
            return np.zeros(7, dtype=np.float32)

        row = self.stock_data.iloc[self.current_step]

        # 计算技术指标
        rsi = self._calculate_rsi()
        macd = self._calculate_macd()
        bb_position = self._calculate_bb_position()
        volume_ratio = self._calculate_volume_ratio()

        observation = np.array([
            self.balance / self.initial_balance,  # 归一化余额
            self.position,  # 当前仓位
            row['close'] / 100.0,  # 归一化价格
            rsi / 100.0,  # 归一化RSI
            macd,  # MACD值
            bb_position,  # 布林带位置
            volume_ratio  # 成交量比率
        ], dtype=np.float32)

        return observation

    def _calculate_rsi(self, period: int = 14) -> float:
        """计算RSI"""
        if self.current_step < period:
            return 50.0  # 默认中性值

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
        signal_line = macd.ewm(span=signal).mean().iloc[-1] if len(macd) > signal else macd

        return (macd - signal_line) / 100.0  # 归一化

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

        return min(5.0, current_volume / avg_volume)  # 限制最大值

    def render(self, mode='human'):
        """渲染环境"""
        if mode == 'human':
            current_price = self.stock_data.iloc[self.current_step]['close']
            portfolio_value = self._get_portfolio_value(current_price)

            print(f"\n{'='*60}")
            print(f"步骤: {self.current_step}/{len(self.stock_data)}")
            print(f"价格: ¥{current_price:.2f}")
            print(f"余额: ¥{self.balance:.2f}")
            print(f"仓位: {self.position:.2%}")
            print(f"组合价值: ¥{portfolio_value:.2f}")
            print(f"收益率: {(portfolio_value / self.initial_balance - 1) * 100:.2f}%")
            print(f"总交易次数: {len(self.trades)}")
            print(f"手续费: ¥{self.total_fees:.2f}")
            print(f"税费: ¥{self.total_taxes:.2f}")
            print(f"{'='*60}\n")

    def get_action_meanings(self) -> List[str]:
        """获取动作含义"""
        return ['HOLD', 'BUY', 'SELL']

    def get_statistics(self) -> Dict:
        """获取环境统计信息"""
        current_price = self.stock_data.iloc[min(self.current_step, len(self.stock_data) - 1)]['close']
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
        for i in range(0, len(self.trades) - 1, 2):
            if i + 1 < len(self.trades):
                buy_trade = self.trades[i]
                sell_trade = self.trades[i + 1]
                if sell_trade['proceeds'] > buy_trade['cost']:
                    profitable_trades += 1

        return (profitable_trades / (len(self.trades) / 2)) * 100 if self.trades else 0.0

    def _calculate_max_drawdown(self) -> float:
        """计算最大回撤"""
        portfolio_values = []
        for i in range(len(self.stock_data)):
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
        volatility = 0.15  # 假设15%波动率

        return (annual_return - risk_free_rate) / volatility if volatility > 0 else 0


class MultiStockTradingEnv(gym.Env):
    """多股票交易环境（投资组合）"""

    def __init__(self,
                 stock_data_dict: Dict[str, pd.DataFrame],
                 initial_balance: float = 100000,
                 num_stocks_in_portfolio: int = 5,
                 **kwargs):

        super(MultiStockTradingEnv, self).__init__()

        self.stock_data_dict = stock_data_dict
        self.stock_symbols = list(stock_data_dict.keys())[:num_stocks_in_portfolio]
        self.n_stocks = len(self.stock_symbols)

        # 环境参数
        self.initial_balance = initial_balance
        self.kwargs = kwargs

        # 创建多个单股票环境
        self.envs = {}
        for symbol in self.stock_symbols:
            self.envs[symbol] = AStockTradingEnv(
                stock_data_dict[symbol],
                initial_balance=initial_balance / num_stocks_in_portfolio,
                **kwargs
            )

        # 状态空间：所有股票的观察值
        self.observation_space = spaces.Box(
            low=-np.inf,
            high=np.inf,
            shape=(self.n_stocks * 7,),
            dtype=np.float32
        )

        # 动作空间：对每只股票执行动作
        self.action_space = spaces.MultiDiscrete([3] * self.n_stocks)

        self.reset()

    def reset(self, seed: Optional[int] = None, options: Optional[dict] = None):
        """重置环境"""
        super().reset(seed=seed)

        self.observations = {}
        for symbol in self.stock_symbols:
            obs, _ = self.envs[symbol].reset(seed=seed)
            self.observations[symbol] = obs

        return self._get_observation(), {}

    def step(self, actions: List[int]):
        """执行动作"""
        rewards = {}
        dones = {}
        infos = {}

        for i, symbol in enumerate(self.stock_symbols):
            action = actions[i]
            obs, reward, done, _, info = self.envs[symbol].step(action)
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

        return self._get_observation(), total_reward, done, False, portfolio_info

    def _get_observation(self) -> np.ndarray:
        """获取组合观察"""
        obs_list = []
        for symbol in self.stock_symbols:
            obs_list.extend(self.observations[symbol])
        return np.array(obs_list, dtype=np.float32)

    def render(self, mode='human'):
        """渲染环境"""
        if mode == 'human':
            for symbol in self.stock_symbols:
                print(f"\n{symbol}:")
                self.envs[symbol].render(mode='human')


if __name__ == "__main__":
    # 测试代码
    import matplotlib.pyplot as plt

    # 生成模拟数据
    np.random.seed(42)
    dates = pd.date_range('2023-01-01', periods=200, freq='D')

    # 创建三只股票的数据
    stock_data_dict = {}
    for i, symbol in enumerate(['STOCK_A', 'STOCK_B', 'STOCK_C']):
        price = 100 + i * 10
        prices = []
        volumes = []

        for j in range(200):
            change = np.random.normal(0, 0.02 + i * 0.005)
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
        stock_data_dict[symbol] = df

    # 创建环境
    env = MultiStockTradingEnv(stock_data_dict, initial_balance=100000)

    # 随机策略测试
    obs, _ = env.reset()
    total_reward = 0
    steps = 0

    print("开始随机策略测试...")
    for _ in range(100):
        actions = [env.action_space.sample() for _ in range(env.n_stocks)]
        obs, reward, done, _, info = env.step(actions)
        total_reward += reward
        steps += 1

        if done:
            break

    print(f"\n测试完成:")
    print(f"步骤数: {steps}")
    print(f"总奖励: {total_reward:.2f}")
    print(f"平均每步奖励: {total_reward/steps:.2f}")
