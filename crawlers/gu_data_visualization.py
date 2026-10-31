import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


# ============================================================
# 0. 設定專案路徑
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

ANALYSIS_DIR = BASE_DIR / "data" / "analysis"
OUTPUT_DIR = BASE_DIR / "outputs"

# 如果 outputs 資料夾不存在，自動建立
OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

# 輸入檔案
INPUT_FILE = (
    ANALYSIS_DIR /
    "gu_products_analysis.csv"
)


# ============================================================
# 1. 讀取 GU 分析資料
# ============================================================

print("正在讀取 GU 分析資料...")
print("讀取位置：", INPUT_FILE)
print()

df = pd.read_csv(
    INPUT_FILE,
    encoding="utf-8-sig"
)

print("資料讀取完成！")
print()


# ============================================================
# 2. 設定中文字體
# ============================================================

plt.rcParams["font.sans-serif"] = [
    "Microsoft JhengHei"
]

plt.rcParams["axes.unicode_minus"] = False


# ============================================================
# 3. 男女裝商品數量
# ============================================================

gender_count = (
    df["gender"]
    .value_counts()
    .reindex(
        ["女裝", "男裝"],
        fill_value=0
    )
)

plt.figure(
    figsize=(8, 6)
)

bars = plt.bar(
    gender_count.index,
    gender_count.values
)

plt.title(
    "GU 男女裝商品數量",
    fontsize=16
)

plt.xlabel(
    "性別",
    fontsize=12
)

plt.ylabel(
    "商\n品\n數\n量",
    fontsize=12,
    rotation=0,
    labelpad=25
)

for bar in bars:

    value = int(
        bar.get_height()
    )

    plt.text(
        bar.get_x() + bar.get_width() / 2,
        value + 1,
        str(value),
        ha="center"
    )

plt.tight_layout()

gender_count_file = (
    OUTPUT_DIR /
    "gu_gender_count.png"
)

plt.savefig(
    gender_count_file,
    dpi=300
)

plt.show()


# ============================================================
# 4. 男女裝平均價格
# ============================================================

gender_avg_price = (
    df.groupby("gender")["price"]
    .mean()
    .reindex(
        ["女裝", "男裝"]
    )
)

plt.figure(
    figsize=(8, 6)
)

bars = plt.bar(
    gender_avg_price.index,
    gender_avg_price.values
)

plt.title(
    "GU 男女裝平均價格",
    fontsize=16
)

plt.xlabel(
    "性別",
    fontsize=12
)

plt.ylabel(
    "平\n均\n價\n格\n（元）",
    fontsize=12,
    rotation=0,
    labelpad=30
)

for bar in bars:

    value = bar.get_height()

    plt.text(
        bar.get_x() + bar.get_width() / 2,
        value + 10,
        f"{value:.0f}",
        ha="center"
    )

plt.tight_layout()

gender_average_price_file = (
    OUTPUT_DIR /
    "gu_gender_average_price.png"
)

plt.savefig(
    gender_average_price_file,
    dpi=300
)

plt.show()


# ============================================================
# 5. GU 價格區間
# ============================================================

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

plt.figure(
    figsize=(10, 6)
)

bars = plt.bar(
    price_range_count.index,
    price_range_count.values
)

plt.title(
    "GU 商品價格區間",
    fontsize=16
)

plt.xlabel(
    "價格區間",
    fontsize=12
)

plt.ylabel(
    "商\n品\n數\n量",
    fontsize=12,
    rotation=0,
    labelpad=25
)

plt.xticks(
    rotation=0
)

for bar in bars:

    value = int(
        bar.get_height()
    )

    if value > 0:

        plt.text(
            bar.get_x() + bar.get_width() / 2,
            value + 1,
            str(value),
            ha="center"
        )

plt.tight_layout()

price_range_file = (
    OUTPUT_DIR /
    "gu_price_range.png"
)

plt.savefig(
    price_range_file,
    dpi=300
)

plt.show()


# ============================================================
# 6. GU 商品價格分布
# ============================================================

plt.figure(
    figsize=(10, 6)
)

plt.hist(
    df["price"],
    bins=range(
        100,
        1401,
        100
    ),
    edgecolor="black"
)

plt.title(
    "GU 商品價格分布",
    fontsize=16
)

plt.xlabel(
    "價格（元）",
    fontsize=12
)

plt.ylabel(
    "商\n品\n數\n量",
    fontsize=12,
    rotation=0,
    labelpad=25
)

plt.xticks(
    range(
        100,
        1401,
        100
    )
)

plt.tight_layout()

price_distribution_file = (
    OUTPUT_DIR /
    "gu_price_distribution.png"
)

plt.savefig(
    price_distribution_file,
    dpi=300
)

plt.show()


# ============================================================
# 7. 完成
# ============================================================

print()
print("========================================")
print("GU 資料視覺化完成")
print("========================================")
print()

print("已產生以下圖片：")
print()

print(
    "1.",
    gender_count_file
)

print(
    "2.",
    gender_average_price_file
)

print(
    "3.",
    price_range_file
)

print(
    "4.",
    price_distribution_file
)

print()

print("視覺化完成！")