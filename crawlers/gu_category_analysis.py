import pandas as pd
from pathlib import Path


# ============================================================
# 0. 設定專案路徑
# ============================================================

# 目前程式位置：
# fashion_crawler/crawlers/gu_category_analysis.py

BASE_DIR = Path(__file__).resolve().parent.parent

CLEANED_DIR = BASE_DIR / "data" / "cleaned"
ANALYSIS_DIR = BASE_DIR / "data" / "analysis"

# 如果 analysis 資料夾不存在，自動建立
ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)

# 輸入檔案
INPUT_FILE = CLEANED_DIR / "gu_products_cleaned.csv"

# 輸出檔案
CATEGORY_OUTPUT = ANALYSIS_DIR / "gu_category_analysis.csv"
GENDER_CATEGORY_OUTPUT = ANALYSIS_DIR / "gu_gender_category.csv"
GENDER_CATEGORY_PRICE_OUTPUT = ANALYSIS_DIR / "gu_gender_category_price.csv"


# ============================================================
# 1. 讀取 GU 清理後資料
# ============================================================

print("正在讀取 GU 清理後資料...")
print("讀取位置：", INPUT_FILE)
print()

df = pd.read_csv(
    INPUT_FILE,
    encoding="utf-8-sig"
)

print("資料讀取完成！")
print()


# ============================================================
# 2. 查看資料基本資訊
# ============================================================

print("========================================")
print("GU 商品類型分析")
print("========================================")
print()

print("商品總數：", len(df))
print("商品類型：", df["category"].nunique(), "種")

print()


# ============================================================
# 3. 各商品類型數量
# ============================================================

print("========================================")
print("各商品類型數量")
print("========================================")

category_count = (
    df["category"]
    .value_counts()
)

print(category_count)

print()


# ============================================================
# 4. 各商品類型平均價格
# ============================================================

print("========================================")
print("各商品類型平均價格")
print("========================================")

category_avg_price = (
    df.groupby("category")["price"]
    .mean()
    .round(2)
    .sort_values()
)

print(category_avg_price)

print()


# ============================================================
# 5. 各商品類型最低價格
# ============================================================

print("========================================")
print("各商品類型最低價格")
print("========================================")

category_min_price = (
    df.groupby("category")["price"]
    .min()
    .sort_values()
)

print(category_min_price)

print()


# ============================================================
# 6. 各商品類型最高價格
# ============================================================

print("========================================")
print("各商品類型最高價格")
print("========================================")

category_max_price = (
    df.groupby("category")["price"]
    .max()
    .sort_values()
)

print(category_max_price)

print()


# ============================================================
# 7. 建立商品類型統計表
# ============================================================

print("========================================")
print("商品類型統計表")
print("========================================")

category_analysis = (
    df.groupby("category")
    .agg(
        商品數量=("product_id", "count"),
        平均價格=("price", "mean"),
        最低價格=("price", "min"),
        最高價格=("price", "max")
    )
)

category_analysis["平均價格"] = (
    category_analysis["平均價格"]
    .round(2)
)

category_analysis = (
    category_analysis
    .sort_values(
        by="商品數量",
        ascending=False
    )
)

print(category_analysis)

print()


# ============================================================
# 8. 男女裝 × 商品類型
# ============================================================

print("========================================")
print("男女裝 × 商品類型")
print("========================================")

gender_category = pd.crosstab(
    df["category"],
    df["gender"]
)

print(gender_category)

print()


# ============================================================
# 9. 男女裝 × 商品類型平均價格
# ============================================================

print("========================================")
print("男女裝 × 商品類型平均價格")
print("========================================")

gender_category_price = pd.pivot_table(
    df,
    values="price",
    index="category",
    columns="gender",
    aggfunc="mean"
)

gender_category_price = (
    gender_category_price
    .round(2)
)

print(gender_category_price)

print()


# ============================================================
# 10. 找出每個類型最便宜的商品
# ============================================================

print("========================================")
print("各類型最便宜商品")
print("========================================")

cheapest_index = (
    df.groupby("category")["price"]
    .idxmin()
)

cheapest_by_category = (
    df.loc[
        cheapest_index,
        [
            "category",
            "gender",
            "product_name",
            "price"
        ]
    ]
    .sort_values("category")
)

print(
    cheapest_by_category.to_string(
        index=False
    )
)

print()


# ============================================================
# 11. 找出每個類型最貴的商品
# ============================================================

print("========================================")
print("各類型最貴商品")
print("========================================")

expensive_index = (
    df.groupby("category")["price"]
    .idxmax()
)

expensive_by_category = (
    df.loc[
        expensive_index,
        [
            "category",
            "gender",
            "product_name",
            "price"
        ]
    ]
    .sort_values("category")
)

print(
    expensive_by_category.to_string(
        index=False
    )
)

print()


# ============================================================
# 12. 儲存商品類型分析
# ============================================================

category_analysis.to_csv(
    CATEGORY_OUTPUT,
    encoding="utf-8-sig"
)


# ============================================================
# 13. 儲存男女裝 × 商品類型數量
# ============================================================

gender_category.to_csv(
    GENDER_CATEGORY_OUTPUT,
    encoding="utf-8-sig"
)


# ============================================================
# 14. 儲存男女裝 × 商品類型平均價格
# ============================================================

gender_category_price.to_csv(
    GENDER_CATEGORY_PRICE_OUTPUT,
    encoding="utf-8-sig"
)


# ============================================================
# 15. 完成
# ============================================================

print("========================================")
print("GU 商品類型分析完成")
print("========================================")
print()

print("已產生以下檔案：")
print()

print("1.", CATEGORY_OUTPUT)
print("2.", GENDER_CATEGORY_OUTPUT)
print("3.", GENDER_CATEGORY_PRICE_OUTPUT)

print()
print("分析完成！")