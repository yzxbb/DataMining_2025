import dask.dataframe as dd
import pandas as pd
import json
from datetime import datetime

# Step 1: Load Data
# filepath: c:\Users\yzxbb\Desktop\DataMining_2025\homework\data\part-00000.parquet
data = dd.read_parquet("c:/Users/yzxbb/Desktop/DataMining_2025/homework/data/part-00000.parquet")

# filepath: c:\Users\yzxbb\Desktop\DataMining_2025\homework\homework2\product_catalog.json
with open("c:/Users/yzxbb/Desktop/DataMining_2025/homework/homework2/product_catalog.json", "r") as f:
    product_catalog = json.load(f)

# Map item_id to categories
item_to_category = {str(i): "Other" for i in range(1, 10000)}  # Default mapping
for product in product_catalog["products"]:
    item_to_category[str(product.get("item_id", ""))] = product.get("categories", "Other")

# Step 2: Preprocess Data
def extract_categories(purchase_history):
    try:
        items = json.loads(purchase_history)
        return [item_to_category.get(str(item["item_id"]), "Other") for item in items]
    except:
        return []

data["categories"] = data["purchase_history"].map(extract_categories, meta=('categories', 'object'))

# Convert purchase_date to datetime
data["purchase_date"] = dd.to_datetime(data["purchase_date"], errors="coerce")

# Step 3: Seasonal Pattern Analysis
# Extract time-based features
data["quarter"] = data["purchase_date"].dt.quarter
data["month"] = data["purchase_date"].dt.month
data["weekday"] = data["purchase_date"].dt.weekday

# Group by time features and categories
seasonal_patterns = data.explode("categories").groupby(["categories", "quarter", "month", "weekday"]).size().compute()
seasonal_patterns = seasonal_patterns.reset_index(name="purchase_count")

# Step 4: Purchase Frequency Analysis
# Group by categories and time features
category_monthly = data.explode("categories").groupby(["categories", "month"]).size().compute()
category_monthly = category_monthly.reset_index(name="purchase_count")

# Step 5: Sequential Pattern Mining
# Sort data by user and purchase_date
data = data.sort_values(by=["user_id", "purchase_date"])

# Create a shifted column to find sequential patterns
data["previous_categories"] = data.groupby("user_id")["categories"].shift(1)

# Filter for "A -> B" patterns
sequential_patterns = data.explode("categories").explode("previous_categories")
sequential_patterns = sequential_patterns.groupby(["previous_categories", "categories"]).size().compute()
sequential_patterns = sequential_patterns.reset_index(name="transition_count")

# Normalize to calculate probabilities
sequential_patterns["probability"] = sequential_patterns["transition_count"] / sequential_patterns.groupby("previous_categories")["transition_count"].transform("sum")

# Step 6: Save Results
seasonal_patterns.to_csv("seasonal_patterns.csv", index=False)
category_monthly.to_csv("category_monthly.csv", index=False)
sequential_patterns.to_csv("sequential_patterns.csv", index=False)

print("结果已保存为 CSV 文件：")
print("- seasonal_patterns.csv：季节性模式")
print("- category_monthly.csv：商品类别的购买频率变化")
print("- sequential_patterns.csv：时序模式")