#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一处理指数数据
- 只保留：日期、开盘价、收盘价
- 日期按递增排序
- 统一列名和格式
"""

import pandas as pd
import os
from datetime import datetime

def process_us_index(filepath, index_name):
    """
    处理美股指数数据（yfinance格式）
    """
    print(f"\n处理 {index_name}...")
    
    # 读取数据，跳过第2和第3行（Ticker和Date行）
    df = pd.read_csv(filepath, skiprows=[1, 2])
    
    # 第一列是日期，重命名列
    df.columns = ['Date'] + list(df.columns[1:])
    
    # 提取需要的列
    df_clean = pd.DataFrame({
        'Date': pd.to_datetime(df['Date']),
        'Open': pd.to_numeric(df['Open'], errors='coerce'),
        'Close': pd.to_numeric(df['Close'], errors='coerce')
    })
    
    # 删除无效数据
    df_clean = df_clean.dropna()
    
    # 按日期递增排序
    df_clean = df_clean.sort_values('Date').reset_index(drop=True)
    
    # 格式化日期
    df_clean['Date'] = df_clean['Date'].dt.strftime('%Y-%m-%d')
    
    print(f"   数据条数: {len(df_clean)}")
    print(f"   日期范围: {df_clean['Date'].iloc[0]} 至 {df_clean['Date'].iloc[-1]}")
    
    return df_clean


def process_csi_index(filepath, index_name):
    """
    处理中证指数数据（官网下载格式）
    """
    print(f"\n处理 {index_name}...")
    
    df = pd.read_csv(filepath)
    
    # 根据列名判断数据格式
    if '日期Date' in df.columns:
        # 930955格式：日期是数字格式 20100104
        # 注意：可能包含多个指数代码（如930955和H20955），只保留主代码
        if '指数代码Index Code' in df.columns:
            # 获取最常见的指数代码
            main_code = df['指数代码Index Code'].value_counts().index[0]
            # 如果有多个代码，优先选择数字开头的（如930955而不是H20955）
            unique_codes = df['指数代码Index Code'].unique()
            numeric_codes = [c for c in unique_codes if str(c)[0].isdigit()]
            if len(numeric_codes) > 0:
                main_code = numeric_codes[0]
            
            df = df[df['指数代码Index Code'] == main_code]
            print(f"   使用指数代码: {main_code}")
        
        df_clean = pd.DataFrame({
            'Date': pd.to_datetime(df['日期Date'].astype(str), format='%Y%m%d'),
            'Open': pd.to_numeric(df['开盘Open'], errors='coerce'),
            'Close': pd.to_numeric(df['收盘Close'], errors='coerce')
        })
        
        # 如果开盘价为空，用收盘价填充
        df_clean['Open'] = df_clean['Open'].fillna(df_clean['Close'])
    elif '日期' in df.columns:
        # 980092和CNB00003格式
        # 检查是否有开盘价（CNB00003可能没有）
        if '开盘价' in df.columns:
            df_clean = pd.DataFrame({
                'Date': pd.to_datetime(df['日期']),
                'Open': pd.to_numeric(df['开盘价'], errors='coerce'),
                'Close': pd.to_numeric(df['收盘价'], errors='coerce')
            })
            
            # 如果开盘价为空，用收盘价填充
            open_na_count = df_clean['Open'].isna().sum()
            if open_na_count > 0:
                df_clean['Open'] = df_clean['Open'].fillna(df_clean['Close'])
                print(f"   注意: {open_na_count} 条数据缺失开盘价，已用收盘价填充")
        else:
            # 如果没有开盘价列，用收盘价填充
            df_clean = pd.DataFrame({
                'Date': pd.to_datetime(df['日期']),
                'Open': pd.to_numeric(df['收盘价'], errors='coerce'),
                'Close': pd.to_numeric(df['收盘价'], errors='coerce')
            })
            print(f"   注意: 该数据没有开盘价列，使用收盘价代替")
    else:
        raise ValueError(f"未识别的数据格式: {filepath}")
    
    # 删除任何仍然为空的行
    df_clean = df_clean.dropna()
    
    # 按日期递增排序
    df_clean = df_clean.sort_values('Date').reset_index(drop=True)
    
    # 格式化日期
    df_clean['Date'] = df_clean['Date'].dt.strftime('%Y-%m-%d')
    
    print(f"   数据条数: {len(df_clean)}")
    print(f"   日期范围: {df_clean['Date'].iloc[0]} 至 {df_clean['Date'].iloc[-1]}")
    
    return df_clean


def main():
    """主函数"""
    print("="*60)
    print("开始统一处理指数数据")
    print("="*60)
    
    # 数据文件配置
    data_config = [
        {
            'file': '../data/sp500_daily_data.csv',
            'name': '标普500 (S&P 500)',
            'output': 'sp500_normalized.csv',
            'type': 'us'
        },
        {
            'file': '../data/nasdaq100_daily_data.csv',
            'name': '纳斯达克100 (NASDAQ 100)',
            'output': 'nasdaq100_normalized.csv',
            'type': 'us'
        },
        {
            'file': '../data/930955perf.csvx',
            'name': '中证红利低波动100 (930955)',
            'output': '930955_normalized.csv',
            'type': 'csi'
        },
        {
            'file': '../data/980092_perf_20121231-20251029.csv',
            'name': '980092指数',
            'output': '980092_normalized.csv',
            'type': 'csi'
        },
        {
            'file': '../data/CNB00003_perf_20111230-20251029.csv',
            'name': 'CNB00003指数',
            'output': 'CNB00003_normalized.csv',
            'type': 'csi'
        }
    ]
    
    # 创建输出目录
    output_dir = '../data/processed'
    os.makedirs(output_dir, exist_ok=True)
    
    # 处理每个数据文件
    processed_count = 0
    for config in data_config:
        filepath = config['file']
        
        # 检查文件是否存在
        if not os.path.exists(filepath):
            print(f"\n⚠️  跳过 {config['name']}: 文件不存在 ({filepath})")
            continue
        
        try:
            # 根据类型选择处理函数
            if config['type'] == 'us':
                df = process_us_index(filepath, config['name'])
            else:
                df = process_csi_index(filepath, config['name'])
            
            # 保存处理后的数据
            output_path = os.path.join(output_dir, config['output'])
            df.to_csv(output_path, index=False)
            print(f"   ✅ 已保存至: {output_path}")
            
            processed_count += 1
            
        except Exception as e:
            print(f"\n❌ 处理 {config['name']} 时出错: {str(e)}")
            continue
    
    # 总结
    print("\n" + "="*60)
    print(f"处理完成！成功处理 {processed_count}/{len(data_config)} 个文件")
    print(f"所有处理后的数据保存在: {output_dir}/")
    print("="*60)
    
    # 显示统一后的数据格式说明
    print("\n📊 统一后的数据格式:")
    print("  列名: Date, Open, Close")
    print("  日期格式: YYYY-MM-DD")
    print("  排序: 日期递增（从早到晚）")
    print()


if __name__ == '__main__':
    main()

