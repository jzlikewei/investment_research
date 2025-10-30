#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
下载标普500和纳斯达克100指数历史数据
使用yfinance API
"""

import yfinance as yf
import pandas as pd
from datetime import datetime
import os

def download_index_data(ticker, name, start_date='2010-01-01', end_date=None):
    """
    下载指数数据
    
    参数:
        ticker: 指数代码 (如 ^GSPC)
        name: 指数名称 (用于保存文件)
        start_date: 开始日期
        end_date: 结束日期 (默认为今天)
    """
    if end_date is None:
        end_date = datetime.now().strftime('%Y-%m-%d')
    
    print(f"\n正在下载 {name} ({ticker}) 数据...")
    print(f"时间范围: {start_date} 至 {end_date}")
    
    try:
        # 下载数据
        data = yf.download(ticker, start=start_date, end=end_date, progress=False)
        
        if data.empty:
            print(f"❌ 错误: {name} 没有获取到数据")
            return None
        
        # 添加一些有用的列
        data['Daily_Return'] = data['Close'].pct_change()
        data['Cumulative_Return'] = (1 + data['Daily_Return']).cumprod()
        
        # 数据统计
        print(f"✅ 成功下载 {len(data)} 条数据")
        print(f"   日期范围: {data.index[0].strftime('%Y-%m-%d')} 至 {data.index[-1].strftime('%Y-%m-%d')}")
        open_min = data['Open'].min().item() if hasattr(data['Open'].min(), 'item') else data['Open'].min()
        open_max = data['Open'].max().item() if hasattr(data['Open'].max(), 'item') else data['Open'].max()
        close_min = data['Close'].min().item() if hasattr(data['Close'].min(), 'item') else data['Close'].min()
        close_max = data['Close'].max().item() if hasattr(data['Close'].max(), 'item') else data['Close'].max()
        print(f"   开盘价范围: {open_min:.2f} - {open_max:.2f}")
        print(f"   收盘价范围: {close_min:.2f} - {close_max:.2f}")
        
        return data
        
    except Exception as e:
        print(f"❌ 下载 {name} 时出错: {str(e)}")
        return None


def save_data(data, filename):
    """保存数据到CSV文件"""
    if data is None:
        return
    
    try:
        # 创建data目录（如果不存在）
        os.makedirs('data', exist_ok=True)
        
        filepath = os.path.join('data', filename)
        data.to_csv(filepath)
        print(f"💾 数据已保存至: {filepath}")
        
    except Exception as e:
        print(f"❌ 保存文件时出错: {str(e)}")


def generate_summary_all(sp500_data, nasdaq100_data, csi930955_data):
    """生成数据摘要报告"""
    print("\n" + "="*60)
    print("数据摘要报告")
    print("="*60)
    
    if sp500_data is not None:
        print("\n📊 标普500 (S&P 500) 统计:")
        print(f"   总交易日: {len(sp500_data)} 天")
        close_first = sp500_data['Close'].iloc[0].item() if hasattr(sp500_data['Close'].iloc[0], 'item') else sp500_data['Close'].iloc[0]
        close_last = sp500_data['Close'].iloc[-1].item() if hasattr(sp500_data['Close'].iloc[-1], 'item') else sp500_data['Close'].iloc[-1]
        print(f"   期间涨幅: {((close_last / close_first - 1) * 100):.2f}%")
        high_max_idx = sp500_data['High'].idxmax()
        low_min_idx = sp500_data['Low'].idxmin()
        # 处理MultiIndex情况
        if isinstance(high_max_idx, pd.Series):
            high_max_idx = high_max_idx.iloc[0]
        if isinstance(low_min_idx, pd.Series):
            low_min_idx = low_min_idx.iloc[0]
        high_max = sp500_data['High'].max().item() if hasattr(sp500_data['High'].max(), 'item') else sp500_data['High'].max()
        low_min = sp500_data['Low'].min().item() if hasattr(sp500_data['Low'].min(), 'item') else sp500_data['Low'].min()
        mean_return = sp500_data['Daily_Return'].mean().item() if hasattr(sp500_data['Daily_Return'].mean(), 'item') else sp500_data['Daily_Return'].mean()
        std_return = sp500_data['Daily_Return'].std().item() if hasattr(sp500_data['Daily_Return'].std(), 'item') else sp500_data['Daily_Return'].std()
        print(f"   最高点: {high_max:.2f} ({high_max_idx.strftime('%Y-%m-%d')})")
        print(f"   最低点: {low_min:.2f} ({low_min_idx.strftime('%Y-%m-%d')})")
        print(f"   平均日涨跌: {(mean_return * 100):.3f}%")
        print(f"   日波动率: {(std_return * 100):.3f}%")
    
    if nasdaq100_data is not None:
        print("\n📊 纳斯达克100 (NASDAQ 100) 统计:")
        print(f"   总交易日: {len(nasdaq100_data)} 天")
        close_first = nasdaq100_data['Close'].iloc[0].item() if hasattr(nasdaq100_data['Close'].iloc[0], 'item') else nasdaq100_data['Close'].iloc[0]
        close_last = nasdaq100_data['Close'].iloc[-1].item() if hasattr(nasdaq100_data['Close'].iloc[-1], 'item') else nasdaq100_data['Close'].iloc[-1]
        print(f"   期间涨幅: {((close_last / close_first - 1) * 100):.2f}%")
        high_max_idx = nasdaq100_data['High'].idxmax()
        low_min_idx = nasdaq100_data['Low'].idxmin()
        # 处理MultiIndex情况
        if isinstance(high_max_idx, pd.Series):
            high_max_idx = high_max_idx.iloc[0]
        if isinstance(low_min_idx, pd.Series):
            low_min_idx = low_min_idx.iloc[0]
        high_max = nasdaq100_data['High'].max().item() if hasattr(nasdaq100_data['High'].max(), 'item') else nasdaq100_data['High'].max()
        low_min = nasdaq100_data['Low'].min().item() if hasattr(nasdaq100_data['Low'].min(), 'item') else nasdaq100_data['Low'].min()
        mean_return = nasdaq100_data['Daily_Return'].mean().item() if hasattr(nasdaq100_data['Daily_Return'].mean(), 'item') else nasdaq100_data['Daily_Return'].mean()
        std_return = nasdaq100_data['Daily_Return'].std().item() if hasattr(nasdaq100_data['Daily_Return'].std(), 'item') else nasdaq100_data['Daily_Return'].std()
        print(f"   最高点: {high_max:.2f} ({high_max_idx.strftime('%Y-%m-%d')})")
        print(f"   最低点: {low_min:.2f} ({low_min_idx.strftime('%Y-%m-%d')})")
        print(f"   平均日涨跌: {(mean_return * 100):.3f}%")
        print(f"   日波动率: {(std_return * 100):.3f}%")
    
    if csi930955_data is not None:
        print("\n📊 930955.SS指数 统计:")
        print(f"   总交易日: {len(csi930955_data)} 天")
        close_first = csi930955_data['Close'].iloc[0].item() if hasattr(csi930955_data['Close'].iloc[0], 'item') else csi930955_data['Close'].iloc[0]
        close_last = csi930955_data['Close'].iloc[-1].item() if hasattr(csi930955_data['Close'].iloc[-1], 'item') else csi930955_data['Close'].iloc[-1]
        print(f"   期间涨幅: {((close_last / close_first - 1) * 100):.2f}%")
        high_max_idx = csi930955_data['High'].idxmax()
        low_min_idx = csi930955_data['Low'].idxmin()
        # 处理MultiIndex情况
        if isinstance(high_max_idx, pd.Series):
            high_max_idx = high_max_idx.iloc[0]
        if isinstance(low_min_idx, pd.Series):
            low_min_idx = low_min_idx.iloc[0]
        high_max = csi930955_data['High'].max().item() if hasattr(csi930955_data['High'].max(), 'item') else csi930955_data['High'].max()
        low_min = csi930955_data['Low'].min().item() if hasattr(csi930955_data['Low'].min(), 'item') else csi930955_data['Low'].min()
        mean_return = csi930955_data['Daily_Return'].mean().item() if hasattr(csi930955_data['Daily_Return'].mean(), 'item') else csi930955_data['Daily_Return'].mean()
        std_return = csi930955_data['Daily_Return'].std().item() if hasattr(csi930955_data['Daily_Return'].std(), 'item') else csi930955_data['Daily_Return'].std()
        print(f"   最高点: {high_max:.2f} ({high_max_idx.strftime('%Y-%m-%d')})")
        print(f"   最低点: {low_min:.2f} ({low_min_idx.strftime('%Y-%m-%d')})")
        print(f"   平均日涨跌: {(mean_return * 100):.3f}%")
        print(f"   日波动率: {(std_return * 100):.3f}%")
    
    print("\n" + "="*60)


def main():
    """主函数"""
    print("="*60)
    print("开始下载指数历史数据")
    print("="*60)
    
    # 下载标普500数据
    sp500_data = download_index_data(
        ticker='^GSPC',
        name='标普500 (S&P 500)',
        start_date='2010-01-01'
    )
    
    # 下载纳斯达克100数据
    nasdaq100_data = download_index_data(
        ticker='^NDX',
        name='纳斯达克100 (NASDAQ 100)',
        start_date='2010-01-01'
    )
    
    # 下载930955.SS指数数据
    csi930955_data = download_index_data(
        ticker='930955.SS',
        name='930955.SS指数',
        start_date='2010-01-01'
    )
    
    # 保存数据
    print("\n" + "-"*60)
    print("保存数据文件...")
    print("-"*60)
    
    save_data(sp500_data, 'sp500_daily_data.csv')
    save_data(nasdaq100_data, 'nasdaq100_daily_data.csv')
    save_data(csi930955_data, '930955_daily_data.csv')
    
    # 生成摘要报告
    generate_summary_all(sp500_data, nasdaq100_data, csi930955_data)
    
    print("\n✅ 所有任务完成！")
    print(f"📁 数据文件保存在 'data' 目录下\n")


if __name__ == '__main__':
    main()

