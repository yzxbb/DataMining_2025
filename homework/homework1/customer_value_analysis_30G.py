import ast
import pandas as pd
import glob
import time

start_time = time.time()

testing_path = 'data/10G_data_new/part-00000.parquet'

data_scale = '30G'
data_path = {
    '10G': "data/10G_data_new",
    '30G': "data/30G_data_new",
}

file_pattern = data_path[data_scale] + "/*.parquet"
file_list = glob.glob(file_pattern)

df = pd.concat([pd.read_parquet(file) for file in file_list], ignore_index=True)
# df = pd.read_parquet(testing_path)

# 将字典样式字符串解析为Python字典，并获取avg_price
def get_avg_price_from_str(dict_str):
    try:
        data_dict = ast.literal_eval(dict_str)  # 将字符串解析为字典
        return data_dict.get('avg_price', 0)
    except:
        return 0

df["avg_purchase_price"] = df["purchase_history"].apply(get_avg_price_from_str)

# 筛选高价值用户
high_value_users = df[
    ((df['age'] > 25) & (df['income'] > 500000)) |
    (df['avg_purchase_price'] > 5000)
]

print("潜在高价值用户数量:", len(high_value_users))
print(high_value_users[["id", "age", "income", "avg_purchase_price"]].head())

end_time = time.time()
execution_time = end_time - start_time
print(f"程序执行时间: {execution_time:.2f}秒")