import dask.dataframe as dd
import pandas as pd
import json
from mlxtend.frequent_patterns import apriori, association_rules

# Step 1: Load Data with Dask
# filepath: c:\Users\yzxbb\Desktop\DataMining_2025\homework\data\part-00000.parquet
data = dd.read_parquet("homework\data\30G_data_new\part-00000.parquet")

# filepath: c:\Users\yzxbb\Desktop\DataMining_2025\homework\homework2\product_catalog.json
with open("homework\homework2\product_catalog.json", "r") as f:
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

# Step 3: Aggregate by Order
transactions = data.groupby("order_id")["categories"].apply(list, meta=('categories', 'object')).compute()

# Step 4: One-Hot Encoding for Apriori
from mlxtend.preprocessing import TransactionEncoder

te = TransactionEncoder()
te_ary = te.fit(transactions).transform(transactions)
df = pd.DataFrame(te_ary, columns=te.columns_)

# Step 5: Frequent Itemsets and Association Rules
frequent_itemsets = apriori(df, min_support=0.02, use_colnames=True)
rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=0.5)

# Step 6: Filter Rules for Electronics
electronics_rules = rules[rules["antecedents"].apply(lambda x: "Electronics" in x or "Electronics" in rules["consequents"])]

# Output Results
print("Frequent Itemsets:")
print(frequent_itemsets)

# Save frequent itemsets to CSV
frequent_itemsets.to_csv("frequent_itemsets.csv", index=False)

print("频繁项集已保存为 'frequent_itemsets.csv'")

print("\nAssociation Rules:")
print(rules)

print("\nElectronics-Related Rules:")
print(electronics_rules)