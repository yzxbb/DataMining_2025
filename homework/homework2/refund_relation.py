import dask.dataframe as dd
import pandas as pd
import json
from mlxtend.frequent_patterns import apriori, association_rules

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

# Filter for refunded or partially refunded orders
refunded_data = data[data["payment_status"].isin(["已退款", "部分退款"])]

# Step 3: Aggregate Refunded Orders
# Explode categories to analyze combinations
refunded_transactions = refunded_data.explode("categories").groupby("order_id")["categories"].apply(list, meta=('categories', 'object')).compute()

# Step 4: One-Hot Encoding for Apriori
from mlxtend.preprocessing import TransactionEncoder

te = TransactionEncoder()
te_ary = te.fit(refunded_transactions).transform(refunded_transactions)
df = pd.DataFrame(te_ary, columns=te.columns_)

# Step 5: Frequent Itemsets and Association Rules
frequent_itemsets = apriori(df, min_support=0.005, use_colnames=True)
rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=0.4)

# Step 6: Save Results
frequent_itemsets.to_csv("refunded_frequent_itemsets.csv", index=False)
rules.to_csv("refunded_association_rules.csv", index=False)

print("结果已保存为 CSV 文件：")
print("- refunded_frequent_itemsets.csv：与退款相关的频繁项集")
print("- refunded_association_rules.csv：与退款相关的关联规则")