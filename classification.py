import os
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.preprocessing import OneHotEncoder, LabelEncoder
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.utils.class_weight import compute_class_weight

# 配置参数
DATA_PATH = "/home/zym/DataMining/project/data/steam_games.ndjson"
SAVE_DIR = "project/results/classification"
CLASS_BINS = [
    (0, 0),
    (0, 20000),
    (20000, 50000),
    (50000, 100000),
    (100000, 200000),
    (200000, 500000),
    (500000, 1000000),
    (1000000, 2000000),
    (2000000, 5000000),
    (5000000, 10000000),
    (10000000, 20000000),
    (20000000, 50000000),
    (50000000, 100000000),
    (100000000, 200000000),
    (200000000, 500000000),
]


def create_labels(lower, upper):
    """将区间转换为标签字符串"""
    if lower == upper:
        return f"{lower}-{upper}"
    return f"{lower}-{upper}"


CLASS_LABELS = [create_labels(b[0], b[1]) for b in CLASS_BINS]

# 创建保存目录
os.makedirs(SAVE_DIR, exist_ok=True)


# 数据预处理函数
def preprocess_data(df):
    # 转换目标变量
    def get_owner_class(owner_str):
        try:
            lower, upper = map(
                int, owner_str.replace(" ", "").replace(",", "").split("-")
            )
            # 合并区间为 50000000-500000000
            if lower >= 50000000 and upper <= 500000000:
                return "50000000-500000000"
            for min_val, max_val in CLASS_BINS:
                if lower >= min_val and upper <= max_val:
                    return create_labels(min_val, max_val)
            return "Other"
        except:
            return "Invalid"

    df["owner_class"] = df["estimated_owners"].apply(get_owner_class)
    df = df[df["owner_class"].isin(CLASS_LABELS)].copy()

    # 特征工程
    df["release_year"] = pd.to_datetime(df["release_date"], errors="coerce").dt.year
    df["positive_ratio"] = df["positive"] / (df["positive"] + df["negative"] + 1e-6)
    df["num_languages"] = df["supported_languages"].apply(len)
    df["has_achievements"] = df["achievements"].apply(lambda x: 1 if x > 0 else 0)
    # 确保列中只有数值数据
    df["discount"] = pd.to_numeric(df["discount"], errors="coerce")

    # 移除 NaN 值
    df = df.dropna(subset=["discount"])
    df["discount_group"] = pd.cut(
        df["discount"],
        bins=[-1, 0, 25, 50, 75, 101],
        labels=["No Discount", "0-25%", "25-50%", "50-75%", "75-100%"],
    )

    # 选择特征
    features = df[
        [
            "price",
            "release_year",
            "windows",
            "mac",
            "linux",
            "metacritic_score",
            "positive_ratio",
            "num_languages",
            "has_achievements",
            "discount_group",
            "recommendations",
        ]
    ]

    # 处理缺失值
    features["metacritic_score"] = features["metacritic_score"].fillna(
        features["metacritic_score"].median()
    )
    features["release_year"] = features["release_year"].fillna(
        features["release_year"].mode()[0]
    )

    return features, df["owner_class"]


# 加载数据
raw_data = []
with open(DATA_PATH, "r") as f:
    for line in f:
        try:
            raw_data.append(json.loads(line))
        except json.JSONDecodeError:
            continue
df = pd.DataFrame(raw_data)

# 执行预处理
X, y = preprocess_data(df)

# 编码目标变量
le = LabelEncoder()
y = le.fit_transform(y)
print("y:", y)

# 检查类别分布
y_counts = pd.Series(y).value_counts()
print("类别分布：\n", y_counts)

# 移除样本数少于 2 的类别
valid_classes = y_counts[y_counts > 1].index
X = X[np.isin(y, valid_classes)]
y = y[np.isin(y, valid_classes)]

# 划分数据集
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)

# 定义预处理管道
numeric_features = [
    "price",
    "release_year",
    "metacritic_score",
    "positive_ratio",
    "num_languages",
    "recommendations",
]
categorical_features = ["discount_group"]

preprocessor = ColumnTransformer(
    transformers=[
        ("num", "passthrough", numeric_features),
        ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features),
    ]
)

# 计算类别权重
classes = np.unique(y_train)
weights = compute_class_weight("balanced", classes=classes, y=y_train)
class_weights = dict(zip(classes, weights))

# 创建模型管道
pipeline = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        (
            "classifier",
            RandomForestClassifier(
                class_weight=class_weights, random_state=42, n_jobs=-1
            ),
        ),
    ]
)

# 网格搜索参数
param_grid = {
    "classifier__n_estimators": [100, 200],
    "classifier__max_depth": [None, 20],
    "classifier__min_samples_split": [2, 5],
}

grid_search = GridSearchCV(pipeline, param_grid, cv=3, scoring="f1_weighted")
grid_search.fit(X_train, y_train)

# 获取最佳模型
best_model = grid_search.best_estimator_

# 模型评估
y_pred = best_model.predict(X_test)

print(np.unique(y_pred))
print(np.unique(y_test))
print(np.unique(y_train))

# 生成报告
report = classification_report(
    y_test,
    y_pred,
    target_names=le.classes_,
    output_dict=True,
)
report_df = pd.DataFrame(report).transpose()

# 保存结果
report_df.to_csv(f"{SAVE_DIR}/classification_report.csv")
pd.DataFrame(
    confusion_matrix(y_test, y_pred), index=le.classes_, columns=le.classes_
).to_csv(f"{SAVE_DIR}/confusion_matrix.csv")

# 可视化特征重要性
feature_names = numeric_features + list(
    best_model.named_steps["preprocessor"]
    .named_transformers_["cat"]
    .get_feature_names_out(categorical_features)
)

importances = best_model.named_steps["classifier"].feature_importances_

plt.figure(figsize=(12, 8))
sns.barplot(x=importances, y=feature_names)
plt.title("Feature Importance")
plt.tight_layout()
plt.savefig(f"{SAVE_DIR}/feature_importance.png", dpi=300)
plt.close()

# 可视化混淆矩阵（简化版）
plt.figure(figsize=(15, 10))
sns.heatmap(
    confusion_matrix(y_test, y_pred),
    annot=True,
    fmt="d",
    cmap="Blues",
    xticklabels=le.classes_,
    yticklabels=le.classes_,
)
plt.title("Confusion Matrix")
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.xticks(rotation=45)
plt.yticks(rotation=0)
plt.tight_layout()
plt.savefig(f"{SAVE_DIR}/confusion_matrix.png", dpi=300)
plt.close()

print(
    f"""
=== 分类模型训练完成 ===
最佳参数：{grid_search.best_params_}
模型准确率：{report['accuracy']:.2%}
详细结果保存至：{SAVE_DIR}
"""
)
