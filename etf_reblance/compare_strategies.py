#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
对比两种投资策略：不再平衡 vs 定期再平衡
"""

import pandas as pd
import numpy as np


def load_results():
    """加载两种策略的回测结果"""
    
    # 加载原始策略（不再平衡）
    df_original = pd.read_csv('backtest_result.csv', parse_dates=['Date'], index_col='Date')
    
    # 加载再平衡策略
    df_rebalance = pd.read_csv('backtest_rebalance_result.csv', parse_dates=['Date'], index_col='Date')
    
    return df_original, df_rebalance


def calculate_metrics(df):
    """计算性能指标"""
    
    # 总收益率
    total_return = df['return'].iloc[-1]
    
    # 年化收益率
    days = (df.index[-1] - df.index[0]).days
    years = days / 365.25
    final_value = df['total_value'].iloc[-1]
    initial_invest = df['cumulative_invest'].iloc[-1]
    annualized_return = (pow(final_value / initial_invest, 1/years) - 1) * 100
    
    # 最大回撤
    rolling_max = df['total_value'].expanding().max()
    drawdown = (df['total_value'] - rolling_max) / rolling_max * 100
    max_drawdown = drawdown.min()
    
    # 波动率（年化）
    daily_returns = df['total_value'].pct_change().dropna()
    volatility = daily_returns.std() * np.sqrt(252) * 100
    
    # 夏普比率（假设无风险利率3%）
    risk_free_rate = 0.03
    sharpe_ratio = (annualized_return / 100 - risk_free_rate) / (volatility / 100)
    
    return {
        'total_return': total_return,
        'annualized_return': annualized_return,
        'max_drawdown': max_drawdown,
        'volatility': volatility,
        'sharpe_ratio': sharpe_ratio,
        'final_value': final_value,
        'total_profit': df['profit'].iloc[-1]
    }


def compare_asset_allocation(df_original, df_rebalance):
    """对比最终资产配置"""
    
    assets = ['nasdaq100', 'sp500', 'csi930955', 'csi980092']
    asset_names = ['纳斯达克100', '标普500', '红利低波100', '自由现金流']
    
    print("\n📊 最终资产配置对比")
    print("="*80)
    print(f"{'资产':<15} | {'不再平衡':<20} | {'定期再平衡':<20} | {'差异':<15}")
    print("-"*80)
    
    for asset, name in zip(assets, asset_names):
        value_col = f'{asset}_value'
        
        value_orig = df_original[value_col].iloc[-1]
        value_rebal = df_rebalance[value_col].iloc[-1]
        
        total_orig = df_original['total_value'].iloc[-1]
        total_rebal = df_rebalance['total_value'].iloc[-1]
        
        pct_orig = value_orig / total_orig * 100
        pct_rebal = value_rebal / total_rebal * 100
        
        diff = pct_rebal - pct_orig
        
        print(f"{name:<15} | {pct_orig:>6.2f}% (¥{value_orig:>8,.0f}) | " +
              f"{pct_rebal:>6.2f}% (¥{value_rebal:>8,.0f}) | {diff:>+6.2f}%")
    
    print("="*80)


def main():
    """主函数"""
    print("\n" + "="*80)
    print("投资策略对比分析")
    print("="*80)
    
    # 加载数据
    print("\n正在加载回测数据...")
    df_original, df_rebalance = load_results()
    
    # 计算指标
    metrics_orig = calculate_metrics(df_original)
    metrics_rebal = calculate_metrics(df_rebalance)
    
    # 整体对比
    print("\n📈 整体收益对比")
    print("="*80)
    print(f"{'指标':<20} | {'不再平衡':<25} | {'定期再平衡':<25} | {'差异':<15}")
    print("-"*80)
    
    # 最终市值
    print(f"{'最终市值':<20} | ¥{metrics_orig['final_value']:>23,.2f} | " +
          f"¥{metrics_rebal['final_value']:>23,.2f} | " +
          f"¥{metrics_rebal['final_value'] - metrics_orig['final_value']:>+13,.2f}")
    
    # 总收益
    print(f"{'总收益':<20} | ¥{metrics_orig['total_profit']:>23,.2f} | " +
          f"¥{metrics_rebal['total_profit']:>23,.2f} | " +
          f"¥{metrics_rebal['total_profit'] - metrics_orig['total_profit']:>+13,.2f}")
    
    # 总收益率
    print(f"{'总收益率':<20} | {metrics_orig['total_return']:>23.2f}% | " +
          f"{metrics_rebal['total_return']:>23.2f}% | " +
          f"{metrics_rebal['total_return'] - metrics_orig['total_return']:>+13.2f}%")
    
    # 年化收益率
    print(f"{'年化收益率':<20} | {metrics_orig['annualized_return']:>23.2f}% | " +
          f"{metrics_rebal['annualized_return']:>23.2f}% | " +
          f"{metrics_rebal['annualized_return'] - metrics_orig['annualized_return']:>+13.2f}%")
    
    # 最大回撤
    print(f"{'最大回撤':<20} | {metrics_orig['max_drawdown']:>23.2f}% | " +
          f"{metrics_rebal['max_drawdown']:>23.2f}% | " +
          f"{metrics_rebal['max_drawdown'] - metrics_orig['max_drawdown']:>+13.2f}%")
    
    # 年化波动率
    print(f"{'年化波动率':<20} | {metrics_orig['volatility']:>23.2f}% | " +
          f"{metrics_rebal['volatility']:>23.2f}% | " +
          f"{metrics_rebal['volatility'] - metrics_orig['volatility']:>+13.2f}%")
    
    # 夏普比率
    print(f"{'夏普比率':<20} | {metrics_orig['sharpe_ratio']:>27.3f} | " +
          f"{metrics_rebal['sharpe_ratio']:>27.3f} | " +
          f"{metrics_rebal['sharpe_ratio'] - metrics_orig['sharpe_ratio']:>+15.3f}")
    
    print("="*80)
    
    # 资产配置对比
    compare_asset_allocation(df_original, df_rebalance)
    
    # 结论分析
    print("\n💡 策略分析")
    print("="*80)
    
    if metrics_rebal['total_return'] > metrics_orig['total_return']:
        winner = "定期再平衡"
        diff = metrics_rebal['total_return'] - metrics_orig['total_return']
        diff_value = metrics_rebal['total_profit'] - metrics_orig['total_profit']
    else:
        winner = "不再平衡"
        diff = metrics_orig['total_return'] - metrics_rebal['total_return']
        diff_value = metrics_orig['total_profit'] - metrics_rebal['total_profit']
    
    print(f"\n🏆 收益优胜: {winner} 策略")
    print(f"   收益率优势: {abs(diff):.2f}%")
    print(f"   收益额优势: ¥{abs(diff_value):,.2f}")
    
    # 风险对比
    if abs(metrics_rebal['max_drawdown']) < abs(metrics_orig['max_drawdown']):
        risk_winner = "定期再平衡"
        risk_diff = abs(metrics_orig['max_drawdown']) - abs(metrics_rebal['max_drawdown'])
    else:
        risk_winner = "不再平衡"
        risk_diff = abs(metrics_rebal['max_drawdown']) - abs(metrics_orig['max_drawdown'])
    
    print(f"\n🛡️  风险优胜: {risk_winner} 策略")
    print(f"   回撤优势: {risk_diff:.2f}%")
    
    # 夏普比率对比
    if metrics_rebal['sharpe_ratio'] > metrics_orig['sharpe_ratio']:
        sharpe_winner = "定期再平衡"
    else:
        sharpe_winner = "不再平衡"
    
    print(f"\n⚖️  风险调整后收益: {sharpe_winner} 策略更优")
    print(f"   夏普比率: {max(metrics_rebal['sharpe_ratio'], metrics_orig['sharpe_ratio']):.3f}")
    
    # 建议
    print("\n📋 投资建议")
    print("="*80)
    
    if winner == "不再平衡" and sharpe_winner == "不再平衡":
        print("✅ 在本回测期间，不再平衡策略表现更优")
        print("   - 收益更高，风险调整后收益也更好")
        print("   - 适合牛市环境，让强势资产充分上涨")
        print("   - 但要注意集中度风险和极端市场风险")
    elif winner == "定期再平衡" and sharpe_winner == "定期再平衡":
        print("✅ 在本回测期间，定期再平衡策略表现更优")
        print("   - 收益更高，风险控制也更好")
        print("   - 适合震荡市场，能够高抛低吸")
        print("   - 维持组合平衡，降低集中度风险")
    else:
        print("⚖️  两种策略各有优劣")
        print(f"   - 收益方面: {winner} 策略更优")
        print(f"   - 风险方面: {risk_winner} 策略更优")
        print("   - 建议根据市场环境和风险偏好选择")
    
    print("\n" + "="*80)
    print("\n✅ 对比分析完成！\n")


if __name__ == '__main__':
    main()

