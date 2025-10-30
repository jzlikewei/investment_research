# 投资研究 - 指数数据下载

## 📊 已下载的数据

### 1. 标普500指数 (S&P 500) ✅
- **文件**: `data/sp500_daily_data.csv`
- **代码**: ^GSPC
- **时间范围**: 2010-01-04 至 2025-10-29
- **数据条数**: 3,981 条
- **期间涨幅**: 508.18%
- **数据源**: Yahoo Finance (yfinance)

### 2. 纳斯达克100指数 (NASDAQ 100) ✅
- **文件**: `data/nasdaq100_daily_data.csv`
- **代码**: ^NDX
- **时间范围**: 2010-01-04 至 2025-10-29
- **数据条数**: 3,981 条
- **期间涨幅**: 1,284.42%
- **数据源**: Yahoo Finance (yfinance)

### 3. 930955 中证红利低波动100指数 ✅
- **文件**: `data/930955perf.xlsx`
- **数据源**: 中证指数官网手动下载
- **官网链接**: https://www.csindex.com.cn/#/indices/family/detail?indexCode=930955

### 4. 980092指数 ✅
- **文件**: `data/980092_perf_20121231-20251029.csv`
- **时间范围**: 2012-12-31 至 2025-10-29
- **数据条数**: 3,113 条
- **数据源**: 手动导入的XLS文件

## 📥 A股指数数据下载

### 中证指数官网
对于中国A股指数，推荐直接从官网下载历史数据：

- **中证指数有限公司**: https://www.csindex.com.cn/
  - 示例（930955）: https://www.csindex.com.cn/#/indices/family/detail?indexCode=930955
  
- **国证指数**: https://www.cnindex.com.cn/
  - 示例（CNB00003）: https://www.cnindex.com.cn/module/index-detail.html?act_menu=1&indexCode=CNB00003

### 下载步骤
1. 访问对应指数的官网链接
2. 找到"历史数据"或"数据下载"栏目
3. 选择时间范围（如2010-01-01至今）
4. 下载Excel或CSV格式文件
5. 将文件放入 `data/` 目录

### 其他数据源
- **Tushare**: https://tushare.pro/ （需注册获取token）
- **AKShare**: 免费开源金融数据接口库
- **Wind金融终端**: 专业机构版
- **东方财富Choice**: 专业数据终端

## 📁 数据文件说明

### CSV文件列说明
- **Date**: 日期
- **Open**: 开盘价
- **High**: 最高价
- **Low**: 最低价
- **Close**: 收盘价
- **Volume**: 成交量
- **Adj Close**: 调整后收盘价
- **Daily_Return**: 日收益率
- **Cumulative_Return**: 累计收益率

## 🔧 使用脚本

### 下载美股指数数据
```bash
python download_index_data.py
```
当前配置下载：标普500、纳斯达克100

### 数据预处理
查看/转换Excel数据为CSV格式：
```bash
cd preprocessing
python read_xls_data.py
```
读取 `data/` 目录中的Excel文件并转换为CSV格式

更多预处理工具请查看 `preprocessing/` 目录

## 📦 依赖包

### 安装依赖
```bash
pip install -r requirements.txt
```

### 依赖列表
- **yfinance** >= 0.2.31 - 用于下载美股指数数据
- **pandas** >= 2.0.0 - 数据处理和分析

## 💡 使用建议

### 美股指数
- ✅ 使用 `download_index_data.py` 脚本自动下载
- 数据源：Yahoo Finance (yfinance)
- 优点：免费、实时、历史数据完整

### A股指数
- ✅ 推荐从指数官网手动下载
- 优点：数据权威、准确、免费
- 缺点：需要手动操作，不支持自动更新

### 数据管理
1. 所有数据统一保存在 `data/` 目录
2. 美股数据可通过脚本定期更新
3. A股数据需要定期手动下载更新
4. 建议使用版本控制跟踪数据变化

