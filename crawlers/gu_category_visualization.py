import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from pathlib import Path


# ============================================================
# 0. 設定專案路徑
# ============================================================

# gu_category_visualization.py 位於：
# fashion_crawler/crawlers/
#
# parent       = crawlers
# parent.parent = fashion_crawler

BASE_DIR = Path(__file__).resolve().parent.parent

CLEANED_DIR = BASE_DIR / "data" / "cleaned"
OUTPUT_DIR = BASE_DIR / "outputs"

# 如果 outputs 資料夾不存在，自動建立
OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# 1. 讀取資料
# ============================================================

print("正在讀取 GU 商品資料...")

input_file = (
    CLEANED_DIR
    / "gu_products_cleaned.csv"
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
# 3. 商品類型順序
# ============================================================

category_order = [
    "T恤",
    "背心",
    "休閒上衣",
    "連帽上衣",
    "針織",
    "內衣",
    "外套"
]


# ============================================================
# 4. 各商品類型數量
# ============================================================

category_count = (
    df["category"]
    .value_counts()
    .reindex(
        category_order,
        fill_value=0
    )
)

plt.figure(
    figsize=(10, 6)
)

bars = plt.bar(
    category_count.index,
    category_count.values
)

plt.title(
    "GU 各商品類型數量",
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

# 顯示柱狀圖上方數字
for bar in bars:

    height = bar.get_height()

    plt.text(
        bar.get_x()
        + bar.get_width() / 2,
        height + 1,
        f"{int(height)}",
        ha="center",
        va="bottom"
    )

plt.tight_layout()

output_file = (
    OUTPUT_DIR
    / "gu_category_count.png"
)

plt.savefig(
    output_file,
    dpi=300,
    bbox_inches="tight"
)

plt.show()


# ============================================================
# 5. 各商品類型平均價格
# ============================================================

category_avg_price = (
    df.groupby("category")["price"]
    .mean()
    .reindex(category_order)
)

plt.figure(
    figsize=(10, 6)
)

bars = plt.bar(
    category_avg_price.index,
    category_avg_price.values
)

plt.title(
    "GU 各商品類型平均價格",
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

# Y 軸不要顯示小數點
plt.gca().yaxis.set_major_formatter(
    FuncFormatter(
        lambda x, pos: f"{int(x)}"
    )
)

# 柱狀圖上方顯示整數
for bar in bars:

    height = bar.get_height()

    plt.text(
        bar.get_x()
        + bar.get_width() / 2,
        height + 15,
        f"{height:.0f}",
        ha="center",
        va="bottom"
    )

plt.tight_layout()

output_file = (
    OUTPUT_DIR
    / "gu_category_average_price.png"
)

plt.savefig(
    output_file,
    dpi=300,
    bbox_inches="tight"
)

plt.show()


# ============================================================
# 6. 男女裝 × 商品類型
# ============================================================

gender_category = pd.crosstab(
    df["category"],
    df["gender"]
)

# 確保女裝、男裝欄位存在
gender_category = (
    gender_category
    .reindex(
        columns=[
            "女裝",
            "男裝"
        ],
        fill_value=0
    )
)

# 按照商品類型順序排列
gender_category = (
    gender_category
    .reindex(
        category_order,
        fill_value=0
    )
)

ax = gender_category.plot(
    kind="bar",
    figsize=(11, 6)
)

plt.title(
    "GU 男女裝 × 商品類型",
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

plt.xticks(
    rotation=0
)

plt.legend(
    title="性別"
)

# 顯示柱狀圖數字
for container in ax.containers:

    labels = []

    for value in container.datavalues:

        if value == 0:

            labels.append("")

        else:

            labels.append(
                f"{int(value)}"
            )

    ax.bar_label(
        container,
        labels=labels,
        padding=3
    )

plt.tight_layout()

output_file = (
    OUTPUT_DIR
    / "gu_gender_category.png"
)

plt.savefig(
    output_file,
    dpi=300,
    bbox_inches="tight"
)

plt.show()


# ============================================================
# 7. 各商品類型最低／最高價格
# ============================================================

category_price = (
    df.groupby("category")["price"]
    .agg([
        "min",
        "max"
    ])
    .reindex(category_order)
)

category_price.columns = [
    "最低價格",
    "最高價格"
]

ax = category_price.plot(
    kind="bar",
    figsize=(11, 6)
)

plt.title(
    "GU 各商品類型最低／最高價格",
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

plt.xticks(
    rotation=0
)

plt.legend(
    title="價格"
)

# Y 軸顯示整數
plt.gca().yaxis.set_major_formatter(
    FuncFormatter(
        lambda x, pos: f"{int(x)}"
    )
)

# 顯示柱狀圖上的價格
for container in ax.containers:

    labels = []

    for value in container.datavalues:

        if pd.isna(value):

            labels.append("")

        else:

            labels.append(
                f"{int(value)}"
            )

    ax.bar_label(
        container,
        labels=labels,
        padding=3
    )

plt.tight_layout()

output_file = (
    OUTPUT_DIR
    / "gu_category_price_range.png"
)

plt.savefig(
    output_file,
    dpi=300,
    bbox_inches="tight"
)

plt.show()


# ============================================================
# 8. 完成
# ============================================================

print()
print("========================================")
print("GU 商品類型視覺化完成")
print("========================================")
print()

print("已產生以下圖片：")
print()

print(
    "1.",
    OUTPUT_DIR
    / "gu_category_count.png"
)

print(
    "2.",
    OUTPUT_DIR
    / "gu_category_average_price.png"
)

print(
    "3.",
    OUTPUT_DIR
    / "gu_gender_category.png"
)

print(
    "4.",
    OUTPUT_DIR
    / "gu_category_price_range.png"
)

print()
print("視覺化完成！")