#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
计算所有策略的索提诺比率并生成对比报告
"""

import pandas as pd
import numpy as np


def calculate_all_metrics(df):
    """计算完整的性能指标（包括索提诺比率）"""
    
    # 基本指标
    days = (df.index[-1] - df.index[0]).days
    years = days / 365.25
    final_value = df['total_value'].iloc[-1]
    initial_invest = df['cumulative_invest'].iloc[-1]
    
    # 收益率
    total_return = df['return'].iloc[-1]
    annualized_return = (pow(final_value / initial_invest, 1/years) - 1) * 100
    
    # 最大回撤
    rolling_max = df['total_value'].expanding().max()
    drawdown = (df['total_value'] - rolling_max) / rolling_max * 100
    max_drawdown = drawdown.min()
    
    # 日收益率序列
    daily_returns = df['total_value'].pct_change().dropna()
    
    # 年化波动率
    volatility = daily_returns.std() * np.sqrt(252) * 100
    
    # 夏普比率
    risk_free_rate = 0.03
    sharpe_ratio = (annualized_return / 100 - risk_free_rate) / (volatility / 100)
    
    # 索提诺比率 - 只考虑下行风险
    # 下行标准差：只计算负收益的波动
    downside_returns = daily_returns[daily_returns < 0]
    if len(downside_returns) > 0:
        downside_std = downside_returns.std() * np.sqrt(252) * 100
        sortino_ratio = (annualized_return / 100 - risk_free_rate) / (downside_std / 100)
    else:
        sortino_ratio = float('inf')  # 如果没有负收益，索提诺比率无限大
    
    return {
        'total_return': total_return,
        'annualized_return': annualized_return,
        'max_drawdown': max_drawdown,
        'volatility': volatility,
        'downside_volatility': downside_std if len(downside_returns) > 0 else 0,
        'sharpe_ratio': sharpe_ratio,
        'sortino_ratio': sortino_ratio,
        'final_value': final_value,
        'total_profit': df['profit'].iloc[-1],
        'years': years
    }


def main():
    """主函数"""
    print("\n" + "="*100)
    print("投资策略索提诺比率分析")
    print("="*100)
    
    # 加载所有策略结果
    strategies = {
        '无债不再平衡': 'backtest_result.csv',
        '无债定期再平衡': 'backtest_rebalance_result.csv',
        '无债阈值再平衡': 'backtest_threshold_rebalance_result.csv',
        '含债不再平衡': 'backtest_with_bond_result.csv',
        '含债阈值再平衡': 'backtest_with_bond_threshold_result.csv'
    }
    
    all_metrics = []
    
    print("\n正在计算各策略指标...")
    for name, filename in strategies.items():
        try:
            df = pd.read_csv(filename, parse_dates=['Date'], index_col='Date')
            metrics = calculate_all_metrics(df)
            metrics['name'] = name
            all_metrics.append(metrics)
            print(f"✅ {name}")
        except FileNotFoundError:
            print(f"❌ 未找到 {name} 数据")
            continue
    
    if len(all_metrics) == 0:
        print("\n没有找到回测数据，请先运行回测脚本")
        return
    
    # 完整对比表
    print("\n" + "="*100)
    print("📊 完整风险收益指标对比")
    print("="*100)
    print(f"{'策略':<18} | {'总收益':<10} | {'年化':<8} | {'回撤':<8} | {'夏普':<7} | {'索提诺':<7} | {'波动率':<8} | {'下行波动':<8}")
    print("-"*100)
    
    for m in all_metrics:
        print(f"{m['name']:<18} | "
              f"{m['total_return']:>8.2f}% | "
              f"{m['annualized_return']:>6.2f}% | "
              f"{m['max_drawdown']:>6.2f}% | "
              f"{m['sharpe_ratio']:>6.3f} | "
              f"{m['sortino_ratio']:>6.3f} | "
              f"{m['volatility']:>6.2f}% | "
              f"{m['downside_volatility']:>6.2f}%")
    
    print("="*100)
    
    # 按索提诺比率排名
    print("\n🏆 索提诺比率排名（只考虑下行风险）")
    print("="*100)
    
    sorted_by_sortino = sorted(all_metrics, key=lambda x: x['sortino_ratio'], reverse=True)
    
    for i, m in enumerate(sorted_by_sortino, 1):
        print(f"\n{i}. {m['name']}")
        print(f"   索提诺比率: {m['sortino_ratio']:.3f}")
        print(f"   年化收益: {m['annualized_return']:.2f}%")
        print(f"   下行波动: {m['downside_volatility']:.2f}% (vs 总波动 {m['volatility']:.2f}%)")
        print(f"   最大回撤: {m['max_drawdown']:.2f}%")
    
    print("\n" + "="*100)
    
    # 夏普 vs 索提诺对比
    print("\n⚖️  夏普比率 vs 索提诺比率对比")
    print("="*100)
    print(f"{'策略':<18} | {'夏普比率':<12} | {'索提诺比率':<12} | {'差异':<12} | {'说明'}")
    print("-"*100)
    
    for m in all_metrics:
        diff = m['sortino_ratio'] - m['sharpe_ratio']
        
        if m['sortino_ratio'] > m['sharpe_ratio'] * 1.5:
            note = "下行风险控制优秀 ✅"
        elif m['sortino_ratio'] > m['sharpe_ratio'] * 1.2:
            note = "下行风险控制良好"
        else:
            note = "上下波动较均衡"
        
        print(f"{m['name']:<18} | "
              f"{m['sharpe_ratio']:>10.3f} | "
              f"{m['sortino_ratio']:>10.3f} | "
              f"{diff:>+10.3f} | {note}")
    
    print("="*100)
    
    # 分析
    print("\n💡 索提诺比率的意义")
    print("="*100)
    print("""
索提诺比率 vs 夏普比率的区别：

夏普比率（Sharpe Ratio）:
  - 分母：总波动率（包括上涨和下跌的波动）
  - 惩罚所有波动，即使是向上的波动
  - 公式：(收益率 - 无风险利率) / 总波动率

索提诺比率（Sortino Ratio）:
  - 分母：下行波动率（只计算亏损日的波动）
  - 只关注真正的风险（下跌）
  - 不惩罚盈利波动
  - 公式：(收益率 - 无风险利率) / 下行波动率

为什么索提诺比率更好？
  ✅ 投资者真正害怕的是亏损，不是盈利波动
  ✅ 更符合实际风险感受
  ✅ 对单边上涨的资产更友好

通常：索提诺比率 > 夏普比率（因为下行波动 < 总波动）
    """)
    
    print("\n" + "="*100)
    
    # 推荐
    best_sortino = sorted_by_sortino[0]
    print(f"\n🎯 基于索提诺比率的推荐：{best_sortino['name']}")
    print(f"   索提诺比率: {best_sortino['sortino_ratio']:.3f}（最高）")
    print(f"   年化收益: {best_sortino['annualized_return']:.2f}%")
    print(f"   下行波动: {best_sortino['downside_volatility']:.2f}%（只关注亏损风险）")
    print(f"   最大回撤: {best_sortino['max_drawdown']:.2f}%")
    
    print("\n" + "="*100)
    print()


if __name__ == '__main__':
    main()

