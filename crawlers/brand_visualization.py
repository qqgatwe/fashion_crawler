import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
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


# ============================================================
# 1. 設定檔案路徑
# ============================================================

INPUT_FILE = (
    ANALYSIS_DIR /
    "brand_products_combined.csv"
)

print("正在讀取品牌比較資料...")
print("讀取位置：", INPUT_FILE)
print()


# ============================================================
# 2. 讀取資料
# ============================================================

df = pd.read_csv(
    INPUT_FILE,
    encoding="utf-8-sig"
)

print("資料讀取完成！")
print()


# ============================================================
# 3. 設定中文字體
# ============================================================

plt.rcParams["font.sans-serif"] = [
    "Microsoft JhengHei"
]

plt.rcParams["axes.unicode_minus"] = False


# ============================================================
# 4. 共用圖表設定函式
# ============================================================

def setup_chart(
    title,
    xlabel,
    ylabel
):

    plt.title(
        title,
        fontsize=16,
        fontweight="bold",
        pad=15
    )

    plt.xlabel(
        xlabel,
        fontsize=12,
        labelpad=10
    )

    # Y 軸中文字直排
    plt.ylabel(
        ylabel,
        fontsize=12,
        rotation=0,
        labelpad=35
    )

    # 水平格線
    plt.grid(
        axis="y",
        linestyle="--",
        alpha=0.3
    )

    # 讓長條圖顯示在格線前面
    plt.gca().set_axisbelow(True)


# ============================================================
# 5. GU vs UNIQLO 平均價格
# ============================================================

brand_avg_price = (
    df.groupby("brand")["price"]
    .mean()
    .reindex(
        ["GU", "UNIQLO"]
    )
)

plt.figure(
    figsize=(9, 6)
)

bars = plt.bar(
    brand_avg_price.index,
    brand_avg_price.values,
    width=0.55
)

setup_chart(
    title="GU vs UNIQLO 平均價格",
    xlabel="品牌",
    ylabel="平\n均\n價\n格\n（元）"
)


# ------------------------------------------------------------
# 顯示平均價格
# ------------------------------------------------------------

for bar, value in zip(
    bars,
    brand_avg_price.values
):

    plt.text(
        bar.get_x() + bar.get_width() / 2,
        value + 12,
        f"{value:.2f} 元",
        ha="center",
        va="bottom",
        fontsize=11
    )


# ------------------------------------------------------------
# 留出上方空間
# ------------------------------------------------------------

plt.ylim(
    0,
    brand_avg_price.max() * 1.25
)

plt.tight_layout()


# ------------------------------------------------------------
# 儲存圖片
# ------------------------------------------------------------

average_price_file = (
    OUTPUT_DIR /
    "brand_average_price.png"
)

plt.savefig(
    average_price_file,
    dpi=300,
    bbox_inches="tight"
)

plt.show()
plt.close()


# ============================================================
# 6. GU vs UNIQLO 價格區間分布
# ============================================================

price_order = [
    "200元以下",
    "200-399元",
    "400-599元",
    "600-799元",
    "800-999元",
    "1000元以上"
]


price_range_table = pd.crosstab(
    df["price_range"],
    df["brand"]
)


# ------------------------------------------------------------
# 固定價格區間順序
# ------------------------------------------------------------

price_range_table = (
    price_range_table
    .reindex(
        price_order,
        fill_value=0
    )
)


# ------------------------------------------------------------
# 確保 GU、UNIQLO 欄位存在
# ------------------------------------------------------------

price_range_table = (
    price_range_table
    .reindex(
        columns=[
            "GU",
            "UNIQLO"
        ],
        fill_value=0
    )
)


# ------------------------------------------------------------
# 建立 X 軸位置
# ------------------------------------------------------------

x = np.arange(
    len(price_range_table.index)
)

width = 0.34


plt.figure(
    figsize=(11, 6)
)


# ------------------------------------------------------------
# GU
# ------------------------------------------------------------

gu_bars = plt.bar(
    x - width / 2,
    price_range_table["GU"],
    width,
    label="GU"
)


# ------------------------------------------------------------
# UNIQLO
# ------------------------------------------------------------

uniqlo_bars = plt.bar(
    x + width / 2,
    price_range_table["UNIQLO"],
    width,
    label="UNIQLO"
)


setup_chart(
    title="GU vs UNIQLO 價格區間比較",
    xlabel="價格區間",
    ylabel="商\n品\n數\n量"
)


# ------------------------------------------------------------
# X 軸標籤
# ------------------------------------------------------------

plt.xticks(
    x,
    price_range_table.index,
    rotation=15,
    ha="right"
)


# ------------------------------------------------------------
# 圖例
# ------------------------------------------------------------

plt.legend(
    title="品牌"
)


# ------------------------------------------------------------
# 顯示 GU 商品數量
# ------------------------------------------------------------

for bar in gu_bars:

    value = int(
        bar.get_height()
    )

    if value > 0:

        plt.text(
            bar.get_x()
            + bar.get_width() / 2,
            value + 0.8,
            str(value),
            ha="center",
            va="bottom",
            fontsize=10
        )


# ------------------------------------------------------------
# 顯示 UNIQLO 商品數量
# ------------------------------------------------------------

for bar in uniqlo_bars:

    value = int(
        bar.get_height()
    )

    if value > 0:

        plt.text(
            bar.get_x()
            + bar.get_width() / 2,
            value + 0.8,
            str(value),
            ha="center",
            va="bottom",
            fontsize=10
        )


# ------------------------------------------------------------
# 留出上方空間
# ------------------------------------------------------------

max_count = (
    price_range_table
    .to_numpy()
    .max()
)

plt.ylim(
    0,
    max_count * 1.18
)

plt.tight_layout()


# ------------------------------------------------------------
# 儲存圖片
# ------------------------------------------------------------

price_range_file = (
    OUTPUT_DIR /
    "brand_price_range.png"
)

plt.savefig(
    price_range_file,
    dpi=300,
    bbox_inches="tight"
)

plt.show()
plt.close()


# ============================================================
# 7. 找出兩個品牌共同商品類型
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


common_categories_set = (
    gu_categories
    &
    uniqlo_categories
)


# ------------------------------------------------------------
# 固定共同商品類型顯示順序
# ------------------------------------------------------------

preferred_category_order = [
    "T恤",
    "外套",
    "連帽上衣",
    "針織"
]


common_categories = [
    category
    for category
    in preferred_category_order
    if category in common_categories_set
]


# 如果未來多出其他共同類型，自動加到最後
other_categories = sorted(
    common_categories_set
    -
    set(common_categories)
)

common_categories.extend(
    other_categories
)


print("共同商品類型：")
print(common_categories)
print()


# ============================================================
# 8. 篩選共同商品類型資料
# ============================================================

common_df = df[
    df["category"].isin(
        common_categories
    )
].copy()


# ============================================================
# 9. 共同商品類型平均價格比較
# ============================================================

category_avg_price = pd.pivot_table(
    common_df,
    values="price",
    index="category",
    columns="brand",
    aggfunc="mean"
)


# ------------------------------------------------------------
# 固定類型順序
# ------------------------------------------------------------

category_avg_price = (
    category_avg_price
    .reindex(
        common_categories
    )
)


# ------------------------------------------------------------
# 固定品牌順序
# ------------------------------------------------------------

category_avg_price = (
    category_avg_price
    .reindex(
        columns=[
            "GU",
            "UNIQLO"
        ]
    )
)


x = np.arange(
    len(category_avg_price.index)
)

width = 0.34


plt.figure(
    figsize=(11, 6)
)


# ------------------------------------------------------------
# GU
# ------------------------------------------------------------

gu_bars = plt.bar(
    x - width / 2,
    category_avg_price["GU"],
    width,
    label="GU"
)


# ------------------------------------------------------------
# UNIQLO
# ------------------------------------------------------------

uniqlo_bars = plt.bar(
    x + width / 2,
    category_avg_price["UNIQLO"],
    width,
    label="UNIQLO"
)


setup_chart(
    title="GU vs UNIQLO 共同商品類型平均價格",
    xlabel="商品類型",
    ylabel="平\n均\n價\n格\n（元）"
)


plt.xticks(
    x,
    category_avg_price.index
)


plt.legend(
    title="品牌"
)


# ------------------------------------------------------------
# 顯示 GU 平均價格
# ------------------------------------------------------------

for bar in gu_bars:

    value = bar.get_height()

    if not np.isnan(value):

        plt.text(
            bar.get_x()
            + bar.get_width() / 2,
            value + 18,
            f"{value:.0f}",
            ha="center",
            va="bottom",
            fontsize=10
        )


# ------------------------------------------------------------
# 顯示 UNIQLO 平均價格
# ------------------------------------------------------------

for bar in uniqlo_bars:

    value = bar.get_height()

    if not np.isnan(value):

        plt.text(
            bar.get_x()
            + bar.get_width() / 2,
            value + 18,
            f"{value:.0f}",
            ha="center",
            va="bottom",
            fontsize=10
        )


# ------------------------------------------------------------
# 留出上方空間
# ------------------------------------------------------------

max_category_price = (
    category_avg_price
    .max()
    .max()
)

plt.ylim(
    0,
    max_category_price * 1.18
)


plt.tight_layout()


# ------------------------------------------------------------
# 儲存圖片
# ------------------------------------------------------------

category_average_price_file = (
    OUTPUT_DIR /
    "brand_category_average_price.png"
)

plt.savefig(
    category_average_price_file,
    dpi=300,
    bbox_inches="tight"
)

plt.show()
plt.close()


# ============================================================
# 10. 共同商品類型數量比較
# ============================================================

category_count = pd.crosstab(
    common_df["category"],
    common_df["brand"]
)


# ------------------------------------------------------------
# 固定商品類型順序
# ------------------------------------------------------------

category_count = (
    category_count
    .reindex(
        common_categories,
        fill_value=0
    )
)


# ------------------------------------------------------------
# 固定品牌順序
# ------------------------------------------------------------

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


x = np.arange(
    len(category_count.index)
)

width = 0.34


plt.figure(
    figsize=(11, 6)
)


# ------------------------------------------------------------
# GU
# ------------------------------------------------------------

gu_bars = plt.bar(
    x - width / 2,
    category_count["GU"],
    width,
    label="GU"
)


# ------------------------------------------------------------
# UNIQLO
# ------------------------------------------------------------

uniqlo_bars = plt.bar(
    x + width / 2,
    category_count["UNIQLO"],
    width,
    label="UNIQLO"
)


setup_chart(
    title="GU vs UNIQLO 共同商品類型數量",
    xlabel="商品類型",
    ylabel="商\n品\n數\n量"
)


plt.xticks(
    x,
    category_count.index
)


plt.legend(
    title="品牌"
)


# ------------------------------------------------------------
# 顯示 GU 商品數量
# ------------------------------------------------------------

for bar in gu_bars:

    value = int(
        bar.get_height()
    )

    if value > 0:

        plt.text(
            bar.get_x()
            + bar.get_width() / 2,
            value + 1,
            str(value),
            ha="center",
            va="bottom",
            fontsize=10
        )


# ------------------------------------------------------------
# 顯示 UNIQLO 商品數量
# ------------------------------------------------------------

for bar in uniqlo_bars:

    value = int(
        bar.get_height()
    )

    if value > 0:

        plt.text(
            bar.get_x()
            + bar.get_width() / 2,
            value + 1,
            str(value),
            ha="center",
            va="bottom",
            fontsize=10
        )


# ------------------------------------------------------------
# 留出上方空間
# ------------------------------------------------------------

max_category_count = (
    category_count
    .to_numpy()
    .max()
)

plt.ylim(
    0,
    max_category_count * 1.18
)


plt.tight_layout()


# ------------------------------------------------------------
# 儲存圖片
# ------------------------------------------------------------

category_count_file = (
    OUTPUT_DIR /
    "brand_category_count.png"
)

plt.savefig(
    category_count_file,
    dpi=300,
    bbox_inches="tight"
)

plt.show()
plt.close()


# ============================================================
# 11. 完成
# ============================================================

print()
print("========================================")
print("GU vs UNIQLO 品牌視覺化完成")
print("========================================")
print()

print("已產生以下圖片：")
print()

print(
    "1.",
    average_price_file
)

print(
    "2.",
    price_range_file
)

print(
    "3.",
    category_average_price_file
)

print(
    "4.",
    category_count_file
)

print()

print("視覺化完成！")