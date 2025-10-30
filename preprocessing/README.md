# 数据预处理模块

本目录包含所有数据预处理相关的脚本。

## 📁 文件说明

### read_xls_data.py
- **功能**: 读取并转换Excel文件为CSV格式
- **用途**: 处理从指数官网下载的Excel格式历史数据
- **使用方法**: 
  ```bash
  cd preprocessing
  python read_xls_data.py
  ```
- **输入**: `../data/` 目录下的 `.xls` 或 `.xlsx` 文件
- **输出**: 同名的 `.csv` 文件保存在 `../data/` 目录

### normalize_index_data.py ⭐
- **功能**: 统一处理所有指数数据，标准化格式
- **用途**: 将不同格式的指数数据统一为相同的格式
- **使用方法**:
  ```bash
  cd preprocessing
  python normalize_index_data.py
  ```
- **输入**: `../data/` 目录下的各种指数CSV文件
- **输出**: `../data/processed/` 目录下的标准化文件

#### 处理内容
- ✅ 只保留三列：Date（日期）、Open（开盘价）、Close（收盘价）
- ✅ 统一日期格式为 `YYYY-MM-DD`
- ✅ 按日期递增排序（从早到晚）
- ✅ 自动填充缺失的开盘价（使用收盘价）
- ✅ 删除无效数据行

#### 支持的指数
- 标普500 (S&P 500)
- 纳斯达克100 (NASDAQ 100)
- 中证红利低波动100 (930955)
- 980092指数
- CNB00003指数

## 🔧 使用说明

### 快速开始
```bash
# 1. 进入预处理目录
cd preprocessing

# 2. 转换Excel文件为CSV（如果需要）
python read_xls_data.py

# 3. 统一处理所有指数数据
python normalize_index_data.py
```

### 输出说明
标准化后的数据保存在 `../data/processed/` 目录，格式统一为：

| Date       | Open     | Close    |
|------------|----------|----------|
| 2010-01-04 | 1116.56  | 1132.99  |
| 2010-01-05 | 1132.66  | 1136.52  |
| ...        | ...      | ...      |

## 📝 开发规范

- 所有预处理脚本统一放在此目录
- 输入文件从 `../data/` 读取
- 输出文件保存到 `../data/` 或 `../data/processed/` 目录
- 保持原始文件不变，生成新的处理后文件
- 统一数据格式，方便后续分析

