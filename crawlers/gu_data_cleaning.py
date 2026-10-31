import pandas as pd
from pathlib import Path


# ============================================================
# 0. 專案路徑設定
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

RAW_DIR = BASE_DIR / "data" / "raw"
CLEANED_DIR = BASE_DIR / "data" / "cleaned"

# 新版 GU 爬蟲輸出的 RAW 資料
INPUT_FILE = RAW_DIR / "gu_products_raw.csv"

# 清理完成後輸出
OUTPUT_FILE = CLEANED_DIR / "gu_products_cleaned.csv"

CLEANED_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# 1. 開始
# ============================================================

print()
print("=" * 70)
print("GU 女裝商品資料清理")
print("=" * 70)
print()

print("正在讀取 GU RAW 商品資料...")
print("讀取位置：")
print(INPUT_FILE)
print()


# ============================================================
# 2. 檢查檔案
# ============================================================

if not INPUT_FILE.exists():

    print("找不到 GU RAW 商品資料！")
    print()
    print("請確認是否存在：")
    print(INPUT_FILE)

    raise FileNotFoundError(
        f"找不到檔案：{INPUT_FILE}"
    )


# ============================================================
# 3. 讀取資料
# ============================================================

df = pd.read_csv(
    INPUT_FILE,
    encoding="utf-8-sig"
)

print("資料讀取完成！")
print()


# ============================================================
# 4. 原始資料資訊
# ============================================================

print("=" * 70)
print("原始資料資訊")
print("=" * 70)
print()

print(
    "原始商品紀錄：",
    len(df),
    "筆"
)

print()

print("資料欄位：")
print(list(df.columns))

print()

print("缺失值：")
print(df.isnull().sum())

print()


# ============================================================
# 5. 檢查必要欄位
# ============================================================

required_columns = [
    "brand",
    "product_name",
    "product_id",
    "price",
    "product_url",
    "crawl_time",
    "source_category"
]

missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]

if missing_columns:

    raise ValueError(
        "GU RAW 資料缺少必要欄位："
        f"{missing_columns}"
    )


# ============================================================
# 6. 統一品牌名稱
# ============================================================

df["brand"] = "GU"


# ============================================================
# 7. 清理商品名稱
# ============================================================

print("=" * 70)
print("清理商品名稱")
print("=" * 70)
print()

before_count = len(df)

df["product_name"] = (
    df["product_name"]
    .fillna("")
    .astype(str)
    .str.strip()
)

invalid_names = [
    "",
    "GU台灣",
    "商品詳情 - GU台灣",
    "商品詳情-GU台灣"
]

df = df[
    ~df["product_name"].isin(
        invalid_names
    )
].copy()

removed_invalid_name = (
    before_count - len(df)
)

print(
    "移除無效商品名稱：",
    removed_invalid_name,
    "筆"
)

print()


# ============================================================
# 8. 清理商品 ID
# ============================================================

print("=" * 70)
print("清理商品 ID")
print("=" * 70)
print()

before_count = len(df)

df["product_id"] = (
    df["product_id"]
    .astype("string")
    .str.strip()
)

df["product_id"] = (
    df["product_id"]
    .replace(
        {
            "": pd.NA,
            "nan": pd.NA,
            "None": pd.NA,
            "<NA>": pd.NA
        }
    )
)

df = df.dropna(
    subset=["product_id"]
).copy()

# 359516.0 → 359516
df["product_id"] = (
    df["product_id"]
    .str.replace(
        r"\.0$",
        "",
        regex=True
    )
)

# 只保留商品編號數字
df["product_id"] = (
    df["product_id"]
    .str.extract(
        r"(\d+)",
        expand=False
    )
)

df = df.dropna(
    subset=["product_id"]
).copy()

removed_no_id = (
    before_count - len(df)
)

print(
    "移除無效商品 ID：",
    removed_no_id,
    "筆"
)

print()


# ============================================================
# 9. 清理價格
# ============================================================

print("=" * 70)
print("清理商品價格")
print("=" * 70)
print()

before_count = len(df)

df["price"] = pd.to_numeric(
    df["price"],
    errors="coerce"
)

df = df.dropna(
    subset=["price"]
).copy()

# 排除 0 元與負數價格
df = df[
    df["price"] > 0
].copy()

df["price"] = (
    df["price"]
    .astype(int)
)

removed_invalid_price = (
    before_count - len(df)
)

print(
    "移除無效價格：",
    removed_invalid_price,
    "筆"
)

print()


# ============================================================
# 10. 判斷商品性別
# ============================================================

print("=" * 70)
print("判斷商品性別")
print("=" * 70)
print()


def get_gender(product_name):

    name = str(product_name).strip()

    # 一定要先判斷男女適穿
    if "男女適穿" in name:
        return "男女適穿"

    if name.startswith("女裝"):
        return "女裝"

    if name.startswith("男裝"):
        return "男裝"

    return "其他"


df["gender"] = (
    df["product_name"]
    .apply(get_gender)
)

print("篩選前性別分布：")
print()

print(
    df["gender"]
    .value_counts()
)

print()


# ============================================================
# 11. 保留女裝 + 男女適穿
# ============================================================

print("=" * 70)
print("保留 GU 女裝與男女適穿商品")
print("=" * 70)
print()

before_count = len(df)

allowed_gender = [
    "女裝",
    "男女適穿"
]

df = df[
    df["gender"].isin(
        allowed_gender
    )
].copy()

removed_gender = (
    before_count - len(df)
)

print(
    "排除純男裝 / 其他：",
    removed_gender,
    "筆"
)

print()

print(
    "目前保留商品紀錄：",
    len(df),
    "筆"
)

print()

print("保留後性別分布：")
print(
    df["gender"]
    .value_counts()
)

print()


# ============================================================
# 12. 移除商品名稱前面的性別標籤
# ============================================================

df["product_name"] = (
    df["product_name"]
    .str.replace(
        r"^(女裝|男女適穿)[\s\-・:：]*",
        "",
        regex=True
    )
    .str.strip()
)


# ============================================================
# 13. 統一商品名稱格式
# ============================================================

# 全形Ｔ → 半形 T
df["product_name"] = (
    df["product_name"]
    .str.replace(
        "Ｔ",
        "T",
        regex=False
    )
)

# 全形空白 → 一般空白
df["product_name"] = (
    df["product_name"]
    .str.replace(
        "\u3000",
        " ",
        regex=False
    )
)

# 多個空白 → 單一空白
df["product_name"] = (
    df["product_name"]
    .str.replace(
        r"\s+",
        " ",
        regex=True
    )
    .str.strip()
)


# ============================================================
# 14. 重複商品檢查
# ============================================================

print("=" * 70)
print("重複商品檢查")
print("=" * 70)
print()

duplicate_mask = (
    df.duplicated(
        subset=["product_id"],
        keep=False
    )
)

duplicate_products = (
    df[
        duplicate_mask
    ]
    .sort_values(
        by=[
            "product_id",
            "price"
        ]
    )
)

if duplicate_products.empty:

    print("沒有重複商品。")

else:

    duplicate_id_count = (
        duplicate_products[
            "product_id"
        ]
        .nunique()
    )

    print(
        "發現重複商品 ID：",
        duplicate_id_count,
        "個"
    )

    print()

    print(
        duplicate_products[
            [
                "product_id",
                "product_name",
                "price",
                "source_category"
            ]
        ].to_string(
            index=False
        )
    )

print()


# ============================================================
# 15. 同商品不同價格檢查
# ============================================================

print("=" * 70)
print("同商品 ID 不同價格檢查")
print("=" * 70)
print()

price_nunique = (
    df.groupby(
        "product_id"
    )["price"]
    .nunique()
)

different_price_ids = (
    price_nunique[
        price_nunique > 1
    ]
    .index
)

different_price_products = (
    df[
        df["product_id"].isin(
            different_price_ids
        )
    ]
    .sort_values(
        by=[
            "product_id",
            "price"
        ]
    )
)

if different_price_products.empty:

    print(
        "沒有發現同商品 ID 不同價格。"
    )

else:

    print(
        "發現",
        len(different_price_ids),
        "個商品 ID 有不同價格。"
    )

    print()

    print(
        different_price_products[
            [
                "product_id",
                "product_name",
                "price",
                "source_category"
            ]
        ].to_string(
            index=False
        )
    )

print()


# ============================================================
# 16. 處理重複商品
# ============================================================

print("=" * 70)
print("處理重複商品")
print("=" * 70)
print()

before_count = len(df)

# 同一商品 ID 如果有不同價格
# 保留最低價格，視為目前優惠 / 售價
df = (
    df
    .sort_values(
        by=[
            "product_id",
            "price"
        ],
        ascending=[
            True,
            True
        ]
    )
    .drop_duplicates(
        subset=["product_id"],
        keep="first"
    )
    .copy()
)

removed_duplicates = (
    before_count - len(df)
)

print(
    "移除重複紀錄：",
    removed_duplicates,
    "筆"
)

print(
    "去重後商品數：",
    len(df),
    "件"
)

print()


# ============================================================
# 17. 商品分類函式
# ============================================================

def get_category(
    product_name,
    source_category
):

    name = str(product_name)
    source = str(source_category)

    name_upper = name.upper()

    # --------------------------------------------------------
    # 內衣
    # --------------------------------------------------------

    if (
        "內衣" in name
        or "BRA TOP" in name_upper
        or "BRATOP" in name_upper
        or "BRA FEEL" in name_upper
    ):
        return "內衣"

    # --------------------------------------------------------
    # 背心
    # --------------------------------------------------------

    if (
        "背心" in name
        or "坦克" in name
        or "CAMISOLE" in name_upper
    ):
        return "背心"

    # --------------------------------------------------------
    # POLO衫
    # --------------------------------------------------------

    if "POLO" in name_upper:
        return "POLO衫"

    # --------------------------------------------------------
    # 外套
    # 一定放在連帽前面
    # --------------------------------------------------------

    if (
        "外套" in name
        or "大衣" in name
        or "夾克" in name
        or "風衣" in name
        or "西裝外套" in name
        or "JACKET" in name_upper
        or "COAT" in name_upper
    ):
        return "外套"

    # --------------------------------------------------------
    # 襯衫
    # --------------------------------------------------------

    if (
        "襯衫" in name
        or "設計上衣" in name
        or "BLOUSE" in name_upper
        or "SHIRT" in name_upper
    ):
        return "襯衫"

    # --------------------------------------------------------
    # 連帽上衣
    # --------------------------------------------------------

    if (
        "連帽" in name
        or "HOODIE" in name_upper
    ):
        return "連帽上衣"

    # --------------------------------------------------------
    # 休閒上衣
    # --------------------------------------------------------

    if (
        "休閒上衣" in name
        or "休閒寬版上衣" in name
        or "休閒衫" in name
        or "SWEAT" in name_upper
    ):
        return "休閒上衣"

    # --------------------------------------------------------
    # T恤
    # --------------------------------------------------------

    if (
        "T恤" in name
        or "T-SHIRT" in name_upper
        or "TEE" in name_upper
    ):
        return "T恤"

    # --------------------------------------------------------
    # 針織
    # --------------------------------------------------------

    if (
        "針織" in name
        or "毛衣" in name
        or "KNIT" in name_upper
        or "CARDIGAN" in name_upper
    ):
        return "針織"

    # --------------------------------------------------------
    # 一般上衣 / TUNIC
    # --------------------------------------------------------

    if (
        "上衣" in name
        or "罩衫" in name
        or "TUNIC" in name_upper
    ):
        return "上衣"

    # --------------------------------------------------------
    # 商品名稱無法判斷
    # 使用 GU 網站來源分類輔助
    # --------------------------------------------------------

    if (
        "襯衫" in source
        or "設計上衣" in source
    ):
        return "襯衫"

    if (
        "針織" in source
        or "開襟外套" in source
    ):
        return "針織"

    if "外套" in source:
        return "外套"

    if (
        "T恤" in source
        or "背心" in source
        or "TUNIC" in source.upper()
    ):
        return "上衣"

    return "其他"


# ============================================================
# 18. 建立商品類型
# ============================================================

df["category"] = (
    df.apply(
        lambda row: get_category(
            row["product_name"],
            row["source_category"]
        ),
        axis=1
    )
)


# ============================================================
# 19. 建立價格區間
# ============================================================

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
# 20. 商品類型數量
# ============================================================

print("=" * 70)
print("商品類型數量")
print("=" * 70)
print()

category_count = (
    df["category"]
    .value_counts()
)

print(category_count)
print()


# ============================================================
# 21. 商品類型占比
# ============================================================

print("=" * 70)
print("商品類型占比")
print("=" * 70)
print()

category_share = (
    df["category"]
    .value_counts(
        normalize=True
    )
    .mul(100)
    .round(2)
)

for category, share in category_share.items():

    print(
        f"{category}：{share:.2f}%"
    )

print()


# ============================================================
# 22. 商品類型統計表
# ============================================================

print("=" * 70)
print("商品類型統計表")
print("=" * 70)
print()

category_summary = pd.DataFrame(
    {
        "商品數量": category_count,
        "商品占比": category_share
    }
)

print(category_summary)
print()


# ============================================================
# 23. 查看「其他」商品
# ============================================================

print("=" * 70)
print("被分類為「其他」的商品")
print("=" * 70)
print()

other_products = (
    df[
        df["category"] == "其他"
    ]
)

if other_products.empty:

    print(
        "沒有商品被分類為其他。"
    )

else:

    print(
        other_products[
            [
                "product_id",
                "product_name",
                "price",
                "source_category"
            ]
        ].to_string(
            index=False
        )
    )

print()


# ============================================================
# 24. 價格區間統計
# ============================================================

print("=" * 70)
print("價格區間統計")
print("=" * 70)
print()

price_order = [
    "200元以下",
    "200-399元",
    "400-599元",
    "600-799元",
    "800-999元",
    "1000元以上"
]

price_range_count = (
    df["price_range"]
    .value_counts()
    .reindex(
        price_order,
        fill_value=0
    )
)

price_range_share = (
    price_range_count
    / len(df)
    * 100
).round(2)

price_range_summary = pd.DataFrame(
    {
        "商品數量": price_range_count,
        "商品占比": price_range_share
    }
)

print(price_range_summary)
print()


# ============================================================
# 25. 整體價格統計
# ============================================================

print("=" * 70)
print("價格統計")
print("=" * 70)
print()

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

print(
    "平均價格：",
    round(
        df["price"].mean(),
        2
    ),
    "元"
)

print(
    "價格中位數：",
    df["price"].median(),
    "元"
)

print()


# ============================================================
# 26. 各商品類型平均價格
# ============================================================

print("=" * 70)
print("各商品類型平均價格")
print("=" * 70)
print()

category_avg_price = (
    df.groupby(
        "category"
    )["price"]
    .mean()
    .round(2)
    .sort_values(
        ascending=False
    )
)

print(category_avg_price)
print()


# ============================================================
# 27. 最便宜 10 件商品
# ============================================================

print("=" * 70)
print("最便宜的 10 件商品")
print("=" * 70)
print()

cheapest = (
    df.sort_values(
        by="price",
        ascending=True
    )
    .head(10)
)

print(
    cheapest[
        [
            "gender",
            "category",
            "product_name",
            "price"
        ]
    ].to_string(
        index=False
    )
)

print()


# ============================================================
# 28. 最貴 10 件商品
# ============================================================

print("=" * 70)
print("最貴的 10 件商品")
print("=" * 70)
print()

most_expensive = (
    df.sort_values(
        by="price",
        ascending=False
    )
    .head(10)
)

print(
    most_expensive[
        [
            "gender",
            "category",
            "product_name",
            "price"
        ]
    ].to_string(
        index=False
    )
)

print()


# ============================================================
# 29. 整理最終欄位
# ============================================================

final_columns = [
    "brand",
    "product_name",
    "product_id",
    "price",
    "product_url",
    "crawl_time",
    "source_category",
    "gender",
    "category",
    "price_range"
]

df = df[
    final_columns
].copy()


# ============================================================
# 30. 商品 ID 排序
# ============================================================

# 用數字版本輔助排序
df["_product_id_number"] = pd.to_numeric(
    df["product_id"],
    errors="coerce"
)

df = (
    df.sort_values(
        by="_product_id_number"
    )
    .drop(
        columns=["_product_id_number"]
    )
    .reset_index(
        drop=True
    )
)


# ============================================================
# 31. 最終資料檢查
# ============================================================

print("=" * 70)
print("最終資料檢查")
print("=" * 70)
print()

print(
    "最終商品數：",
    len(df),
    "件"
)

print(
    "女裝商品：",
    (df["gender"] == "女裝").sum(),
    "件"
)

print(
    "男女適穿商品：",
    (df["gender"] == "男女適穿").sum(),
    "件"
)

print(
    "重複商品 ID：",
    df["product_id"]
    .duplicated()
    .sum(),
    "件"
)

print(
    "缺失商品 ID：",
    df["product_id"]
    .isna()
    .sum(),
    "件"
)

print(
    "缺失價格：",
    df["price"]
    .isna()
    .sum(),
    "件"
)

print(
    "其他分類：",
    (
        df["category"] == "其他"
    ).sum(),
    "件"
)

print()


# ============================================================
# 32. 清理後資料預覽
# ============================================================

print("=" * 70)
print("清理後前 20 筆資料")
print("=" * 70)
print()

print(
    df[
        [
            "brand",
            "gender",
            "category",
            "source_category",
            "product_name",
            "product_id",
            "price",
            "price_range"
        ]
    ]
    .head(20)
    .to_string(
        index=False
    )
)

print()


# ============================================================
# 33. 儲存 CSV
# ============================================================

df.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# 34. 完成
# ============================================================

print("=" * 70)
print("GU 資料清理完成")
print("=" * 70)
print()

print(
    "清理後商品數量：",
    len(df),
    "件"
)

print(
    "女裝商品數量：",
    (df["gender"] == "女裝").sum(),
    "件"
)

print(
    "男女適穿商品數量：",
    (df["gender"] == "男女適穿").sum(),
    "件"
)

print(
    "商品類型數量：",
    df["category"].nunique(),
    "種"
)

print(
    "其他商品數量：",
    (
        df["category"] == "其他"
    ).sum(),
    "件"
)

print()

print("資料已儲存：")
print(OUTPUT_FILE)

print()
print("GU 資料清理完成！")