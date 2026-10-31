import pandas as pd
from pathlib import Path


# ============================================================
# 0. 專案路徑設定
# ============================================================

# fashion_crawler 專案根目錄
BASE_DIR = Path(__file__).resolve().parent.parent

# 資料夾位置
CLEANED_DIR = BASE_DIR / "data" / "cleaned"
ANALYSIS_DIR = BASE_DIR / "data" / "analysis"

# 輸入檔案
INPUT_FILE = (
    CLEANED_DIR /
    "uniqlo_products_cleaned.csv"
)

# 輸出檔案
OUTPUT_FILE = (
    ANALYSIS_DIR /
    "uniqlo_products_analysis.csv"
)

GENDER_ANALYSIS_FILE = (
    ANALYSIS_DIR /
    "uniqlo_gender_analysis.csv"
)

PRICE_RANGE_ANALYSIS_FILE = (
    ANALYSIS_DIR /
    "uniqlo_price_range_analysis.csv"
)

GENDER_CATEGORY_FILE = (
    ANALYSIS_DIR /
    "uniqlo_gender_category.csv"
)

GENDER_CATEGORY_PRICE_FILE = (
    ANALYSIS_DIR /
    "uniqlo_gender_category_price.csv"
)

CATEGORY_ANALYSIS_FILE = (
    ANALYSIS_DIR /
    "uniqlo_category_analysis.csv"
)


# 如果 analysis 資料夾不存在，自動建立
ANALYSIS_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# 1. 讀取清理後資料
# ============================================================

print("正在讀取 UNIQLO 清理後商品資料...")
print("讀取位置：")
print(INPUT_FILE)
print()

df = pd.read_csv(
    INPUT_FILE,
    encoding="utf-8-sig"
)

print("資料讀取完成！")
print()


# ============================================================
# 2. 基本資料檢查
# ============================================================

print("========================================")
print("資料基本資訊")
print("========================================")
print()

print(
    "商品總數：",
    len(df),
    "件"
)

print()

print("資料欄位：")
print(
    df.columns.tolist()
)

print()


# ============================================================
# 3. 檢查缺失值
# ============================================================

print("========================================")
print("缺失值檢查")
print("========================================")
print()

print(
    df.isnull().sum()
)

print()


# ============================================================
# 4. 確認價格格式
# ============================================================

df["price"] = pd.to_numeric(
    df["price"],
    errors="coerce"
)

# 移除沒有價格的資料
df = df.dropna(
    subset=["price"]
)

# 轉成整數
df["price"] = (
    df["price"]
    .astype(int)
)


# ============================================================
# 5. 建立價格區間
# ============================================================

price_bins = [
    0,
    200,
    400,
    600,
    800,
    1000,
    float("inf")
]

price_labels = [
    "200元以下",
    "200-399元",
    "400-599元",
    "600-799元",
    "800-999元",
    "1000元以上"
]

df["price_range"] = pd.cut(
    df["price"],
    bins=price_bins,
    labels=price_labels,
    right=False
)


# ============================================================
# 6. 整體價格統計
# ============================================================

print("========================================")
print("UNIQLO 整體價格統計")
print("========================================")
print()

print(
    "商品數量：",
    len(df),
    "件"
)

print(
    "平均價格：",
    round(
        df["price"].mean(),
        2
    ),
    "元"
)

print(
    "中位數價格：",
    round(
        df["price"].median(),
        2
    ),
    "元"
)

print(
    "最低價格：",
    df["price"].min(),
    "元"
)

print(
    "最高價格：",
    df["price"].max(),
    "元"
)

print()


# ============================================================
# 7. 性別商品數量
# ============================================================

print("========================================")
print("性別商品數量")
print("========================================")
print()

gender_count = (
    df["gender"]
    .value_counts()
)

print(
    gender_count
)

print()


# ============================================================
# 8. 性別商品占比
# ============================================================

print("========================================")
print("性別商品占比")
print("========================================")
print()

gender_percentage = (
    df["gender"]
    .value_counts(
        normalize=True
    )
    .mul(100)
    .round(2)
)

for gender, percentage in gender_percentage.items():

    print(
        f"{gender}：{percentage:.2f}%"
    )

print()


# ============================================================
# 9. 性別平均價格
# ============================================================

print("========================================")
print("性別平均價格")
print("========================================")
print()

gender_avg_price = (
    df.groupby("gender")["price"]
    .mean()
    .round(2)
)

print(
    gender_avg_price
)

print()


# ============================================================
# 10. 建立性別分析表
# ============================================================

gender_analysis = pd.DataFrame({
    "商品數量": gender_count,
    "商品占比": gender_percentage,
    "平均價格": gender_avg_price
})

print("========================================")
print("性別分析表")
print("========================================")
print()

print(
    gender_analysis
)

print()


# ============================================================
# 11. 商品類型數量
# ============================================================

print("========================================")
print("商品類型數量")
print("========================================")
print()

category_count = (
    df["category"]
    .value_counts()
)

print(
    category_count
)

print()


# ============================================================
# 12. 商品類型占比
# ============================================================

print("========================================")
print("商品類型占比")
print("========================================")
print()

category_percentage = (
    df["category"]
    .value_counts(
        normalize=True
    )
    .mul(100)
    .round(2)
)

for category, percentage in category_percentage.items():

    print(
        f"{category}：{percentage:.2f}%"
    )

print()


# ============================================================
# 13. 各商品類型平均價格
# ============================================================

print("========================================")
print("各商品類型平均價格")
print("========================================")
print()

category_avg_price = (
    df.groupby("category")["price"]
    .mean()
    .round(2)
    .reindex(
        category_count.index
    )
)

print(
    category_avg_price
)

print()


# ============================================================
# 14. 各商品類型中位數價格
# ============================================================

print("========================================")
print("各商品類型中位數價格")
print("========================================")
print()

category_median_price = (
    df.groupby("category")["price"]
    .median()
    .round(2)
    .reindex(
        category_count.index
    )
)

print(
    category_median_price
)

print()


# ============================================================
# 15. 各商品類型最低價格
# ============================================================

category_min_price = (
    df.groupby("category")["price"]
    .min()
    .reindex(
        category_count.index
    )
)


# ============================================================
# 16. 各商品類型最高價格
# ============================================================

category_max_price = (
    df.groupby("category")["price"]
    .max()
    .reindex(
        category_count.index
    )
)


# ============================================================
# 17. 建立商品類型完整分析表
# ============================================================

category_analysis = pd.DataFrame({
    "商品數量": category_count,
    "商品占比": category_percentage,
    "平均價格": category_avg_price,
    "中位數價格": category_median_price,
    "最低價格": category_min_price,
    "最高價格": category_max_price
})


print("========================================")
print("商品類型完整分析表")
print("========================================")
print()

print(
    category_analysis
)

print()


# ============================================================
# 18. 價格區間商品數量
# ============================================================

print("========================================")
print("價格區間商品數量")
print("========================================")
print()

price_range_count = (
    df["price_range"]
    .value_counts()
    .reindex(
        price_labels,
        fill_value=0
    )
)

print(
    price_range_count
)

print()


# ============================================================
# 19. 價格區間商品占比
# ============================================================

print("========================================")
print("價格區間商品占比")
print("========================================")
print()

price_range_percentage = (
    df["price_range"]
    .value_counts(
        normalize=True
    )
    .mul(100)
    .reindex(
        price_labels,
        fill_value=0
    )
    .round(2)
)

for price_range, percentage in price_range_percentage.items():

    print(
        f"{price_range}：{percentage:.2f}%"
    )

print()


# ============================================================
# 20. 建立價格區間分析表
# ============================================================

price_range_analysis = pd.DataFrame({
    "商品數量": price_range_count,
    "商品占比": price_range_percentage
})


print("========================================")
print("價格區間分析表")
print("========================================")
print()

print(
    price_range_analysis
)

print()


# ============================================================
# 21. 性別 × 商品類型數量
# ============================================================

print("========================================")
print("性別 × 商品類型數量")
print("========================================")
print()

gender_category = pd.crosstab(
    df["category"],
    df["gender"]
)

# 依照商品數量順序排列
gender_category = (
    gender_category
    .reindex(
        category_count.index,
        fill_value=0
    )
)

print(
    gender_category
)

print()


# ============================================================
# 22. 性別 × 商品類型平均價格
# ============================================================

print("========================================")
print("性別 × 商品類型平均價格")
print("========================================")
print()

gender_category_price = pd.pivot_table(
    df,
    values="price",
    index="category",
    columns="gender",
    aggfunc="mean"
)

gender_category_price = (
    gender_category_price
    .reindex(
        category_count.index
    )
    .round(2)
)

print(
    gender_category_price
)

print()


# ============================================================
# 23. 最便宜商品
# ============================================================

print("========================================")
print("最便宜的 10 件商品")
print("========================================")
print()

cheapest_products = (
    df.sort_values(
        by="price"
    )
    .head(10)
)

print(
    cheapest_products[
        [
            "brand",
            "gender",
            "category",
            "product_name",
            "price"
        ]
    ]
    .to_string(
        index=False
    )
)

print()


# ============================================================
# 24. 最貴商品
# ============================================================

print("========================================")
print("最貴的 10 件商品")
print("========================================")
print()

most_expensive_products = (
    df.sort_values(
        by="price",
        ascending=False
    )
    .head(10)
)

print(
    most_expensive_products[
        [
            "brand",
            "gender",
            "category",
            "product_name",
            "price"
        ]
    ]
    .to_string(
        index=False
    )
)

print()


# ============================================================
# 25. 商品類型占比排名
# ============================================================

print("========================================")
print("商品類型占比排名")
print("========================================")
print()

for rank, (category, percentage) in enumerate(
    category_percentage.items(),
    start=1
):

    count = int(
        category_count[
            category
        ]
    )

    print(
        f"{rank}. "
        f"{category}："
        f"{count} 件 "
        f"({percentage:.2f}%)"
    )

print()


# ============================================================
# 26. 找出商品數量最多的類型
# ============================================================

top_category = (
    category_count.index[0]
)

top_category_count = int(
    category_count.iloc[0]
)

top_category_percentage = float(
    category_percentage.iloc[0]
)


print("========================================")
print("主要商品類型")
print("========================================")
print()

print(
    "商品數量最多的類型：",
    top_category
)

print(
    "商品數量：",
    top_category_count,
    "件"
)

print(
    "商品占比：",
    f"{top_category_percentage:.2f}%"
)

print()


# ============================================================
# 27. 找出平均價格最高的商品類型
# ============================================================

highest_avg_category = (
    category_avg_price.idxmax()
)

highest_avg_category_price = (
    category_avg_price.max()
)


print("========================================")
print("平均價格最高的商品類型")
print("========================================")
print()

print(
    "商品類型：",
    highest_avg_category
)

print(
    "平均價格：",
    f"{highest_avg_category_price:.2f}",
    "元"
)

print()


# ============================================================
# 28. 儲存完整分析資料
# ============================================================

df.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# 29. 儲存性別分析
# ============================================================

gender_analysis.to_csv(
    GENDER_ANALYSIS_FILE,
    encoding="utf-8-sig"
)


# ============================================================
# 30. 儲存價格區間分析
# ============================================================

price_range_analysis.to_csv(
    PRICE_RANGE_ANALYSIS_FILE,
    encoding="utf-8-sig"
)


# ============================================================
# 31. 儲存性別 × 商品類型
# ============================================================

gender_category.to_csv(
    GENDER_CATEGORY_FILE,
    encoding="utf-8-sig"
)


# ============================================================
# 32. 儲存性別 × 商品類型平均價格
# ============================================================

gender_category_price.to_csv(
    GENDER_CATEGORY_PRICE_FILE,
    encoding="utf-8-sig"
)


# ============================================================
# 33. 儲存商品類型分析
# ============================================================

category_analysis.to_csv(
    CATEGORY_ANALYSIS_FILE,
    encoding="utf-8-sig"
)


# ============================================================
# 34. 完成
# ============================================================

print("========================================")
print("UNIQLO 資料分析完成")
print("========================================")
print()

print(
    "分析商品數量：",
    len(df),
    "件"
)

print(
    "商品類型數量：",
    df["category"].nunique(),
    "種"
)

print()

print("已產生以下檔案：")
print()

print(
    "1.",
    OUTPUT_FILE
)

print(
    "2.",
    GENDER_ANALYSIS_FILE
)

print(
    "3.",
    PRICE_RANGE_ANALYSIS_FILE
)

print(
    "4.",
    GENDER_CATEGORY_FILE
)

print(
    "5.",
    GENDER_CATEGORY_PRICE_FILE
)

print(
    "6.",
    CATEGORY_ANALYSIS_FILE
)

print()

print("UNIQLO 資料分析完成！")