#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成HTML格式的投资回测分析报告
"""

import pandas as pd
import numpy as np
import json
from datetime import datetime


def load_all_results():
    """加载所有策略的回测结果"""
    strategies = {
        '无债不再平衡': 'backtest_result.csv',
        '无债定期再平衡': 'backtest_rebalance_result.csv',
        '无债阈值再平衡': 'backtest_threshold_rebalance_result.csv',
        '含债不再平衡': 'backtest_with_bond_result.csv',
        '含债阈值再平衡': 'backtest_with_bond_threshold_result.csv'
    }
    
    results = {}
    for name, filename in strategies.items():
        try:
            df = pd.read_csv(filename, parse_dates=['Date'], index_col='Date')
            results[name] = df
            print(f"✅ 加载 {name}: {len(df)} 条数据")
        except FileNotFoundError:
            print(f"❌ 未找到 {name} 数据文件")
    
    return results


def calculate_metrics(df, strategy_name):
    """计算策略指标（含索提诺比率）"""
    
    days = (df.index[-1] - df.index[0]).days
    years = days / 365.25
    final_value = df['total_value'].iloc[-1]
    initial_invest = df['cumulative_invest'].iloc[-1]
    
    annualized_return = (pow(final_value / initial_invest, 1/years) - 1) * 100
    
    rolling_max = df['total_value'].expanding().max()
    drawdown = (df['total_value'] - rolling_max) / rolling_max * 100
    max_drawdown = drawdown.min()
    
    daily_returns = df['total_value'].pct_change().dropna()
    volatility = daily_returns.std() * np.sqrt(252) * 100
    sharpe_ratio = (annualized_return / 100 - 0.03) / (volatility / 100)
    
    # 索提诺比率 - 只考虑下行风险
    downside_returns = daily_returns[daily_returns < 0]
    if len(downside_returns) > 0:
        downside_std = downside_returns.std() * np.sqrt(252) * 100
        sortino_ratio = (annualized_return / 100 - 0.03) / (downside_std / 100)
    else:
        sortino_ratio = float('inf')
    
    return {
        'name': strategy_name,
        'total_return': df['return'].iloc[-1],
        'annualized_return': annualized_return,
        'max_drawdown': max_drawdown,
        'volatility': volatility,
        'sharpe_ratio': sharpe_ratio,
        'sortino_ratio': sortino_ratio,
        'downside_volatility': downside_std if len(downside_returns) > 0 else 0,
        'final_value': final_value,
        'total_profit': df['profit'].iloc[-1],
        'years': years
    }


def get_asset_performance(df, strategy_name):
    """获取各资产表现"""
    
    # 识别资产列
    value_columns = [col for col in df.columns if col.endswith('_value')]
    
    assets = []
    final_total = df['total_value'].iloc[-1]
    
    for col in value_columns:
        asset_name = col.replace('_value', '')
        final_value = df[col].iloc[-1]
        initial_value = df[col].iloc[0]
        
        # 计算该资产贡献的利润
        profit = final_value - initial_value
        weight = final_value / final_total * 100
        
        assets.append({
            'name': asset_name,
            'final_value': final_value,
            'profit': profit,
            'weight': weight
        })
    
    return assets


def generate_html(results):
    """生成HTML报告"""
    
    # 计算所有策略的指标
    all_metrics = []
    for name, df in results.items():
        metrics = calculate_metrics(df, name)
        all_metrics.append(metrics)
    
    # 准备净值曲线数据
    chart_data = {}
    for name, df in results.items():
        chart_data[name] = {
            'dates': df.index.strftime('%Y-%m-%d').tolist(),
            'values': df['total_value'].tolist(),
            'returns': df['return'].tolist()
        }
    
    # 准备资产利润数据
    asset_data = {}
    for name, df in results.items():
        asset_data[name] = get_asset_performance(df, name)
    
    # 生成HTML
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ETF投资组合回测分析报告</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            color: #333;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .header p {{
            font-size: 1.2em;
            opacity: 0.9;
        }}
        
        .nav {{
            background: #f8f9fa;
            padding: 20px 40px;
            display: flex;
            gap: 20px;
            border-bottom: 1px solid #dee2e6;
            overflow-x: auto;
        }}
        
        .nav-btn {{
            padding: 12px 24px;
            background: white;
            border: 2px solid #667eea;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            transition: all 0.3s;
            white-space: nowrap;
        }}
        
        .nav-btn:hover {{
            background: #667eea;
            color: white;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }}
        
        .nav-btn.active {{
            background: #667eea;
            color: white;
        }}
        
        .content {{
            padding: 40px;
        }}
        
        .section {{
            display: none;
        }}
        
        .section.active {{
            display: block;
        }}
        
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        
        .metric-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 25px;
            border-radius: 12px;
            color: white;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }}
        
        .metric-card h3 {{
            font-size: 14px;
            opacity: 0.9;
            margin-bottom: 10px;
        }}
        
        .metric-card .value {{
            font-size: 32px;
            font-weight: bold;
        }}
        
        .metric-card .sub {{
            font-size: 14px;
            opacity: 0.8;
            margin-top: 5px;
        }}
        
        .comparison-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 30px 0;
            background: white;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }}
        
        .comparison-table th {{
            background: #667eea;
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: 600;
        }}
        
        .comparison-table td {{
            padding: 12px 15px;
            border-bottom: 1px solid #f0f0f0;
        }}
        
        .comparison-table tr:hover {{
            background: #f8f9fa;
        }}
        
        .best {{
            color: #28a745;
            font-weight: bold;
        }}
        
        .chart-container {{
            position: relative;
            height: 400px;
            margin: 30px 0;
            background: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }}
        
        .asset-bars {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}
        
        .asset-bar {{
            background: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }}
        
        .asset-bar h4 {{
            margin-bottom: 15px;
            color: #667eea;
        }}
        
        .bar-fill {{
            height: 30px;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            border-radius: 6px;
            position: relative;
            margin: 10px 0;
        }}
        
        .bar-label {{
            position: absolute;
            right: 10px;
            line-height: 30px;
            color: white;
            font-weight: bold;
        }}
        
        .strategy-header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 12px;
            margin-bottom: 30px;
        }}
        
        .strategy-header h2 {{
            font-size: 2em;
            margin-bottom: 10px;
        }}
        
        .badge {{
            display: inline-block;
            padding: 6px 12px;
            background: rgba(255,255,255,0.2);
            border-radius: 20px;
            font-size: 14px;
            margin-right: 10px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 ETF投资组合回测分析报告</h1>
            <p>2015年1月 - 2025年10月 | 初始资金100万 | 定投2年</p>
            <p style="margin-top: 10px; font-size: 0.9em;">生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="nav">
            <button class="nav-btn active" onclick="showSection('overview')">📊 总览对比</button>
            <button class="nav-btn" onclick="showSection('strategy1')">策略1: 无债不再平衡</button>
            <button class="nav-btn" onclick="showSection('strategy2')">策略2: 无债阈值再平衡</button>
            <button class="nav-btn" onclick="showSection('strategy3')">策略3: 含债不再平衡</button>
            <button class="nav-btn" onclick="showSection('strategy4')">策略4: 含债阈值再平衡 ⭐</button>
        </div>
        
        <div class="content">
            <!-- 总览对比 -->
            <div id="overview" class="section active">
                <h2 style="margin-bottom: 30px; color: #667eea;">📈 所有策略总览对比</h2>
                
                <table class="comparison-table">
                    <thead>
                        <tr>
                            <th>策略</th>
                            <th>总收益率</th>
                            <th>年化收益率</th>
                            <th>最大回撤</th>
                            <th>夏普比率</th>
                            <th>索提诺比率</th>
                            <th>下行波动</th>
                            <th>操作次数</th>
                        </tr>
                    </thead>
                    <tbody>
"""
    
    # 添加策略对比表格
    strategy_info = {
        '无债不再平衡': {'rebalance': 0},
        '无债定期再平衡': {'rebalance': 17},
        '无债阈值再平衡': {'rebalance': 5},
        '含债不再平衡': {'rebalance': 0},
        '含债阈值再平衡': {'rebalance': 8}
    }
    
    # 找出最优索提诺比率
    best_sortino = max([m['sortino_ratio'] for m in all_metrics])
    
    for metrics in all_metrics:
        name = metrics['name']
        rebalance_count = strategy_info.get(name, {}).get('rebalance', 0)
        
        # 标记最优值
        sortino_class = 'best' if metrics['sortino_ratio'] == best_sortino else ''
        
        html += f"""
                        <tr>
                            <td><strong>{name}</strong></td>
                            <td>{metrics['total_return']:.2f}%</td>
                            <td>{metrics['annualized_return']:.2f}%</td>
                            <td>{metrics['max_drawdown']:.2f}%</td>
                            <td>{metrics['sharpe_ratio']:.3f}</td>
                            <td class="{sortino_class}">{metrics['sortino_ratio']:.3f}</td>
                            <td>{metrics['downside_volatility']:.2f}%</td>
                            <td>{rebalance_count}次</td>
                        </tr>
"""
    
    html += """
                    </tbody>
                </table>
                
                <div style="background: #f8f9fa; padding: 20px; border-radius: 12px; margin: 30px 0;">
                    <h3 style="color: #667eea; margin-bottom: 15px;">💡 什么是索提诺比率？</h3>
                    <p style="line-height: 1.8; color: #666;">
                        <strong>索提诺比率（Sortino Ratio）</strong>是改进版的夏普比率，只考虑<strong>下行风险</strong>（亏损的波动），
                        而不惩罚上涨的波动。这更符合投资者的真实感受，因为我们真正害怕的是亏损，而不是盈利波动。
                    </p>
                    <p style="line-height: 1.8; color: #666; margin-top: 10px;">
                        <strong>公式</strong>: (年化收益率 - 3%) / 下行波动率<br>
                        <strong>意义</strong>: 每承担1单位<strong>亏损风险</strong>，能获得多少超额收益<br>
                        <strong>数值越高越好</strong>: 说明用较小的亏损风险获得了较高收益
                    </p>
                </div>
                
                <h3 style="margin: 40px 0 20px 0; color: #667eea;">净值走势对比</h3>
                <div class="chart-container">
                    <canvas id="overviewChart"></canvas>
                </div>
                
                <h3 style="margin: 40px 0 20px 0; color: #667eea;">收益率对比</h3>
                <div class="chart-container">
                    <canvas id="returnChart"></canvas>
                </div>
            </div>
"""
    
    # 为每个策略生成详细页面
    for strategy_name, df in results.items():
        section_id = strategy_name.replace(' ', '_')
        metrics = calculate_metrics(df, strategy_name)
        assets = get_asset_performance(df, strategy_name)
        
        html += f"""
            <!-- {strategy_name} -->
            <div id="{section_id}" class="section">
                <div class="strategy-header">
                    <h2>{strategy_name}</h2>
                    <div style="margin-top: 15px;">
                        <span class="badge">投资{metrics['years']:.2f}年</span>
                        <span class="badge">年化{metrics['annualized_return']:.2f}%</span>
                        <span class="badge">夏普{metrics['sharpe_ratio']:.3f}</span>
                    </div>
                </div>
                
                <div class="metrics-grid">
                    <div class="metric-card">
                        <h3>总收益率</h3>
                        <div class="value">{metrics['total_return']:.2f}%</div>
                        <div class="sub">年化 {metrics['annualized_return']:.2f}%</div>
                    </div>
                    <div class="metric-card">
                        <h3>最终市值</h3>
                        <div class="value">¥{metrics['final_value']/10000:.1f}万</div>
                        <div class="sub">收益 ¥{metrics['total_profit']/10000:.1f}万</div>
                    </div>
                    <div class="metric-card">
                        <h3>最大回撤</h3>
                        <div class="value">{metrics['max_drawdown']:.2f}%</div>
                        <div class="sub">波动率 {metrics['volatility']:.2f}%</div>
                    </div>
                    <div class="metric-card">
                        <h3>夏普比率</h3>
                        <div class="value">{metrics['sharpe_ratio']:.3f}</div>
                        <div class="sub">综合风险调整收益</div>
                    </div>
                    <div class="metric-card">
                        <h3>索提诺比率</h3>
                        <div class="value">{metrics['sortino_ratio']:.3f}</div>
                        <div class="sub">下行风险调整收益</div>
                    </div>
                    <div class="metric-card">
                        <h3>下行波动率</h3>
                        <div class="value">{metrics['downside_volatility']:.2f}%</div>
                        <div class="sub">只计算亏损风险</div>
                    </div>
                </div>
                
                <h3 style="margin: 30px 0 20px 0; color: #667eea;">净值走势</h3>
                <div class="chart-container">
                    <canvas id="chart_{section_id}"></canvas>
                </div>
                
                <h3 style="margin: 30px 0 20px 0; color: #667eea;">各资产利润贡献</h3>
                <div class="asset-bars">
"""
        
        # 为每个资产添加利润条形图
        max_profit = max([a['profit'] for a in assets])
        asset_names_map = {
            'nasdaq100': '纳斯达克100',
            'sp500': '标普500',
            'csi930955': '红利低波100',
            'csi980092': '自由现金流',
            'cnb00003': '证金债'
        }
        
        for asset in sorted(assets, key=lambda x: x['profit'], reverse=True):
            profit_pct = (asset['profit'] / max_profit * 100)
            display_name = asset_names_map.get(asset['name'], asset['name'])
            
            html += f"""
                    <div class="asset-bar">
                        <h4>{display_name}</h4>
                        <div style="margin: 10px 0;">
                            <div>利润: ¥{asset['profit']/10000:.1f}万</div>
                            <div style="font-size: 14px; color: #666;">占比: {asset['weight']:.2f}%</div>
                        </div>
                        <div class="bar-fill" style="width: {profit_pct}%">
                            <span class="bar-label">{profit_pct:.0f}%</span>
                        </div>
                    </div>
"""
        
        html += """
                </div>
            </div>
"""
    
    # 添加JavaScript
    html += """
        </div>
    </div>
    
    <script>
        // 数据
        const chartData = """ + json.dumps(chart_data, ensure_ascii=False) + """;
        const assetData = """ + json.dumps(asset_data, ensure_ascii=False) + """;
        
        // 切换页面
        function showSection(sectionId) {
            // 隐藏所有section
            document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
            document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
            
            // 显示目标section
            if (sectionId === 'overview') {
                document.getElementById('overview').classList.add('active');
                document.querySelectorAll('.nav-btn')[0].classList.add('active');
            } else if (sectionId === 'strategy1') {
                document.getElementById('无债不再平衡').classList.add('active');
                document.querySelectorAll('.nav-btn')[1].classList.add('active');
            } else if (sectionId === 'strategy2') {
                document.getElementById('无债阈值再平衡').classList.add('active');
                document.querySelectorAll('.nav-btn')[2].classList.add('active');
            } else if (sectionId === 'strategy3') {
                document.getElementById('含债不再平衡').classList.add('active');
                document.querySelectorAll('.nav-btn')[3].classList.add('active');
            } else if (sectionId === 'strategy4') {
                document.getElementById('含债阈值再平衡').classList.add('active');
                document.querySelectorAll('.nav-btn')[4].classList.add('active');
            }
        }
        
        // 颜色配置
        const colors = [
            'rgba(102, 126, 234, 1)',
            'rgba(118, 75, 162, 1)',
            'rgba(237, 100, 166, 1)',
            'rgba(255, 154, 158, 1)',
            'rgba(250, 208, 196, 1)'
        ];
        
        // 总览净值图
        new Chart(document.getElementById('overviewChart'), {
            type: 'line',
            data: {
                labels: chartData['无债不再平衡'].dates,
                datasets: Object.keys(chartData).map((name, idx) => ({
                    label: name,
                    data: chartData[name].values,
                    borderColor: colors[idx],
                    backgroundColor: colors[idx].replace('1)', '0.1)'),
                    borderWidth: 2,
                    tension: 0.4,
                    fill: false
                }))
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: '投资组合净值走势',
                        font: { size: 16 }
                    },
                    legend: {
                        position: 'top'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return '¥' + (value/10000).toFixed(0) + '万';
                            }
                        }
                    }
                }
            }
        });
        
        // 收益率对比图
        new Chart(document.getElementById('returnChart'), {
            type: 'line',
            data: {
                labels: chartData['无债不再平衡'].dates,
                datasets: Object.keys(chartData).map((name, idx) => ({
                    label: name,
                    data: chartData[name].returns,
                    borderColor: colors[idx],
                    backgroundColor: colors[idx].replace('1)', '0.1)'),
                    borderWidth: 2,
                    tension: 0.4,
                    fill: false
                }))
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: '累计收益率走势',
                        font: { size: 16 }
                    },
                    legend: {
                        position: 'top'
                    }
                },
                scales: {
                    y: {
                        ticks: {
                            callback: function(value) {
                                return value.toFixed(0) + '%';
                            }
                        }
                    }
                }
            }
        });
        
        // 为每个策略创建图表
        Object.keys(chartData).forEach((strategyName) => {
            const sectionId = strategyName.replace(' ', '_');
            const canvasId = 'chart_' + sectionId;
            const canvas = document.getElementById(canvasId);
            
            if (canvas) {
                new Chart(canvas, {
                    type: 'line',
                    data: {
                        labels: chartData[strategyName].dates,
                        datasets: [{
                            label: '投资组合净值',
                            data: chartData[strategyName].values,
                            borderColor: 'rgba(102, 126, 234, 1)',
                            backgroundColor: 'rgba(102, 126, 234, 0.1)',
                            borderWidth: 3,
                            tension: 0.4,
                            fill: true
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: {
                                display: false
                            }
                        },
                        scales: {
                            y: {
                                beginAtZero: true,
                                ticks: {
                                    callback: function(value) {
                                        return '¥' + (value/10000).toFixed(0) + '万';
                                    }
                                }
                            }
                        }
                    }
                });
            }
        });
    </script>
</body>
</html>
"""
    
    return html


def main():
    """主函数"""
    print("="*60)
    print("生成HTML分析报告")
    print("="*60 + "\n")
    
    # 加载所有结果
    results = load_all_results()
    
    if len(results) == 0:
        print("\n❌ 没有找到回测结果文件")
        print("请先运行回测脚本生成数据")
        return
    
    print(f"\n正在生成HTML报告...")
    
    # 生成HTML
    html = generate_html(results)
    
    # 保存文件
    output_file = 'investment_report.html'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"\n✅ HTML报告已生成: {output_file}")
    print(f"   请在浏览器中打开此文件查看")
    print("\n" + "="*60)


if __name__ == '__main__':
    main()

