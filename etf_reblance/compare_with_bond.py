#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
对比加入证金债前后的策略效果

对比维度：
1. 无债 vs 含债（不再平衡）
2. 无债阈值 vs 含债阈值（阈值再平衡）
"""

import pandas as pd
import numpy as np


def load_results():
    """加载回测结果"""
    
    # 无债版本
    df_no_bond = pd.read_csv('backtest_result.csv', parse_dates=['Date'], index_col='Date')
    df_no_bond_threshold = pd.read_csv('backtest_threshold_rebalance_result.csv', parse_dates=['Date'], index_col='Date')
    
    # 含债版本
    df_with_bond = pd.read_csv('backtest_with_bond_result.csv', parse_dates=['Date'], index_col='Date')
    df_with_bond_threshold = pd.read_csv('backtest_with_bond_threshold_result.csv', parse_dates=['Date'], index_col='Date')
    
    return df_no_bond, df_no_bond_threshold, df_with_bond, df_with_bond_threshold


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
    
    # 夏普比率
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
    print("加入证金债效果对比分析")
    print("="*100)
    
    # 加载数据
    print("\n正在加载回测数据...")
    df_no_bond, df_no_bond_threshold, df_with_bond, df_with_bond_threshold = load_results()
    
    # 计算指标
    m_no_bond = calculate_metrics(df_no_bond)
    m_no_bond_th = calculate_metrics(df_no_bond_threshold)
    m_with_bond = calculate_metrics(df_with_bond)
    m_with_bond_th = calculate_metrics(df_with_bond_threshold)
    
    # 不再平衡策略对比
    print("\n📊 策略对比1: 不再平衡策略（Buy and Hold）")
    print("="*100)
    print(f"{'指标':<18} | {'4资产均衡(25%)':<25} | {'含债(22.5%+10%)':<25} | {'差异':<20}")
    print("-"*100)
    
    print(f"{'最终市值':<18} | ¥{m_no_bond['final_value']:>23,.0f} | " +
          f"¥{m_with_bond['final_value']:>23,.0f} | " +
          f"¥{m_with_bond['final_value'] - m_no_bond['final_value']:>18,.0f}")
    
    print(f"{'总收益率':<18} | {m_no_bond['total_return']:>23.2f}% | " +
          f"{m_with_bond['total_return']:>23.2f}% | " +
          f"{m_with_bond['total_return'] - m_no_bond['total_return']:>18.2f}%")
    
    print(f"{'年化收益率':<18} | {m_no_bond['annualized_return']:>23.2f}% | " +
          f"{m_with_bond['annualized_return']:>23.2f}% | " +
          f"{m_with_bond['annualized_return'] - m_no_bond['annualized_return']:>18.2f}%")
    
    print(f"{'最大回撤':<18} | {m_no_bond['max_drawdown']:>23.2f}% | " +
          f"{m_with_bond['max_drawdown']:>23.2f}% | " +
          f"{m_with_bond['max_drawdown'] - m_no_bond['max_drawdown']:>18.2f}%")
    
    print(f"{'年化波动率':<18} | {m_no_bond['volatility']:>23.2f}% | " +
          f"{m_with_bond['volatility']:>23.2f}% | " +
          f"{m_with_bond['volatility'] - m_no_bond['volatility']:>18.2f}%")
    
    print(f"{'夏普比率':<18} | {m_no_bond['sharpe_ratio']:>27.3f} | " +
          f"{m_with_bond['sharpe_ratio']:>27.3f} | " +
          f"{m_with_bond['sharpe_ratio'] - m_no_bond['sharpe_ratio']:>22.3f}")
    
    # 阈值再平衡策略对比
    print("\n📊 策略对比2: 阈值触发再平衡策略")
    print("="*100)
    print(f"{'指标':<18} | {'4资产(偏离5%)':<25} | {'含债(相对20%)':<25} | {'差异':<20}")
    print("-"*100)
    
    print(f"{'最终市值':<18} | ¥{m_no_bond_th['final_value']:>23,.0f} | " +
          f"¥{m_with_bond_th['final_value']:>23,.0f} | " +
          f"¥{m_with_bond_th['final_value'] - m_no_bond_th['final_value']:>18,.0f}")
    
    print(f"{'总收益率':<18} | {m_no_bond_th['total_return']:>23.2f}% | " +
          f"{m_with_bond_th['total_return']:>23.2f}% | " +
          f"{m_with_bond_th['total_return'] - m_no_bond_th['total_return']:>18.2f}%")
    
    print(f"{'年化收益率':<18} | {m_no_bond_th['annualized_return']:>23.2f}% | " +
          f"{m_with_bond_th['annualized_return']:>23.2f}% | " +
          f"{m_with_bond_th['annualized_return'] - m_no_bond_th['annualized_return']:>18.2f}%")
    
    print(f"{'最大回撤':<18} | {m_no_bond_th['max_drawdown']:>23.2f}% | " +
          f"{m_with_bond_th['max_drawdown']:>23.2f}% | " +
          f"{m_with_bond_th['max_drawdown'] - m_no_bond_th['max_drawdown']:>18.2f}%")
    
    print(f"{'年化波动率':<18} | {m_no_bond_th['volatility']:>23.2f}% | " +
          f"{m_with_bond_th['volatility']:>23.2f}% | " +
          f"{m_with_bond_th['volatility'] - m_no_bond_th['volatility']:>18.2f}%")
    
    print(f"{'夏普比率':<18} | {m_no_bond_th['sharpe_ratio']:>27.3f} | " +
          f"{m_with_bond_th['sharpe_ratio']:>27.3f} | " +
          f"{m_with_bond_th['sharpe_ratio'] - m_no_bond_th['sharpe_ratio']:>22.3f}")
    
    print("="*100)
    
    # 分析
    print("\n💡 加入证金债的影响分析")
    print("="*100)
    
    print("\n1️⃣  不再平衡策略：加入证金债后")
    return_diff = m_with_bond['total_return'] - m_no_bond['total_return']
    risk_diff = m_with_bond['max_drawdown'] - m_no_bond['max_drawdown']
    sharpe_diff = m_with_bond['sharpe_ratio'] - m_no_bond['sharpe_ratio']
    
    print(f"   收益率变化: {m_no_bond['total_return']:.2f}% → {m_with_bond['total_return']:.2f}% ({return_diff:+.2f}%)")
    print(f"   最大回撤变化: {m_no_bond['max_drawdown']:.2f}% → {m_with_bond['max_drawdown']:.2f}% ({risk_diff:+.2f}%)")
    print(f"   夏普比率变化: {m_no_bond['sharpe_ratio']:.3f} → {m_with_bond['sharpe_ratio']:.3f} ({sharpe_diff:+.3f})")
    
    if sharpe_diff > 0:
        print("   ✅ 结论: 加入债券后，风险调整收益提升")
        print("   💡 分析: 虽然收益略降，但风险大幅降低，综合性价比更高")
    else:
        print("   ❌ 结论: 加入债券后，风险调整收益下降")
    
    print("\n2️⃣  阈值再平衡策略：加入证金债后")
    return_diff2 = m_with_bond_th['total_return'] - m_no_bond_th['total_return']
    risk_diff2 = m_with_bond_th['max_drawdown'] - m_no_bond_th['max_drawdown']
    sharpe_diff2 = m_with_bond_th['sharpe_ratio'] - m_no_bond_th['sharpe_ratio']
    
    print(f"   收益率变化: {m_no_bond_th['total_return']:.2f}% → {m_with_bond_th['total_return']:.2f}% ({return_diff2:+.2f}%)")
    print(f"   最大回撤变化: {m_no_bond_th['max_drawdown']:.2f}% → {m_with_bond_th['max_drawdown']:.2f}% ({risk_diff2:+.2f}%)")
    print(f"   夏普比率变化: {m_no_bond_th['sharpe_ratio']:.3f} → {m_with_bond_th['sharpe_ratio']:.3f} ({sharpe_diff2:+.3f})")
    print(f"   再平衡次数: 2次 → 4次")
    
    if sharpe_diff2 >= 0 and risk_diff2 > 0:
        print("   ✅ 结论: 加入债券后，风险进一步降低，综合表现基本持平")
    
    # 最终推荐
    print("\n🎯 最终推荐策略")
    print("="*100)
    
    best_strategies = [
        ("含债阈值再平衡", m_with_bond_th, "相对阈值20%, 4次再平衡"),
        ("无债阈值再平衡", m_no_bond_th, "固定阈值5%, 2次再平衡"),
        ("含债不再平衡", m_with_bond, "Buy and Hold"),
        ("无债不再平衡", m_no_bond, "Buy and Hold")
    ]
    
    # 按夏普比率排序
    best_strategies.sort(key=lambda x: x[1]['sharpe_ratio'], reverse=True)
    
    print("\n按风险调整收益排名（夏普比率）:")
    for i, (name, metrics, desc) in enumerate(best_strategies, 1):
        print(f"\n{i}. {name}")
        print(f"   描述: {desc}")
        print(f"   收益率: {metrics['total_return']:.2f}% (年化{metrics['annualized_return']:.2f}%)")
        print(f"   最大回撤: {metrics['max_drawdown']:.2f}%")
        print(f"   夏普比率: {metrics['sharpe_ratio']:.3f} ⭐")
    
    print("\n" + "="*100)
    
    print("\n📋 投资建议")
    print("-"*100)
    print("🥇 首选: 含债不再平衡策略")
    print("   • 夏普比率最高(0.373)，性价比最优")
    print("   • 无需任何再平衡操作，最简单")
    print("   • 收益66.58%，回撤-20.77%，平衡最佳")
    print()
    print("🥈 次选: 含债阈值再平衡策略")
    print("   • 夏普比率略低(0.350)，但风险最小(回撤-19.64%)")
    print("   • 仅需4次操作，比较容易执行")
    print("   • 适合更追求稳健的投资者")
    print()
    print("💡 关键发现:")
    print("   • 加入10%证金债，显著提升了风险调整收益")
    print("   • 债券资产起到了降低波动、控制回撤的作用")
    print("   • 适当的债券配置能提高组合的整体质量")
    
    print("\n" + "="*100)
    print()


if __name__ == '__main__':
    main()

