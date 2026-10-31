import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path


# ============================================================
# 0. 設定專案路徑
# ============================================================

# uniqlo_category_visualization.py 位於：
# fashion_crawler/crawlers/
#
# parent        = crawlers
# parent.parent = fashion_crawler

BASE_DIR = Path(__file__).resolve().parent.parent

ANALYSIS_DIR = BASE_DIR / "data" / "analysis"
OUTPUT_DIR = BASE_DIR / "outputs"

# 如果 outputs 資料夾不存在，自動建立
OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# 1. 讀取 UNIQLO 商品資料
# ============================================================

print("正在讀取 UNIQLO 商品資料...")

input_file = (
    ANALYSIS_DIR
    / "uniqlo_products_analysis.csv"
)

print(
    "讀取位置：",
    input_file
)

print()

df = pd.read_csv(
    input_file,
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
# 3. 商品類型數量
# ============================================================

category_count = (
    df["category"]
    .value_counts()
)

plt.figure(
    figsize=(10, 6)
)

bars = plt.bar(
    category_count.index,
    category_count.values
)

plt.title(
    "UNIQLO 商品類型數量",
    fontsize=16
)

plt.xlabel(
    "商品類型",
    fontsize=12
)

plt.ylabel(
    "商\n品\n數\n量",
    fontsize=12,
    rotation=0,
    labelpad=25
)

# 顯示數量
for bar in bars:

    value = int(
        bar.get_height()
    )

    plt.text(
        bar.get_x()
        + bar.get_width() / 2,
        value + 0.2,
        str(value),
        ha="center",
        va="bottom"
    )

plt.tight_layout()

output_file = (
    OUTPUT_DIR
    / "uniqlo_category_count.png"
)

plt.savefig(
    output_file,
    dpi=300,
    bbox_inches="tight"
)

plt.show()


# ============================================================
# 4. 各商品類型平均價格
# ============================================================

category_avg_price = (
    df.groupby("category")["price"]
    .mean()
    .sort_values()
)

plt.figure(
    figsize=(10, 6)
)

bars = plt.bar(
    category_avg_price.index,
    category_avg_price.values
)

plt.title(
    "UNIQLO 各商品類型平均價格",
    fontsize=16
)

plt.xlabel(
    "商品類型",
    fontsize=12
)

plt.ylabel(
    "平\n均\n價\n格\n（元）",
    fontsize=12,
    rotation=0,
    labelpad=30
)

# 顯示平均價格
for bar in bars:

    value = bar.get_height()

    plt.text(
        bar.get_x()
        + bar.get_width() / 2,
        value + 10,
        f"{value:.0f}",
        ha="center",
        va="bottom"
    )

plt.tight_layout()

output_file = (
    OUTPUT_DIR
    / "uniqlo_category_average_price.png"
)

plt.savefig(
    output_file,
    dpi=300,
    bbox_inches="tight"
)

plt.show()


# ============================================================
# 5. 各商品類型最低 / 平均 / 最高價格
#    群組長條圖
# ============================================================

category_price = (
    df.groupby("category")["price"]
    .agg([
        "min",
        "mean",
        "max"
    ])
)

# 按商品數量排序
category_order = (
    df["category"]
    .value_counts()
    .index
)

category_price = (
    category_price
    .reindex(category_order)
)


# ============================================================
# 建立長條圖位置
# ============================================================

x = np.arange(
    len(category_price)
)

width = 0.25

plt.figure(
    figsize=(11, 6)
)


# ============================================================
# 最低價格
# ============================================================

bars_min = plt.bar(
    x - width,
    category_price["min"],
    width,
    label="最低價格"
)


# ============================================================
# 平均價格
# ============================================================

bars_mean = plt.bar(
    x,
    category_price["mean"],
    width,
    label="平均價格"
)


# ============================================================
# 最高價格
# ============================================================

bars_max = plt.bar(
    x + width,
    category_price["max"],
    width,
    label="最高價格"
)


# ============================================================
# 圖表標題
# ============================================================

plt.title(
    "UNIQLO 各商品類型價格比較",
    fontsize=16
)

plt.xlabel(
    "商品類型",
    fontsize=12
)

plt.ylabel(
    "價\n格\n（元）",
    fontsize=12,
    rotation=0,
    labelpad=25
)


# ============================================================
# X 軸商品類型
# ============================================================

plt.xticks(
    x,
    category_price.index
)


# ============================================================
# 顯示價格數字
# ============================================================

for bars in [
    bars_min,
    bars_mean,
    bars_max
]:

    for bar in bars:

        value = bar.get_height()

        plt.text(
            bar.get_x()
            + bar.get_width() / 2,
            value + 10,
            f"{value:.0f}",
            ha="center",
            va="bottom",
            fontsize=9
        )


# ============================================================
# 圖例
# ============================================================

plt.legend()


# ============================================================
# 格線
# ============================================================

plt.grid(
    axis="y",
    linestyle="--",
    alpha=0.4
)


# ============================================================
# 排版
# ============================================================

plt.tight_layout()


# ============================================================
# 儲存圖片
# ============================================================

output_file = (
    OUTPUT_DIR
    / "uniqlo_category_price_comparison.png"
)

plt.savefig(
    output_file,
    dpi=300,
    bbox_inches="tight"
)

plt.show()


# ============================================================
# 6. 商品價格分布
# ============================================================

plt.figure(
    figsize=(10, 6)
)

plt.hist(
    df["price"],
    bins=8,
    edgecolor="black"
)

plt.title(
    "UNIQLO 商品價格分布",
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

plt.tight_layout()

output_file = (
    OUTPUT_DIR
    / "uniqlo_price_distribution.png"
)

plt.savefig(
    output_file,
    dpi=300,
    bbox_inches="tight"
)

plt.show()


# ============================================================
# 7. 完成
# ============================================================

print()
print("========================================")
print("UNIQLO 商品類型視覺化完成")
print("========================================")
print()

print("已產生以下圖片：")
print()

print(
    "1.",
    OUTPUT_DIR
    / "uniqlo_category_count.png"
)

print(
    "2.",
    OUTPUT_DIR
    / "uniqlo_category_average_price.png"
)

print(
    "3.",
    OUTPUT_DIR
    / "uniqlo_category_price_comparison.png"
)

print(
    "4.",
    OUTPUT_DIR
    / "uniqlo_price_distribution.png"
)

print()
print("視覺化完成！")