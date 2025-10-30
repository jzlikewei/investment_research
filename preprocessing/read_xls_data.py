#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
读取XLS文件数据
"""

import pandas as pd
import os

print("="*60)
print("读取XLS文件数据")
print("="*60)

# 查找data目录中的xls文件
data_dir = '../data'
xls_files = [f for f in os.listdir(data_dir) if f.endswith('.xls') or f.endswith('.xlsx')]

print(f"\n找到 {len(xls_files)} 个Excel文件:")
for f in xls_files:
    print(f"  - {f}")

if xls_files:
    for xls_file in xls_files:
        filepath = os.path.join(data_dir, xls_file)
        print(f"\n\n{'='*60}")
        print(f"读取文件: {xls_file}")
        print('='*60)
        
        try:
            # 读取Excel文件
            df = pd.read_excel(filepath)
            
            print(f"\n数据形状: {df.shape[0]} 行 x {df.shape[1]} 列")
            print(f"\n列名:")
            print(df.columns.tolist())
            
            print(f"\n前10行数据:")
            print(df.head(10))
            
            print(f"\n后10行数据:")
            print(df.tail(10))
            
            print(f"\n数据类型:")
            print(df.dtypes)
            
            # 尝试保存为CSV
            csv_filename = xls_file.replace('.xls', '.csv').replace('.xlsx', '.csv')
            csv_filepath = os.path.join(data_dir, csv_filename)
            df.to_csv(csv_filepath, index=False)
            print(f"\n✅ 已转换为CSV: {csv_filepath}")
            
        except Exception as e:
            print(f"❌ 读取失败: {str(e)}")
else:
    print("\n未找到Excel文件")

