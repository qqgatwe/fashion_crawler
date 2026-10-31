import pandas as pd
from pathlib import Path


# ============================================================
# 0. 專案路徑設定
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

CLEANED_DIR = BASE_DIR / "data" / "cleaned"
ANALYSIS_DIR = BASE_DIR / "data" / "analysis"

ANALYSIS_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# 1. 檔案路徑
# ============================================================

GU_FILE = (
    CLEANED_DIR /
    "gu_products_cleaned.csv"
)

UNIQLO_FILE = (
    CLEANED_DIR /
    "uniqlo_products_cleaned.csv"
)


# 輸出檔案

COMBINED_FILE = (
    ANALYSIS_DIR /
    "brand_products_combined.csv"
)

BRAND_COMPARISON_FILE = (
    ANALYSIS_DIR /
    "brand_comparison.csv"
)

PRICE_RANGE_FILE = (
    ANALYSIS_DIR /
    "brand_price_range_comparison.csv"
)

CATEGORY_COUNT_FILE = (
    ANALYSIS_DIR /
    "brand_category_count.csv"
)

CATEGORY_SHARE_FILE = (
    ANALYSIS_DIR /
    "brand_category_share.csv"
)

CATEGORY_PRICE_FILE = (
    ANALYSIS_DIR /
    "brand_category_price.csv"
)

COMMON_CATEGORY_FILE = (
    ANALYSIS_DIR /
    "brand_common_category_comparison.csv"
)


# ============================================================
# 2. 讀取 GU 與 UNIQLO
# ============================================================

print("正在讀取 GU 與 UNIQLO 商品資料...")
print()

print("GU 讀取位置：")
print(GU_FILE)
print()

print("UNIQLO 讀取位置：")
print(UNIQLO_FILE)
print()


gu_df = pd.read_csv(
    GU_FILE,
    encoding="utf-8-sig"
)

uniqlo_df = pd.read_csv(
    UNIQLO_FILE,
    encoding="utf-8-sig"
)


print("資料讀取完成！")
print()


# ============================================================
# 3. 原始商品數量
# ============================================================

print("========================================")
print("原始商品數量")
print("========================================")
print()

print(
    "GU：",
    len(gu_df),
    "件"
)

print(
    "UNIQLO：",
    len(uniqlo_df),
    "件"
)

print()


# ============================================================
# 4. 確保品牌名稱正確
# ============================================================

gu_df["brand"] = "GU"

uniqlo_df["brand"] = "UNIQLO"


# ============================================================
# 5. 確保價格是數字
# ============================================================

gu_df["price"] = pd.to_numeric(
    gu_df["price"],
    errors="coerce"
)

uniqlo_df["price"] = pd.to_numeric(
    uniqlo_df["price"],
    errors="coerce"
)


# ============================================================
# 6. 移除價格缺失資料
# ============================================================

gu_df = gu_df.dropna(
    subset=["price"]
)

uniqlo_df = uniqlo_df.dropna(
    subset=["price"]
)


# ============================================================
# 7. 價格轉成整數
# ============================================================

gu_df["price"] = (
    gu_df["price"]
    .astype(int)
)

uniqlo_df["price"] = (
    uniqlo_df["price"]
    .astype(int)
)


# ============================================================
# 8. 合併 GU + UNIQLO
# ============================================================

df = pd.concat(
    [
        gu_df,
        uniqlo_df
    ],
    ignore_index=True,
    sort=False
)


print("========================================")
print("合併資料")
print("========================================")
print()

print(
    "合併後商品總數：",
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
# 9. 重新建立統一價格區間
# ============================================================

# 這裡非常重要
#
# 不使用 GU / UNIQLO 原本的 price_range
#
# 而是兩個品牌全部重新按照同一套規則分類
#
# 這樣就不會出現：
#
# GU = 0
# GU 占比 = NaN
#
# 的問題


def get_price_range(price):

    if price < 200:

        return "200元以下"

    elif price < 400:

        return "200-399元"

    elif price < 600:

        return "400-599元"

    elif price < 800:

        return "600-799元"

    elif price < 1000:

        return "800-999元"

    else:

        return "1000元以上"


df["price_range"] = (
    df["price"]
    .apply(
        get_price_range
    )
)


# ============================================================
# 10. 價格區間順序
# ============================================================

price_order = [

    "200元以下",

    "200-399元",

    "400-599元",

    "600-799元",

    "800-999元",

    "1000元以上"

]


# ============================================================
# 11. 各品牌商品數量
# ============================================================

brand_count = (
    df["brand"]
    .value_counts()
    .reindex(
        [
            "GU",
            "UNIQLO"
        ],
        fill_value=0
    )
)


print("========================================")
print("各品牌商品數量")
print("========================================")
print()

print(
    brand_count
)

print()


# ============================================================
# 12. 品牌整體價格統計
# ============================================================

brand_price_summary = (
    df.groupby("brand")
    .agg(

        商品數量=(
            "product_name",
            "count"
        ),

        平均價格=(
            "price",
            "mean"
        ),

        中位數價格=(
            "price",
            "median"
        ),

        最低價格=(
            "price",
            "min"
        ),

        最高價格=(
            "price",
            "max"
        )

    )
)


brand_price_summary = (
    brand_price_summary
    .reindex(
        [
            "GU",
            "UNIQLO"
        ]
    )
)


brand_price_summary[
    "平均價格"
] = (
    brand_price_summary[
        "平均價格"
    ]
    .round(2)
)


brand_price_summary[
    "中位數價格"
] = (
    brand_price_summary[
        "中位數價格"
    ]
    .round(2)
)


print("========================================")
print("品牌整體價格統計")
print("========================================")
print()

print(
    brand_price_summary
)

print()


# ============================================================
# 13. 品牌 × 價格區間商品數量
# ============================================================

price_range_count = pd.crosstab(

    df["price_range"],

    df["brand"]

)


price_range_count = (
    price_range_count
    .reindex(
        price_order,
        fill_value=0
    )
)


price_range_count = (
    price_range_count
    .reindex(
        columns=[
            "GU",
            "UNIQLO"
        ],
        fill_value=0
    )
)


print("========================================")
print("品牌 × 價格區間商品數量")
print("========================================")
print()

print(
    price_range_count
)

print()


# ============================================================
# 14. 品牌 × 價格區間占比
# ============================================================

price_range_share = (
    price_range_count
    .div(
        price_range_count.sum(
            axis=0
        ),
        axis=1
    )
    * 100
)


price_range_share = (
    price_range_share
    .round(2)
)


print("========================================")
print("品牌 × 價格區間占比")
print("========================================")
print()

print(
    price_range_share
)

print()


# ============================================================
# 15. 建立價格區間完整比較表
# ============================================================

price_range_comparison = (
    pd.DataFrame(
        index=price_order
    )
)


price_range_comparison[
    "GU商品數量"
] = (
    price_range_count["GU"]
)


price_range_comparison[
    "GU商品占比"
] = (
    price_range_share["GU"]
)


price_range_comparison[
    "UNIQLO商品數量"
] = (
    price_range_count["UNIQLO"]
)


price_range_comparison[
    "UNIQLO商品占比"
] = (
    price_range_share["UNIQLO"]
)


print("========================================")
print("價格區間完整比較表")
print("========================================")
print()

print(
    price_range_comparison
)

print()


# ============================================================
# 16. 品牌 × 商品類型數量
# ============================================================

category_count = pd.crosstab(

    df["category"],

    df["brand"]

)


category_count = (
    category_count
    .reindex(
        columns=[
            "GU",
            "UNIQLO"
        ],
        fill_value=0
    )
)


# 按照兩品牌商品總數排序

category_count[
    "總數"
] = (
    category_count["GU"]
    +
    category_count["UNIQLO"]
)


category_count = (
    category_count
    .sort_values(
        "總數",
        ascending=False
    )
)


category_count = (
    category_count
    .drop(
        columns=[
            "總數"
        ]
    )
)


print("========================================")
print("品牌 × 商品類型數量")
print("========================================")
print()

print(
    category_count
)

print()


# ============================================================
# 17. 品牌 × 商品類型占比
# ============================================================

category_share = (
    category_count
    .div(
        category_count.sum(
            axis=0
        ),
        axis=1
    )
    * 100
)


category_share = (
    category_share
    .round(2)
)


print("========================================")
print("品牌 × 商品類型占比")
print("========================================")
print()

print(
    category_share
)

print()


# ============================================================
# 18. 品牌 × 商品類型平均價格
# ============================================================

category_price = pd.pivot_table(

    df,

    values="price",

    index="category",

    columns="brand",

    aggfunc="mean"

)


category_price = (
    category_price
    .reindex(
        category_count.index
    )
)


category_price = (
    category_price
    .reindex(
        columns=[
            "GU",
            "UNIQLO"
        ]
    )
)


category_price = (
    category_price
    .round(2)
)


print("========================================")
print("品牌 × 商品類型平均價格")
print("========================================")
print()

print(
    category_price
)

print()


# ============================================================
# 19. 找出兩品牌共同商品類型
# ============================================================

gu_categories = set(

    df[
        df["brand"] == "GU"
    ]["category"]

)


uniqlo_categories = set(

    df[
        df["brand"] == "UNIQLO"
    ]["category"]

)


common_categories = [

    category

    for category
    in category_count.index

    if (
        category in gu_categories
        and
        category in uniqlo_categories
    )

]


print("========================================")
print("兩品牌共同商品類型")
print("========================================")
print()

print(
    common_categories
)

print()


# ============================================================
# 20. 共同商品類型完整比較
# ============================================================

common_category_comparison = (
    pd.DataFrame(
        index=common_categories
    )
)


common_category_comparison[
    "GU商品數量"
] = (
    category_count
    .loc[
        common_categories,
        "GU"
    ]
)


common_category_comparison[
    "GU商品占比"
] = (
    category_share
    .loc[
        common_categories,
        "GU"
    ]
)


common_category_comparison[
    "GU平均價格"
] = (
    category_price
    .loc[
        common_categories,
        "GU"
    ]
)


common_category_comparison[
    "UNIQLO商品數量"
] = (
    category_count
    .loc[
        common_categories,
        "UNIQLO"
    ]
)


common_category_comparison[
    "UNIQLO商品占比"
] = (
    category_share
    .loc[
        common_categories,
        "UNIQLO"
    ]
)


common_category_comparison[
    "UNIQLO平均價格"
] = (
    category_price
    .loc[
        common_categories,
        "UNIQLO"
    ]
)


# ============================================================
# 21. 計算商品占比差
# ============================================================

common_category_comparison[
    "商品占比差"
] = (

    common_category_comparison[
        "GU商品占比"
    ]

    -

    common_category_comparison[
        "UNIQLO商品占比"
    ]

).round(2)


# ============================================================
# 22. 計算平均價格差
# ============================================================

common_category_comparison[
    "平均價格差"
] = (

    common_category_comparison[
        "GU平均價格"
    ]

    -

    common_category_comparison[
        "UNIQLO平均價格"
    ]

).round(2)


print("========================================")
print("共同商品類型完整比較")
print("========================================")
print()

print(
    common_category_comparison
)

print()


# ============================================================
# 23. 共同商品類型占比比較
# ============================================================

print("========================================")
print("共同商品類型占比比較")
print("========================================")
print()


for category in common_categories:

    gu_share = (
        category_share
        .loc[
            category,
            "GU"
        ]
    )

    uniqlo_share = (
        category_share
        .loc[
            category,
            "UNIQLO"
        ]
    )

    print(
        f"{category}："
        f"GU {gu_share:.2f}%"
        f" | "
        f"UNIQLO {uniqlo_share:.2f}%"
    )


print()


# ============================================================
# 24. 各品牌主要商品類型
# ============================================================

gu_main_category = (
    category_share["GU"]
    .idxmax()
)

gu_main_share = (
    category_share["GU"]
    .max()
)


uniqlo_main_category = (
    category_share["UNIQLO"]
    .idxmax()
)

uniqlo_main_share = (
    category_share["UNIQLO"]
    .max()
)


print("========================================")
print("各品牌主要商品類型")
print("========================================")
print()


print(
    "GU：",
    gu_main_category,
    f"({gu_main_share:.2f}%)"
)


print(
    "UNIQLO：",
    uniqlo_main_category,
    f"({uniqlo_main_share:.2f}%)"
)


print()


# ============================================================
# 25. 各品牌最便宜商品
# ============================================================

cheapest_products = (

    df.sort_values(
        "price"
    )

    .groupby(
        "brand",
        as_index=False
    )

    .first()

)


cheapest_products = (

    cheapest_products[
        [
            "brand",
            "gender",
            "category",
            "product_name",
            "price"
        ]
    ]

)


print("========================================")
print("各品牌最便宜商品")
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
# 26. 各品牌最貴商品
# ============================================================

most_expensive_products = (

    df.sort_values(
        "price",
        ascending=False
    )

    .groupby(
        "brand",
        as_index=False
    )

    .first()

)


most_expensive_products = (

    most_expensive_products[
        [
            "brand",
            "gender",
            "category",
            "product_name",
            "price"
        ]
    ]

)


print("========================================")
print("各品牌最貴商品")
print("========================================")
print()

print(
    most_expensive_products
    .to_string(
        index=False
    )
)

print()


# ============================================================
# 27. 品牌價格定位比較
# ============================================================

gu_avg_price = (
    df[
        df["brand"] == "GU"
    ]["price"]
    .mean()
)


uniqlo_avg_price = (
    df[
        df["brand"] == "UNIQLO"
    ]["price"]
    .mean()
)


price_difference = abs(
    gu_avg_price
    -
    uniqlo_avg_price
)


print("========================================")
print("品牌價格定位比較")
print("========================================")
print()


print(
    f"GU 平均價格："
    f"{gu_avg_price:.2f} 元"
)


print(
    f"UNIQLO 平均價格："
    f"{uniqlo_avg_price:.2f} 元"
)


print(
    f"平均價格差："
    f"{price_difference:.2f} 元"
)


if gu_avg_price < uniqlo_avg_price:

    print(
        "整體而言，"
        "GU 的平均商品價格較低。"
    )

elif gu_avg_price > uniqlo_avg_price:

    print(
        "整體而言，"
        "UNIQLO 的平均商品價格較低。"
    )

else:

    print(
        "兩品牌平均商品價格相同。"
    )


print()


# ============================================================
# 28. 商品結構比較
# ============================================================

print("========================================")
print("商品結構比較")
print("========================================")
print()


print(
    f"GU 最大商品類型為 "
    f"{gu_main_category}，"
    f"占 GU 全部商品 "
    f"{gu_main_share:.2f}%。"
)


print(
    f"UNIQLO 最大商品類型為 "
    f"{uniqlo_main_category}，"
    f"占 UNIQLO 全部商品 "
    f"{uniqlo_main_share:.2f}%。"
)


print()


# ============================================================
# 29. 價格區間結構比較
# ============================================================

gu_main_price_range = (
    price_range_share["GU"]
    .idxmax()
)

gu_main_price_share = (
    price_range_share["GU"]
    .max()
)


uniqlo_main_price_range = (
    price_range_share["UNIQLO"]
    .idxmax()
)

uniqlo_main_price_share = (
    price_range_share["UNIQLO"]
    .max()
)


print("========================================")
print("價格區間結構比較")
print("========================================")
print()


print(
    f"GU 最大價格區間為 "
    f"{gu_main_price_range}，"
    f"占 GU 商品 "
    f"{gu_main_price_share:.2f}%。"
)


print(
    f"UNIQLO 最大價格區間為 "
    f"{uniqlo_main_price_range}，"
    f"占 UNIQLO 商品 "
    f"{uniqlo_main_price_share:.2f}%。"
)


print()


# ============================================================
# 30. 儲存合併商品資料
# ============================================================

df.to_csv(

    COMBINED_FILE,

    index=False,

    encoding="utf-8-sig"

)


# ============================================================
# 31. 儲存品牌價格統計
# ============================================================

brand_price_summary.to_csv(

    BRAND_COMPARISON_FILE,

    encoding="utf-8-sig"

)


# ============================================================
# 32. 儲存價格區間比較
# ============================================================

price_range_comparison.to_csv(

    PRICE_RANGE_FILE,

    encoding="utf-8-sig"

)


# ============================================================
# 33. 儲存商品類型數量
# ============================================================

category_count.to_csv(

    CATEGORY_COUNT_FILE,

    encoding="utf-8-sig"

)


# ============================================================
# 34. 儲存商品類型占比
# ============================================================

category_share.to_csv(

    CATEGORY_SHARE_FILE,

    encoding="utf-8-sig"

)


# ============================================================
# 35. 儲存商品類型平均價格
# ============================================================

category_price.to_csv(

    CATEGORY_PRICE_FILE,

    encoding="utf-8-sig"

)


# ============================================================
# 36. 儲存共同商品類型比較
# ============================================================

common_category_comparison.to_csv(

    COMMON_CATEGORY_FILE,

    encoding="utf-8-sig"

)


# ============================================================
# 37. 完成
# ============================================================

print("========================================")
print("GU vs UNIQLO 品牌比較完成")
print("========================================")
print()


print(
    "GU 商品數量：",
    len(gu_df),
    "件"
)


print(
    "UNIQLO 商品數量：",
    len(uniqlo_df),
    "件"
)


print(
    "合併商品數量：",
    len(df),
    "件"
)


print()

print(
    "共同商品類型數量：",
    len(common_categories),
    "種"
)


print()

print(
    "GU 主要商品類型：",
    gu_main_category,
    f"({gu_main_share:.2f}%)"
)


print(
    "UNIQLO 主要商品類型：",
    uniqlo_main_category,
    f"({uniqlo_main_share:.2f}%)"
)


print()

print(
    "GU 主要價格區間：",
    gu_main_price_range,
    f"({gu_main_price_share:.2f}%)"
)


print(
    "UNIQLO 主要價格區間：",
    uniqlo_main_price_range,
    f"({uniqlo_main_price_share:.2f}%)"
)


print()

print("已產生以下檔案：")
print()

print(
    "1.",
    COMBINED_FILE
)

print(
    "2.",
    BRAND_COMPARISON_FILE
)

print(
    "3.",
    PRICE_RANGE_FILE
)

print(
    "4.",
    CATEGORY_COUNT_FILE
)

print(
    "5.",
    CATEGORY_SHARE_FILE
)

print(
    "6.",
    CATEGORY_PRICE_FILE
)

print(
    "7.",
    COMMON_CATEGORY_FILE
)

print()

print("品牌比較分析完成！")