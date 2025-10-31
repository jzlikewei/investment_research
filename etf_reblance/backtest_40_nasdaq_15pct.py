#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ETF投资组合回测系统 - 40%纳指 + 相对阈值15%再平衡

策略：
- 初始资金：100万
- 时间范围：2015-01-01 至 2025-10-30
- 仓位分配：纳指40% + 标普20% + 红利20% + 自由现金流20%
- 初始买入20%，剩余80%定投2年
- 定投结束后，当资产偏离目标权重的15%时触发再平衡
  例如：40%的纳指，阈值=40%×15%=6%，触发范围34%-46%
       20%的资产，阈值=20%×15%=3%，触发范围17%-23%
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os


class ETFBacktest40Nasdaq15pct:
    """ETF投资组合回测类 - 40%纳指 + 相对阈值15%再平衡"""
    
    def __init__(self, initial_capital=1000000, start_date='2015-01-01', end_date='2025-10-30'):
        """
        初始化回测参数
        
        参数:
            initial_capital: 初始资金
            start_date: 开始日期
            end_date: 结束日期
        """
        self.initial_capital = initial_capital
        self.start_date = pd.to_datetime(start_date)
        self.end_date = pd.to_datetime(end_date)
        
        # 投资组合配置 - 重仓纳指
        self.portfolio_config = {
            'nasdaq100': {'weight': 0.40, 'name': '纳斯达克100'},
            'sp500': {'weight': 0.20, 'name': '标普500'},
            'csi930955': {'weight': 0.20, 'name': '中证红利低波100'},
            'csi980092': {'weight': 0.20, 'name': '自由现金流指数'}
        }
        
        # 投资策略参数
        self.initial_investment_ratio = 0.20  # 初始买入20%
        self.regular_investment_years = 2      # 定投2年
        self.relative_threshold = 0.15         # 相对阈值15%（更严格）
        
        self.data = {}
        self.portfolio = None
        self.rebalance_dates = []
        self.rebalance_reasons = []
        
    def load_data(self):
        """加载指数数据"""
        print("="*60)
        print("加载指数数据")
        print("="*60)
        
        data_path = '../data/processed'
        
        # 数据文件映射
        data_files = {
            'nasdaq100': 'nasdaq100_normalized.csv',
            'sp500': 'sp500_normalized.csv',
            'csi930955': '930955_normalized.csv',
            'csi980092': '980092_normalized.csv'
        }
        
        for key, filename in data_files.items():
            filepath = os.path.join(data_path, filename)
            df = pd.read_csv(filepath, parse_dates=['Date'])
            df = df.set_index('Date')
            
            # 去除重复日期（保留第一个）
            if df.index.duplicated().any():
                print(f"   ⚠️  {filename} 包含 {df.index.duplicated().sum()} 个重复日期，已去重")
                df = df[~df.index.duplicated(keep='first')]
            
            # 筛选日期范围
            df = df[(df.index >= self.start_date) & (df.index <= self.end_date)]
            
            self.data[key] = df
            
            # 计算该资产的绝对阈值
            abs_threshold = self.portfolio_config[key]['weight'] * self.relative_threshold
            lower_bound = (self.portfolio_config[key]['weight'] - abs_threshold) * 100
            upper_bound = (self.portfolio_config[key]['weight'] + abs_threshold) * 100
            
            print(f"✅ {self.portfolio_config[key]['name']}: {len(df)} 条数据")
            print(f"   目标{self.portfolio_config[key]['weight']*100:.0f}%, 触发范围[{lower_bound:.0f}%-{upper_bound:.0f}%]")
        
        print()
        
    def align_dates(self):
        """对齐所有指数的交易日期"""
        print("对齐交易日期...")
        
        # 获取所有数据的日期交集
        common_dates = self.data['nasdaq100'].index
        for key in self.data:
            common_dates = common_dates.intersection(self.data[key].index)
        
        # 排序共同日期
        common_dates = common_dates.sort_values()
        
        # 筛选共同日期
        for key in self.data:
            self.data[key] = self.data[key].loc[common_dates].sort_index()
        
        print(f"✅ 共同交易日: {len(common_dates)} 天")
        print(f"   日期范围: {common_dates[0].strftime('%Y-%m-%d')} 至 {common_dates[-1].strftime('%Y-%m-%d')}\n")
        
    def check_rebalance_needed(self, date_idx, shares_dict, prices_dict):
        """检查是否需要再平衡 - 使用相对阈值15%"""
        
        # 计算当前各资产市值和总市值
        total_value = 0
        asset_values = {}
        for key in self.portfolio_config.keys():
            value = shares_dict[key][date_idx] * prices_dict[key][date_idx]
            asset_values[key] = value
            total_value += value
        
        # 检查每个资产的占比是否超出其相对阈值
        triggers = []
        for key, config in self.portfolio_config.items():
            current_weight = asset_values[key] / total_value
            target_weight = config['weight']
            
            # 计算该资产的绝对阈值（目标权重的15%）
            abs_threshold = target_weight * self.relative_threshold
            deviation = abs(current_weight - target_weight)
            
            if deviation > abs_threshold:
                triggers.append({
                    'asset': config['name'],
                    'target': target_weight * 100,
                    'current': current_weight * 100,
                    'deviation': deviation * 100,
                    'threshold': abs_threshold * 100
                })
        
        if len(triggers) > 0:
            reason = "; ".join([
                f"{t['asset']}: {t['current']:.1f}% (目标{t['target']:.0f}%, 偏离{t['deviation']:.1f}%, 阈值{t['threshold']:.0f}%)"
                for t in triggers
            ])
            return True, reason
        
        return False, ""
        
    def rebalance_portfolio(self, date_idx, shares_dict, prices_dict):
        """执行再平衡"""
        
        # 计算当前总市值
        total_value = 0
        for key in self.portfolio_config.keys():
            total_value += shares_dict[key][date_idx] * prices_dict[key][date_idx]
        
        # 按目标权重重新分配
        new_shares = {}
        for key, config in self.portfolio_config.items():
            target_value = total_value * config['weight']
            new_shares[key] = target_value / prices_dict[key][date_idx]
        
        return new_shares, total_value
        
    def run_backtest(self):
        """执行回测"""
        print("="*60)
        print("开始回测 - 40%纳指 + 相对阈值15%再平衡")
        print("="*60)
        
        dates = self.data['nasdaq100'].index
        self.portfolio = pd.DataFrame(index=dates)
        
        initial_invest = self.initial_capital * self.initial_investment_ratio
        remaining = self.initial_capital - initial_invest
        
        regular_invest_end = dates[0] + timedelta(days=self.regular_investment_years * 365)
        regular_invest_dates = dates[dates <= regular_invest_end]
        daily_invest = remaining / len(regular_invest_dates) if len(regular_invest_dates) > 0 else 0
        
        print(f"初始投资: ¥{initial_invest:,.2f} ({self.initial_investment_ratio*100}%)")
        print(f"定投金额: ¥{remaining:,.2f}")
        print(f"定投天数: {len(regular_invest_dates)} 天")
        print(f"每日定投: ¥{daily_invest:,.2f}")
        print(f"定投结束日: {regular_invest_dates[-1].strftime('%Y-%m-%d')}")
        print(f"相对阈值: 目标权重的{self.relative_threshold*100:.0f}%")
        print()
        
        # 初始化各资产数据
        shares_dict = {}
        prices_dict = {}
        
        for key in self.portfolio_config.keys():
            prices_dict[key] = self.data[key]['Close'].values
            shares_dict[key] = np.zeros(len(dates))
            initial_price = prices_dict[key][0]
            shares_dict[key][0] = (initial_invest * self.portfolio_config[key]['weight']) / initial_price
        
        # 模拟投资过程
        for i in range(len(dates)):
            if i > 0:
                current_date = dates[i]
                
                if current_date <= regular_invest_end:
                    for key, config in self.portfolio_config.items():
                        price = prices_dict[key][i]
                        new_shares = (daily_invest * config['weight']) / price
                        shares_dict[key][i] = shares_dict[key][i-1] + new_shares
                else:
                    for key in self.portfolio_config.keys():
                        shares_dict[key][i] = shares_dict[key][i-1]
                    
                    need_rebalance, reason = self.check_rebalance_needed(i, shares_dict, prices_dict)
                    
                    if need_rebalance:
                        print(f"触发再平衡: {current_date.strftime('%Y-%m-%d')}")
                        print(f"  原因: {reason}")
                        
                        new_shares, total_value = self.rebalance_portfolio(i, shares_dict, prices_dict)
                        
                        for key in self.portfolio_config.keys():
                            shares_dict[key][i] = new_shares[key]
                        
                        print(f"  总市值: ¥{total_value:,.2f}\n")
                        
                        self.rebalance_dates.append(current_date)
                        self.rebalance_reasons.append(reason)
        
        # 保存到投资组合
        for key in self.portfolio_config.keys():
            self.portfolio[f'{key}_shares'] = shares_dict[key]
            self.portfolio[f'{key}_value'] = shares_dict[key] * prices_dict[key]
        
        value_columns = [col for col in self.portfolio.columns if col.endswith('_value')]
        self.portfolio['total_value'] = self.portfolio[value_columns].sum(axis=1)
        self.portfolio['return'] = (self.portfolio['total_value'] / self.initial_capital - 1) * 100
        
        cumulative_invest = pd.Series(initial_invest, index=dates)
        for i, date in enumerate(dates):
            if i > 0:
                if date <= regular_invest_end:
                    cumulative_invest.iloc[i] = cumulative_invest.iloc[i-1] + daily_invest
                else:
                    cumulative_invest.iloc[i] = cumulative_invest.iloc[i-1]
        
        self.portfolio['cumulative_invest'] = cumulative_invest
        self.portfolio['profit'] = self.portfolio['total_value'] - self.portfolio['cumulative_invest']
        
        print(f"✅ 回测完成")
        print(f"   触发再平衡次数: {len(self.rebalance_dates)} 次\n")
        
    def generate_report(self):
        """生成收益报告"""
        print("="*60)
        print("投资收益报告 - 40%纳指 + 相对阈值15%再平衡")
        print("="*60)
        
        print(f"\n📅 投资周期")
        print(f"   开始日期: {self.portfolio.index[0].strftime('%Y-%m-%d')}")
        print(f"   结束日期: {self.portfolio.index[-1].strftime('%Y-%m-%d')}")
        print(f"   投资天数: {len(self.portfolio)} 天")
        print(f"   再平衡次数: {len(self.rebalance_dates)} 次")
        print(f"   相对阈值: 目标权重的{self.relative_threshold*100:.0f}%")
        
        print(f"\n💰 投资金额")
        print(f"   初始资金: ¥{self.initial_capital:,.2f}")
        print(f"   累计投入: ¥{self.portfolio['cumulative_invest'].iloc[-1]:,.2f}")
        
        final_value = self.portfolio['total_value'].iloc[-1]
        total_profit = self.portfolio['profit'].iloc[-1]
        total_return = self.portfolio['return'].iloc[-1]
        
        print(f"\n📈 最终资产")
        print(f"   总市值: ¥{final_value:,.2f}")
        print(f"   总收益: ¥{total_profit:,.2f}")
        print(f"   收益率: {total_return:.2f}%")
        
        print(f"\n📊 各资产表现")
        for key, config in self.portfolio_config.items():
            shares = self.portfolio[f'{key}_shares'].iloc[-1]
            value = self.portfolio[f'{key}_value'].iloc[-1]
            weight = value / final_value * 100
            target_weight = config['weight'] * 100
            
            deviation = abs(weight - target_weight)
            abs_threshold = config['weight'] * self.relative_threshold * 100
            
            initial_price = self.data[key].iloc[0]['Close']
            final_price = self.data[key].iloc[-1]['Close']
            price_return = (final_price / initial_price - 1) * 100
            
            print(f"\n   {config['name']}:")
            print(f"      目标权重: {target_weight:.0f}% | 实际权重: {weight:.2f}% (偏离{deviation:.2f}%, 阈值{abs_threshold:.0f}%)")
            print(f"      当前市值: ¥{value:,.2f}")
            print(f"      贡献利润: ¥{value - self.portfolio[f'{key}_value'].iloc[0]:,.2f}")
            print(f"      价格涨幅: {price_return:.2f}%")
        
        days = (self.portfolio.index[-1] - self.portfolio.index[0]).days
        years = days / 365.25
        annualized_return = (pow(final_value / self.portfolio['cumulative_invest'].iloc[-1], 1/years) - 1) * 100
        
        print(f"\n📉 风险指标")
        print(f"   投资年限: {years:.2f} 年")
        print(f"   年化收益率: {annualized_return:.2f}%")
        
        rolling_max = self.portfolio['total_value'].expanding().max()
        drawdown = (self.portfolio['total_value'] - rolling_max) / rolling_max * 100
        max_drawdown = drawdown.min()
        max_drawdown_date = drawdown.idxmin()
        
        print(f"   最大回撤: {max_drawdown:.2f}%")
        print(f"   回撤日期: {max_drawdown_date.strftime('%Y-%m-%d')}")
        
        daily_returns = self.portfolio['total_value'].pct_change().dropna()
        volatility = daily_returns.std() * np.sqrt(252) * 100
        sharpe_ratio = (annualized_return / 100 - 0.03) / (volatility / 100)
        
        downside_returns = daily_returns[daily_returns < 0]
        downside_std = downside_returns.std() * np.sqrt(252) * 100
        sortino_ratio = (annualized_return / 100 - 0.03) / (downside_std / 100)
        
        print(f"   年化波动率: {volatility:.2f}%")
        print(f"   下行波动率: {downside_std:.2f}%")
        print(f"   夏普比率: {sharpe_ratio:.3f}")
        print(f"   索提诺比率: {sortino_ratio:.3f}")
        
        output_file = 'backtest_40_nasdaq_15pct_result.csv'
        self.portfolio.to_csv(output_file)
        print(f"\n💾 详细数据已保存至: {output_file}")
        
        print("\n" + "="*60)
        
        return {
            'final_value': final_value,
            'total_profit': total_profit,
            'total_return': total_return,
            'annualized_return': annualized_return,
            'max_drawdown': max_drawdown,
            'sharpe_ratio': sharpe_ratio,
            'sortino_ratio': sortino_ratio,
            'rebalance_count': len(self.rebalance_dates)
        }


def main():
    """主函数"""
    print("\n" + "="*60)
    print("ETF投资组合回测系统")
    print("40%纳指 + 相对阈值15%再平衡（更严格）")
    print("="*60 + "\n")
    
    backtest = ETFBacktest40Nasdaq15pct(
        initial_capital=1000000,
        start_date='2015-01-01',
        end_date='2025-10-30'
    )
    
    backtest.load_data()
    backtest.align_dates()
    backtest.run_backtest()
    result = backtest.generate_report()
    
    print("\n✅ 回测完成！")
    print()


if __name__ == '__main__':
    main()

