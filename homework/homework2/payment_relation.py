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

def extract_high_value(purchase_history):
    try:
        items = json.loads(purchase_history)
        return any(item["price"] > 5000 for item in items)
    except:
        return False

data["categories"] = data["purchase_history"].map(extract_categories, meta=('categories', 'object'))
data["high_value"] = data["purchase_history"].map(extract_high_value, meta=('high_value', 'bool'))

# Step 3: Combine Payment Method and Categories
data["payment_and_categories"] = data.map_partitions(
    lambda df: df.apply(lambda row: [(row["payment_method"], category) for category in row["categories"]], axis=1),
    meta=('payment_and_categories', 'object')
)

# Flatten the list of tuples
transactions = data.explode("payment_and_categories").dropna(subset=["payment_and_categories"])
transactions = transactions.groupby("order_id")["payment_and_categories"].apply(list, meta=('payment_and_categories', 'object')).compute()

# Step 4: One-Hot Encoding for Apriori
from mlxtend.preprocessing import TransactionEncoder

te = TransactionEncoder()
te_ary = te.fit(transactions).transform(transactions)
df = pd.DataFrame(te_ary, columns=te.columns_)

# Step 5: Frequent Itemsets and Association Rules
frequent_itemsets = apriori(df, min_support=0.01, use_colnames=True)
rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=0.6)

# Step 6: Analyze High-Value Items
high_value_data = data[data["high_value"]].compute()
high_value_payment_methods = high_value_data["payment_method"].value_counts()

# Output Results
print("Frequent Itemsets:")
print(frequent_itemsets)

print("\nAssociation Rules:")
print(rules)

print("\nHigh-Value Payment Methods:")
print(high_value_payment_methods)

# Save results to CSV
frequent_itemsets.to_csv("payment_category_frequent_itemsets.csv", index=False)
rules.to_csv("payment_category_association_rules.csv", index=False)
high_value_payment_methods.to_csv("high_value_payment_methods.csv", index=True)

print("结果已保存为 CSV 文件：")
print("- payment_category_frequent_itemsets.csv")
print("- payment_category_association_rules.csv")
print("- high_value_payment_methods.csv")