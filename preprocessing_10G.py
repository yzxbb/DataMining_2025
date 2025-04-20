import glob
import time
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# 记录程序开始时间
start_time = time.time()

data_scale = '10G'  # 数据规模

plt.rcParams['font.family'] = 'WenQuanYi Zen Hei' 

data_path ={
    '10G': "data/10G_data_new",
    '30G': "data/30G_data_new",
}

# 文件路径模式
file_pattern = data_path[data_scale] + "/*.parquet"

# 获取所有匹配的文件路径
file_list = glob.glob(file_pattern)

# 读取并合并所有文件
df = pd.concat([pd.read_parquet(file) for file in file_list], ignore_index=True)

# 原始数据规模
original_count = len(df)
print(f"原始数据量: {original_count}")

# 1. 缺失值情况统计
missing_info = df.isnull().sum()
missing_total = missing_info.sum()
missing_ratio = missing_total / (original_count * df.shape[1])
print("\n[缺失值统计]")
print(missing_info)
print(f"缺失值总数: {missing_total}, 缺失值占所有单元格的比例: {missing_ratio:.2%}")

# 示例处理：直接删除包含缺失值所在行
df_cleaned = df.dropna()
after_dropna_count = len(df_cleaned)
print(f"\n删除包含缺失值的行后，剩余数据量: {after_dropna_count}")

# 统计address字段为"Non-Chinese Address Placeholder"的行数及比例
non_chinese_count = df[df['address'] == 'Non-Chinese Address Placeholder'].shape[0]
print(f"\n[地址统计]")
print(f"包含'Non-Chinese Address Placeholder'的行数: {non_chinese_count}")
print(f"占比: {non_chinese_count / len(df):.2%}")

# 2. 异常值情况统计（示例：对数值型列使用 1.5 * IQR）
numeric_cols = df_cleaned.select_dtypes(include=[np.number]).columns

outlier_indices = []
for col in numeric_cols:
    Q1 = df_cleaned[col].quantile(0.25)
    Q3 = df_cleaned[col].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    col_outlier_indices = df_cleaned[(df_cleaned[col] < lower_bound) | (df_cleaned[col] > upper_bound)].index
    outlier_indices.extend(col_outlier_indices)

outlier_indices = list(set(outlier_indices))  # 去重
print(f"\n[异常值统计]")
print(f"异常值行数: {len(outlier_indices)}, 占当前数据比例: {len(outlier_indices)/after_dropna_count:.2%}")

# 示例处理：删除异常值所在行
df_final = df_cleaned.drop(index=outlier_indices)
final_count = len(df_final)
print(f"\n删除异常值后，剩余数据量: {final_count}")

# 整体情况概览
print("\n[整体情况]")
print(f"原始数据量: {original_count}")
print(f"删除缺失值后数据量: {after_dropna_count}")
print(f"最终数据量: {final_count}")

# 程序运行时间: 297.43秒
end_time = time.time()
print(f"程序运行时间: {end_time - start_time:.2f}秒")