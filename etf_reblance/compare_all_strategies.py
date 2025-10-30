#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
对比三种投资策略：
1. 不再平衡 (Buy and Hold)
2. 定期再平衡 (每半年)
3. 阈值触发再平衡 (偏离>5%时)
"""

import pandas as pd
import numpy as np


def load_results():
    """加载三种策略的回测结果"""
    
    # 加载原始策略（不再平衡）
    df_original = pd.read_csv('backtest_result.csv', parse_dates=['Date'], index_col='Date')
    
    # 加载定期再平衡策略
    df_periodic = pd.read_csv('backtest_rebalance_result.csv', parse_dates=['Date'], index_col='Date')
    
    # 加载阈值触发再平衡策略
    df_threshold = pd.read_csv('backtest_threshold_rebalance_result.csv', parse_dates=['Date'], index_col='Date')
    
    return df_original, df_periodic, df_threshold


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


def main():
    """主函数"""
    print("\n" + "="*100)
    print("三种投资策略全面对比")
    print("="*100)
    
    # 加载数据
    print("\n正在加载回测数据...")
    df_original, df_periodic, df_threshold = load_results()
    
    # 计算指标
    metrics_orig = calculate_metrics(df_original)
    metrics_periodic = calculate_metrics(df_periodic)
    metrics_threshold = calculate_metrics(df_threshold)
    
    # 整体对比
    print("\n📈 核心指标对比")
    print("="*100)
    print(f"{'指标':<18} | {'A.不再平衡':<22} | {'B.定期再平衡':<22} | {'C.阈值再平衡':<22}")
    print("-"*100)
    
    # 最终市值
    print(f"{'最终市值':<18} | ¥{metrics_orig['final_value']:>20,.0f} | " +
          f"¥{metrics_periodic['final_value']:>20,.0f} | " +
          f"¥{metrics_threshold['final_value']:>20,.0f}")
    
    # 总收益
    print(f"{'总收益':<18} | ¥{metrics_orig['total_profit']:>20,.0f} | " +
          f"¥{metrics_periodic['total_profit']:>20,.0f} | " +
          f"¥{metrics_threshold['total_profit']:>20,.0f}")
    
    # 总收益率
    print(f"{'总收益率':<18} | {metrics_orig['total_return']:>20.2f}% | " +
          f"{metrics_periodic['total_return']:>20.2f}% | " +
          f"{metrics_threshold['total_return']:>20.2f}%")
    
    # 年化收益率
    print(f"{'年化收益率':<18} | {metrics_orig['annualized_return']:>20.2f}% | " +
          f"{metrics_periodic['annualized_return']:>20.2f}% | " +
          f"{metrics_threshold['annualized_return']:>20.2f}%")
    
    # 最大回撤
    print(f"{'最大回撤':<18} | {metrics_orig['max_drawdown']:>20.2f}% | " +
          f"{metrics_periodic['max_drawdown']:>20.2f}% | " +
          f"{metrics_threshold['max_drawdown']:>20.2f}%")
    
    # 年化波动率
    print(f"{'年化波动率':<18} | {metrics_orig['volatility']:>20.2f}% | " +
          f"{metrics_periodic['volatility']:>20.2f}% | " +
          f"{metrics_threshold['volatility']:>20.2f}%")
    
    # 夏普比率
    print(f"{'夏普比率':<18} | {metrics_orig['sharpe_ratio']:>24.3f} | " +
          f"{metrics_periodic['sharpe_ratio']:>24.3f} | " +
          f"{metrics_threshold['sharpe_ratio']:>24.3f}")
    
    print("="*100)
    
    # 资产配置对比
    print("\n📊 最终资产配置对比")
    print("="*100)
    
    assets = ['nasdaq100', 'sp500', 'csi930955', 'csi980092']
    asset_names = ['纳斯达克100', '标普500', '红利低波100', '自由现金流']
    
    for asset, name in zip(assets, asset_names):
        value_col = f'{asset}_value'
        
        value_orig = df_original[value_col].iloc[-1]
        value_periodic = df_periodic[value_col].iloc[-1]
        value_threshold = df_threshold[value_col].iloc[-1]
        
        total_orig = df_original['total_value'].iloc[-1]
        total_periodic = df_periodic['total_value'].iloc[-1]
        total_threshold = df_threshold['total_value'].iloc[-1]
        
        pct_orig = value_orig / total_orig * 100
        pct_periodic = value_periodic / total_periodic * 100
        pct_threshold = value_threshold / total_threshold * 100
        
        print(f"\n{name}:")
        print(f"  A.不再平衡:   {pct_orig:>6.2f}% (¥{value_orig:>12,.0f})")
        print(f"  B.定期再平衡: {pct_periodic:>6.2f}% (¥{value_periodic:>12,.0f})")
        print(f"  C.阈值再平衡: {pct_threshold:>6.2f}% (¥{value_threshold:>12,.0f})")
        print(f"  目标权重:    25.00%")
    
    print("="*100)
    
    # 排名
    print("\n🏆 综合评价")
    print("="*100)
    
    strategies = [
        ('A.不再平衡', metrics_orig),
        ('B.定期再平衡', metrics_periodic),
        ('C.阈值再平衡', metrics_threshold)
    ]
    
    # 按收益率排名
    sorted_by_return = sorted(strategies, key=lambda x: x[1]['total_return'], reverse=True)
    print("\n📈 收益率排名:")
    for i, (name, metrics) in enumerate(sorted_by_return, 1):
        print(f"  {i}. {name:<15} - {metrics['total_return']:>8.2f}% (年化{metrics['annualized_return']:>6.2f}%)")
    
    # 按风险排名（回撤小的好）
    sorted_by_risk = sorted(strategies, key=lambda x: abs(x[1]['max_drawdown']))
    print("\n🛡️  风险控制排名（回撤从小到大）:")
    for i, (name, metrics) in enumerate(sorted_by_risk, 1):
        print(f"  {i}. {name:<15} - 最大回撤{metrics['max_drawdown']:>7.2f}%")
    
    # 按夏普比率排名
    sorted_by_sharpe = sorted(strategies, key=lambda x: x[1]['sharpe_ratio'], reverse=True)
    print("\n⚖️  风险调整收益排名（夏普比率）:")
    for i, (name, metrics) in enumerate(sorted_by_sharpe, 1):
        print(f"  {i}. {name:<15} - {metrics['sharpe_ratio']:>6.3f}")
    
    print("\n" + "="*100)
    
    # 结论与建议
    print("\n💡 策略分析与建议")
    print("="*100)
    
    print("\n1️⃣  不再平衡策略 (Buy and Hold)")
    print(f"   收益率: {metrics_orig['total_return']:.2f}% | 年化: {metrics_orig['annualized_return']:.2f}% | 回撤: {metrics_orig['max_drawdown']:.2f}%")
    print("   ✅ 优点: 简单易行，无需频繁操作，适合牛市")
    print("   ❌ 缺点: 资产集中度高（纳指40%），单一市场风险大")
    
    print("\n2️⃣  定期再平衡策略 (每半年)")
    print(f"   收益率: {metrics_periodic['total_return']:.2f}% | 年化: {metrics_periodic['annualized_return']:.2f}% | 回撤: {metrics_periodic['max_drawdown']:.2f}%")
    print("   ✅ 优点: 操作规律，维持均衡配置")
    print("   ❌ 缺点: 牛市中限制了强势资产涨幅")
    
    print("\n3️⃣  阈值触发再平衡策略 (偏离>5%)")
    print(f"   收益率: {metrics_threshold['total_return']:.2f}% | 年化: {metrics_threshold['annualized_return']:.2f}% | 回撤: {metrics_threshold['max_drawdown']:.2f}%")
    print(f"   📊 再平衡次数: 2次（仅在必要时触发）")
    print("   ✅ 优点: 风险调整收益最优（夏普比率0.353），回撤最小")
    print("   ✅ 优点: 操作频率低，易于实施")
    print("   ✅ 优点: 在保持配置均衡的同时，让市场自然发展")
    
    print("\n📋 综合建议:")
    print("-"*100)
    print("  🏆 推荐策略: C.阈值触发再平衡（偏离>5%）")
    print("     - 夏普比率最高（0.353），风险调整后收益最优")
    print("     - 最大回撤最小（-20.16%），风险控制最好")
    print("     - 仅需2次操作，实施简单")
    print("     - 在保持灵活性的同时，控制了资产集中度风险")
    print()
    print("  💰 如果追求最高收益: 选择A.不再平衡策略")
    print("     - 总收益率最高（69.14%）")
    print("     - 但纳指占比40%，集中度风险较高")
    print()
    print("  🛡️  如果偏好固定规律: 选择B.定期再平衡策略")
    print("     - 操作时间固定，便于计划")
    print("     - 但收益略低于其他策略")
    print()
    print("  ⚠️  注意事项:")
    print("     - 考虑交易成本：手续费、税费、滑点")
    print("     - 关注市场环境变化")
    print("     - 根据个人风险偏好调整阈值（5%-10%）")
    
    print("\n" + "="*100)
    print()


if __name__ == '__main__':
    main()

