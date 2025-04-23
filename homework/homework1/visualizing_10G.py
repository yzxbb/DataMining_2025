import pandas as pd
import matplotlib.pyplot as plt
import glob
import time

data_scale = '10G'  # 数据规模

plt.rcParams['font.family'] = 'WenQuanYi Zen Hei' 

data_path ={
    '10G': "data/10G_data_new",
    '30G': "data/30G_data_new",
}

# 记录程序开始时间
start_time = time.time()

# 文件路径模式
file_pattern = data_path[data_scale] + "/*.parquet"

# 获取所有匹配的文件路径
file_list = glob.glob(file_pattern)

# 读取并合并所有文件
data = pd.concat([pd.read_parquet(file) for file in file_list], ignore_index=True)

# 检查数据
print("合并后的数据预览：")
print(data.head())

# 可视化 1: 用户年龄分布直方图
plt.figure(figsize=(10, 6))
data['age'].hist(bins=30, color='skyblue', edgecolor='black')
plt.title('用户年龄分布')
plt.xlabel('年龄')
plt.ylabel('用户数量')
plt.grid(False)
plt.savefig("results/visualization/" + data_scale + f"/{data_scale}_age_distribution.png", dpi=300)  # 保存图像
plt.show()

# 可视化 2: 用户收入分布直方图
plt.figure(figsize=(10, 6))
data['income'].hist(bins=30, color='purple', edgecolor='black')
plt.title('用户收入分布')
plt.xlabel('收入')
plt.ylabel('用户数量')
plt.grid(False)
plt.savefig("results/visualization/" + data_scale + f"/{data_scale}_income_distribution.png", dpi=300)
plt.show()

# 可视化 3: 前十个国家的用户分布条形图
plt.figure(figsize=(10, 6))
top_countries = data['country'].value_counts().head(10)
top_countries.plot(kind='bar', color='teal', edgecolor='black')
plt.title('前十个国家的用户分布')
plt.xlabel('国家')
plt.ylabel('用户数量')
plt.grid(False)
plt.savefig("results/visualization/" + data_scale + f"/{data_scale}_country_distribution.png", dpi=300)
plt.show()

# 记录程序结束时间
# 程序运行时间: 220.20 秒
end_time = time.time()
print(f"程序运行时间: {end_time - start_time:.2f} 秒")