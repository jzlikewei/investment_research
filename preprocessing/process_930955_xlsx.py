#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
专门处理930955perf.xlsx文件
"""

import pandas as pd
import os

print("="*60)
print("处理930955perf.xlsx文件")
print("="*60)

# 读取xlsx文件
filepath = '../data/930955perf.xlsx'
df = pd.read_excel(filepath)

print(f"\n原始数据: {df.shape[0]} 行 x {df.shape[1]} 列")
print(f"指数代码: {df['指数代码Index Code'].unique()}")
print(f"日期范围: {df['日期Date'].min()} 至 {df['日期Date'].max()}")

# 处理数据
df_clean = pd.DataFrame({
    'Date': pd.to_datetime(df['日期Date'].astype(str), format='%Y%m%d'),
    'Open': pd.to_numeric(df['开盘Open'], errors='coerce'),
    'Close': pd.to_numeric(df['收盘Close'], errors='coerce')
})

# 如果开盘价为空，用收盘价填充
open_na_count = df_clean['Open'].isna().sum()
if open_na_count > 0:
    df_clean['Open'] = df_clean['Open'].fillna(df_clean['Close'])
    print(f"已填充 {open_na_count} 个缺失的开盘价")

# 删除任何仍然为空的行
df_clean = df_clean.dropna()

# 按日期递增排序
df_clean = df_clean.sort_values('Date').reset_index(drop=True)

# 格式化日期
df_clean['Date'] = df_clean['Date'].dt.strftime('%Y-%m-%d')

print(f"\n处理后数据: {len(df_clean)} 行")
print(f"日期范围: {df_clean['Date'].iloc[0]} 至 {df_clean['Date'].iloc[-1]}")

# 显示前后几行
print(f"\n前5行:")
print(df_clean.head())
print(f"\n后5行:")
print(df_clean.tail())

# 保存到processed目录
output_dir = '../data/processed'
os.makedirs(output_dir, exist_ok=True)
output_file = os.path.join(output_dir, '930955_normalized.csv')

df_clean.to_csv(output_file, index=False)
print(f"\n✅ 已保存至: {output_file}")

# 统计信息
print(f"\n📊 数据统计:")
print(f"   总行数: {len(df_clean)}")
print(f"   起始收盘价: {df_clean.loc[0, 'Close']}")
print(f"   最终收盘价: {df_clean.loc[len(df_clean)-1, 'Close']}")
print(f"   期间涨幅: {(float(df_clean.loc[len(df_clean)-1, 'Close']) / float(df_clean.loc[0, 'Close']) - 1) * 100:.2f}%")

print("\n" + "="*60)

