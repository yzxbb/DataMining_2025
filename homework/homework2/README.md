# Homework 2 - 数据挖掘任务说明

本项目包含四个 Python 程序，分别实现了不同的数据挖掘任务，具体如下：

---

## 1. 商品类别关联规则挖掘 (`category_relation.py`)

### 功能：
- 分析用户在同一订单中购买的不同商品类别之间的关联关系。
- 挖掘支持度（support）≥ 0.02、置信度（confidence）≥ 0.5 的频繁项集和关联规则。
- 特别关注电子产品与其他类别之间的关联关系。

### 输出：
- homework\homework2\results\frequent_itemsets1.csv

---

## 2. 支付方式与商品类别的关联分析 (`payment_relation.py`)

### 功能：
- 挖掘不同支付方式与商品类别之间的关联规则。
- 分析高价值商品（价格 > 5000）的首选支付方式。
- 找出支持度 ≥ 0.01、置信度 ≥ 0.6 的规则。

### 输出：
- homework\homework2\results\frequent_itemsets2.csv

---

## 3. 时间序列模式挖掘 (`time_sequence_relation.py`)

### 功能：
- 分析用户购物行为的季节性模式（按季度、月份或星期）。
- 识别特定商品类别在不同时间段的购买频率变化。
- 探索 "先购买 A 类别，后购买 B 类别" 的时序模式。

---

## 4. 退款模式分析 (`refund_relation.py`)

### 功能：
- 挖掘与 "已退款" 或 "部分退款" 状态相关的商品类别组合。
- 分析导致退款的可能商品组合模式。
- 找出支持度 ≥ 0.005、置信度 ≥ 0.4 的规则。

### 输出：
- homework\homework2\results\frequent_itemsets4.csv

---

## 环境依赖

请确保安装以下 Python 库：
```bash
pip install dask pandas mlxtend