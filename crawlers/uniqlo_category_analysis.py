import pandas as pd
from pathlib import Path


# ============================================================
# 0. 專案路徑設定
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

ANALYSIS_DIR = BASE_DIR / "data" / "analysis"

INPUT_FILE = (
    ANALYSIS_DIR /
    "uniqlo_products_analysis.csv"
)

OUTPUT_FILE = (
    ANALYSIS_DIR /
    "uniqlo_category_analysis.csv"
)


# ============================================================
# 1. 讀取 UNIQLO 分析資料
# ============================================================

print("正在讀取 UNIQLO 分析資料...")
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
# 2. 基本資料確認
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
# 3. 商品類型數量
# ============================================================

category_count = (
    df["category"]
    .value_counts()
)

print("========================================")
print("商品類型數量")
print("========================================")
print()

print(category_count)

print()


# ============================================================
# 4. 商品類型占比
# ============================================================

category_percentage = (
    df["category"]
    .value_counts(
        normalize=True
    )
    .mul(100)
    .round(2)
)

print("========================================")
print("商品類型占比")
print("========================================")
print()

for category, percentage in category_percentage.items():

    print(
        f"{category}："
        f"{percentage:.2f}%"
    )

print()


# ============================================================
# 5. 各商品類型平均價格
# ============================================================

category_avg_price = (
    df.groupby("category")["price"]
    .mean()
    .round(2)
)

print("========================================")
print("各商品類型平均價格")
print("========================================")
print()

print(category_avg_price)

print()


# ============================================================
# 6. 各商品類型中位數價格
# ============================================================

category_median_price = (
    df.groupby("category")["price"]
    .median()
    .round(2)
)

print("========================================")
print("各商品類型中位數價格")
print("========================================")
print()

print(category_median_price)

print()


# ============================================================
# 7. 各商品類型最低價格
# ============================================================

category_min_price = (
    df.groupby("category")["price"]
    .min()
)

print("========================================")
print("各商品類型最低價格")
print("========================================")
print()

print(category_min_price)

print()


# ============================================================
# 8. 各商品類型最高價格
# ============================================================

category_max_price = (
    df.groupby("category")["price"]
    .max()
)

print("========================================")
print("各商品類型最高價格")
print("========================================")
print()

print(category_max_price)

print()


# ============================================================
# 9. 建立商品類型完整分析表
# ============================================================

category_analysis = pd.DataFrame({

    "商品數量":
        category_count,

    "商品占比":
        category_percentage,

    "平均價格":
        category_avg_price,

    "中位數價格":
        category_median_price,

    "最低價格":
        category_min_price,

    "最高價格":
        category_max_price

})


# ============================================================
# 10. 按商品數量排序
# ============================================================

category_analysis = (
    category_analysis
    .sort_values(
        by="商品數量",
        ascending=False
    )
)


print("========================================")
print("商品類型完整分析表")
print("========================================")
print()

print(category_analysis)

print()


# ============================================================
# 11. 商品類型占比排名
# ============================================================

print("========================================")
print("商品類型占比排名")
print("========================================")
print()

for rank, (
    category,
    row
) in enumerate(
    category_analysis.iterrows(),
    start=1
):

    print(
        f"{rank}. "
        f"{category}："
        f"{int(row['商品數量'])} 件 "
        f"({row['商品占比']:.2f}%)"
    )

print()


# ============================================================
# 12. 找出商品數量最多的類型
# ============================================================

largest_category = (
    category_analysis
    .iloc[0]
)

largest_category_name = (
    category_analysis
    .index[0]
)

print("========================================")
print("主要商品類型")
print("========================================")
print()

print(
    "商品類型：",
    largest_category_name
)

print(
    "商品數量：",
    int(
        largest_category["商品數量"]
    ),
    "件"
)

print(
    "商品占比：",
    f"{largest_category['商品占比']:.2f}%"
)

print()


# ============================================================
# 13. 找出平均價格最高的商品類型
# ============================================================

highest_avg_category = (
    category_analysis[
        "平均價格"
    ]
    .idxmax()
)

highest_avg_price = (
    category_analysis.loc[
        highest_avg_category,
        "平均價格"
    ]
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
    f"{highest_avg_price:.2f}",
    "元"
)

print()


# ============================================================
# 14. 找出平均價格最低的商品類型
# ============================================================

lowest_avg_category = (
    category_analysis[
        "平均價格"
    ]
    .idxmin()
)

lowest_avg_price = (
    category_analysis.loc[
        lowest_avg_category,
        "平均價格"
    ]
)

print("========================================")
print("平均價格最低的商品類型")
print("========================================")
print()

print(
    "商品類型：",
    lowest_avg_category
)

print(
    "平均價格：",
    f"{lowest_avg_price:.2f}",
    "元"
)

print()


# ============================================================
# 15. 找出各類型最便宜商品
# ============================================================

cheapest_index = (
    df.groupby("category")["price"]
    .idxmin()
)

cheapest_products = (
    df.loc[
        cheapest_index,
        [
            "category",
            "product_name",
            "price"
        ]
    ]
    .sort_values(
        by="category"
    )
)

print("========================================")
print("各商品類型最便宜商品")
print("========================================")
print()

print(
    cheapest_products
    .to_string(
        index=False
    )
)

print()


# ============================================================
# 16. 找出各類型最貴商品
# ============================================================

expensive_index = (
    df.groupby("category")["price"]
    .idxmax()
)

expensive_products = (
    df.loc[
        expensive_index,
        [
            "category",
            "product_name",
            "price"
        ]
    ]
    .sort_values(
        by="category"
    )
)

print("========================================")
print("各商品類型最貴商品")
print("========================================")
print()

print(
    expensive_products
    .to_string(
        index=False
    )
)

print()


# ============================================================
# 17. 價格區間 × 商品類型
# ============================================================

price_order = [
    "200元以下",
    "200-399元",
    "400-599元",
    "600-799元",
    "800-999元",
    "1000元以上"
]

category_price_range = pd.crosstab(
    df["category"],
    df["price_range"]
)

category_price_range = (
    category_price_range
    .reindex(
        columns=price_order,
        fill_value=0
    )
)

# 依商品數量排序
category_order = (
    category_analysis.index
)

category_price_range = (
    category_price_range
    .reindex(
        category_order,
        fill_value=0
    )
)


print("========================================")
print("商品類型 × 價格區間")
print("========================================")
print()

print(category_price_range)

print()


# ============================================================
# 18. 商品類型價格差距
# ============================================================

category_analysis[
    "價格差距"
] = (
    category_analysis["最高價格"]
    -
    category_analysis["最低價格"]
)

print("========================================")
print("商品類型價格差距")
print("========================================")
print()

print(
    category_analysis[
        [
            "最低價格",
            "最高價格",
            "價格差距"
        ]
    ]
)

print()


# ============================================================
# 19. 儲存商品類型分析表
# ============================================================

category_analysis.to_csv(
    OUTPUT_FILE,
    encoding="utf-8-sig"
)


# ============================================================
# 20. 額外儲存價格區間 × 商品類型
# ============================================================

PRICE_RANGE_OUTPUT_FILE = (
    ANALYSIS_DIR /
    "uniqlo_category_price_range.csv"
)

category_price_range.to_csv(
    PRICE_RANGE_OUTPUT_FILE,
    encoding="utf-8-sig"
)


# ============================================================
# 21. 完成
# ============================================================

print("========================================")
print("UNIQLO 商品類型分析完成")
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

print(
    "主要商品類型：",
    largest_category_name
)

print(
    "主要商品類型占比：",
    f"{largest_category['商品占比']:.2f}%"
)

print()

print(
    "平均價格最高類型：",
    highest_avg_category
)

print(
    "平均價格：",
    f"{highest_avg_price:.2f}",
    "元"
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
    PRICE_RANGE_OUTPUT_FILE
)

print()

print("UNIQLO 商品類型分析完成！")