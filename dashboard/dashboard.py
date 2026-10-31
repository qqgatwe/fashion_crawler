
# ============================================================
# Fashion Radar Dashboard
# GU vs UNIQLO 商品資料分析
#
# 執行方式：
# streamlit run dashboard/dashboard.py
# ============================================================

from pathlib import Path
from html import escape

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


# ============================================================
# 1. 基本設定
# ============================================================

st.set_page_config(
    page_title="Fashion Radar | GU vs UNIQLO",
    page_icon="👕",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE_DIR = Path(__file__).resolve().parent.parent

GU_FILE = BASE_DIR / "data" / "cleaned" / "gu_products_cleaned.csv"
UNIQLO_FILE = BASE_DIR / "data" / "cleaned" / "uniqlo_products_cleaned.csv"
COMBINED_FILE = BASE_DIR / "data" / "analysis" / "brand_products_combined.csv"

BRANDS = ["GU", "UNIQLO"]

COLORS = {
    "GU": "#82A9D5",
    "UNIQLO": "#FF5664",
}

BG = "#0E1117"
CARD = "#171F2B"
GRID = "#293749"
TEXT = "#E9EFF7"
MUTED = "#98A9BD"

PRICE_LABELS = [
    "200元以下",
    "200–399元",
    "400–599元",
    "600–799元",
    "800–999元",
    "1000元以上",
]


# ============================================================
# 2. CSS 介面設計
# ============================================================

st.markdown(
    """
    <style>
    .stApp {
        background: #0E1117;
        color: #E9EFF7;
    }

    .block-container {
        max-width: 1480px;
        padding-top: 1.7rem;
        padding-bottom: 3rem;
    }

    h1 {
        font-size: 1.85rem !important;
        font-weight: 700 !important;
    }

    h2 {
        font-size: 1.35rem !important;
    }

    h3 {
        font-size: 1.08rem !important;
    }

    [data-testid="stSidebar"] {
        background: #111925;
        border-right: 1px solid #304052;
    }

    [data-testid="stMetric"] {
        background: #171F2B;
        border: 1px solid #34455A;
        border-radius: 12px;
        padding: 16px;
        min-height: 105px;
    }

    [data-testid="stMetricLabel"] {
        color: #98A9BD;
        font-size: 0.84rem;
    }

    [data-testid="stMetricValue"] {
        font-size: 1.5rem;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 7px;
        flex-wrap: wrap;
    }

    .stTabs [data-baseweb="tab"] {
        background: #171F2B;
        border-radius: 8px 8px 0 0;
        padding: 10px 15px;
        white-space: nowrap;
    }

    .stTabs [aria-selected="true"] {
        background: #26384C;
    }

    div[data-testid="stPlotlyChart"] {
        background: #171F2B;
        border: 1px solid #304052;
        border-radius: 12px;
        padding: 5px;
    }

    .insight-box {
        background: #171F2B;
        border: 1px solid #34455A;
        border-radius: 12px;
        padding: 18px 20px;
        margin-bottom: 10px;
        min-height: 115px;
    }

    .insight-title {
        color: #98A9BD;
        font-size: 0.83rem;
    }

    .insight-value {
        font-size: 1.45rem;
        font-weight: 700;
        color: #F1F5FA;
        margin-top: 9px;
    }

    .insight-detail {
        font-size: 0.82rem;
        color: #98A9BD;
        margin-top: 9px;
        line-height: 1.5;
    }

    .conclusion-box {
        background: #171F2B;
        border-left: 3px solid #82A9D5;
        border-radius: 8px;
        padding: 18px 22px;
        line-height: 1.9;
        margin-top: 12px;
    }

    .difference-box {
        background: #171F2B;
        border: 1px solid #34455A;
        border-radius: 12px;
        padding: 20px;
        margin-top: 12px;
    }

    .difference-label {
        color: #98A9BD;
        font-size: 0.83rem;
    }

    .difference-value {
        color: #FF7883;
        font-size: 1.6rem;
        font-weight: 700;
        margin-top: 6px;
    }

    .difference-description {
        color: #D9E3EF;
        font-size: 0.9rem;
        margin-top: 8px;
    }

    .chart-setting-title {
        font-size: 0.9rem;
        font-weight: 600;
        color: #E9EFF7;
        margin-bottom: 3px;
    }

    .chart-setting-description {
        font-size: 0.8rem;
        color: #98A9BD;
        margin-bottom: 10px;
    }

    [data-testid="stSlider"] {
        padding-top: 0.15rem;
        padding-bottom: 0.35rem;
    }

    /* 左側資料分析完成提示置中 */

    .sidebar-success {
        width: 100%;
        box-sizing: border-box;
        display: flex;
        align-items: center;
        justify-content: center;
        text-align: center;
        min-height: 54px;
        padding: 12px 16px;
        background: #173D30;
        border: 1px solid #275A46;
        border-radius: 8px;
        color: #39E58C;
        font-size: 0.94rem;
        font-weight: 600;
        line-height: 1.5;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# 3. 共用函式
# ============================================================

def money(value):
    """
    金額顯示為整數，不更動原始計算值。
    """
    if pd.isna(value):
        return "無資料"

    return f"NT$ {value:,.0f}"


def classify_price(price):
    if pd.isna(price):
        return "未知"

    if price < 200:
        return PRICE_LABELS[0]

    if price < 400:
        return PRICE_LABELS[1]

    if price < 600:
        return PRICE_LABELS[2]

    if price < 800:
        return PRICE_LABELS[3]

    if price < 1000:
        return PRICE_LABELS[4]

    return PRICE_LABELS[5]


def insight(title, value, detail=""):
    st.markdown(
        f"""
        <div class="insight-box">
            <div class="insight-title">
                {escape(str(title))}
            </div>
            <div class="insight-value">
                {escape(str(value))}
            </div>
            <div class="insight-detail">
                {escape(str(detail))}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section(title, description=""):
    st.subheader(title)

    if description:
        st.caption(description)


def chart_style(
    fig,
    height=400,
    left=80,
    right=100,
    bottom=60,
):
    """
    統一圖表風格。
    移除 X、Y 軸標題，避免中文字直排擠壓。
    """

    fig.update_layout(
        height=height,
        paper_bgcolor=CARD,
        plot_bgcolor=CARD,
        font=dict(
            color=TEXT,
            size=12,
        ),
        margin=dict(
            l=left,
            r=right,
            t=65,
            b=bottom,
        ),
        bargap=0.25,
        bargroupgap=0.08,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.03,
            xanchor="right",
            x=1,
            title_text="",
        ),
        hoverlabel=dict(
            bgcolor="#26364B",
            font_color=TEXT,
        ),
        xaxis_title=None,
        yaxis_title=None,
    )

    fig.update_xaxes(
        title_text=None,
        gridcolor=GRID,
        zeroline=False,
        automargin=True,
        tickfont=dict(size=11),
    )

    fig.update_yaxes(
        title_text=None,
        gridcolor=GRID,
        zeroline=False,
        automargin=True,
        tickfont=dict(size=11),
    )

    return fig


def show_chart(fig):
    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "displaylogo": False,
            "responsive": True,
        },
    )


def brand_bar_chart(
    values,
    price=False,
    height=350,
):
    fig = go.Figure()

    for brand, value in zip(BRANDS, values):
        if pd.isna(value):
            continue

        label = (
            money(value)
            if price
            else f"{value:,.0f} 件"
        )

        fig.add_trace(
            go.Bar(
                name=brand,
                x=[brand],
                y=[value],
                marker_color=COLORS[brand],
                text=[label],
                textposition="outside",
                cliponaxis=False,
                hovertemplate=(
                    f"{brand}<br>"
                    + (
                        "平均價格：NT$ %{y:,.0f}"
                        if price
                        else "商品數量：%{y:,.0f} 件"
                    )
                    + "<extra></extra>"
                ),
            )
        )

    chart_style(
        fig,
        height=height,
        left=55,
        right=55,
    )

    fig.update_layout(showlegend=False)

    valid_values = [
        value
        for value in values
        if pd.notna(value)
    ]

    maximum = max(valid_values, default=1)

    fig.update_yaxes(
        range=[0, max(maximum * 1.23, 1)]
    )

    return fig


def horizontal_comparison(
    data,
    value_col,
    category_col="category",
    price=False,
    height=None,
):
    if data.empty:
        return None

    order = (
        data.groupby(category_col)[value_col]
        .sum()
        .sort_values(ascending=False)
        .index.tolist()
    )

    fig = px.bar(
        data,
        x=value_col,
        y=category_col,
        color="brand",
        orientation="h",
        barmode="group",
        color_discrete_map=COLORS,
        category_orders={
            category_col: order[::-1],
        },
    )

    fig.update_traces(
        texttemplate=(
            "NT$ %{x:,.0f}"
            if price
            else "%{x:,.0f} 件"
        ),
        textposition="outside",
        cliponaxis=False,
    )

    chart_style(
        fig,
        height=height or max(
            420,
            len(order) * 57 + 110,
        ),
        left=125,
        right=135,
    )

    maximum = data[value_col].max()

    fig.update_xaxes(
        range=[
            0,
            maximum * 1.30,
        ] if maximum > 0 else [0, 1]
    )

    return fig


# ============================================================
# 4. 讀取資料
# ============================================================

@st.cache_data(show_spinner=False)
def load_data():

    if GU_FILE.exists() and UNIQLO_FILE.exists():

        gu = pd.read_csv(
            GU_FILE,
            encoding="utf-8-sig",
            dtype={"product_id": str},
        )

        uniqlo = pd.read_csv(
            UNIQLO_FILE,
            encoding="utf-8-sig",
            dtype={"product_id": str},
        )

        gu["brand"] = "GU"
        uniqlo["brand"] = "UNIQLO"

        data = pd.concat(
            [gu, uniqlo],
            ignore_index=True,
        )

    elif COMBINED_FILE.exists():

        data = pd.read_csv(
            COMBINED_FILE,
            encoding="utf-8-sig",
            dtype={"product_id": str},
        )

    else:

        raise FileNotFoundError(
            "找不到商品資料，請確認 data/cleaned 資料夾。"
        )

    # 不使用 gender 欄位進行分析
    # 因為目前 UNIQLO 的性別標記尚未驗證

    required = [
        "brand",
        "product_name",
        "product_id",
        "price",
        "product_url",
        "crawl_time",
        "source_category",
        "category",
    ]

    for column in required:
        if column not in data.columns:
            data[column] = pd.NA

    text_columns = [
        "brand",
        "product_name",
        "product_id",
        "product_url",
        "source_category",
        "category",
    ]

    for column in text_columns:
        data[column] = (
            data[column]
            .astype("string")
            .str.strip()
        )

    data["brand"] = (
        data["brand"]
        .str.upper()
    )

    data["price"] = pd.to_numeric(
        data["price"]
        .astype(str)
        .str.replace(",", "", regex=False)
        .str.replace("NT$", "", regex=False)
        .str.replace("元", "", regex=False)
        .str.strip(),
        errors="coerce",
    )

    data["price_range"] = (
        data["price"].apply(classify_price)
    )

    return data


try:
    df = load_data()

except Exception as error:
    st.error(f"讀取資料失敗：{error}")
    st.stop()


valid_df = df.dropna(
    subset=["price"]
).copy()

if valid_df.empty:
    st.error("目前沒有有效的商品價格資料。")
    st.stop()


# ============================================================
# 5. 資料統計
# ============================================================

gu_df = valid_df[
    valid_df["brand"] == "GU"
].copy()

uniqlo_df = valid_df[
    valid_df["brand"] == "UNIQLO"
].copy()

total_count = len(df)
gu_count = len(gu_df)
uniqlo_count = len(uniqlo_df)

gu_avg = gu_df["price"].mean()
uniqlo_avg = uniqlo_df["price"].mean()

price_diff = uniqlo_avg - gu_avg

price_diff_pct = (
    price_diff / gu_avg * 100
    if pd.notna(gu_avg) and gu_avg > 0
    else np.nan
)

categories = sorted(
    valid_df["category"]
    .dropna()
    .unique()
    .tolist()
)

common_categories = sorted(
    set(gu_df["category"].dropna())
    & set(uniqlo_df["category"].dropna())
)

category_stats = (
    valid_df
    .dropna(subset=["category"])
    .groupby(["brand", "category"])
    .agg(
        count=("price", "count"),
        avg_price=("price", "mean"),
        median_price=("price", "median"),
    )
    .reset_index()
)

category_pivot = (
    category_stats
    .pivot(
        index="category",
        columns="brand",
        values="avg_price",
    )
    .reindex(columns=BRANDS)
)

comparison = (
    category_pivot
    .dropna()
    .copy()
)

# 原始價差保留正負號，供其他分析判斷哪個品牌較貴
comparison["difference"] = (
    comparison["UNIQLO"] - comparison["GU"]
)

comparison["difference_pct"] = np.where(
    comparison["GU"] > 0,
    comparison["difference"]
    / comparison["GU"] * 100,
    np.nan,
)


# ============================================================
# 6. 側邊欄
# ============================================================

with st.sidebar:

    st.title("控制台")

    st.divider()

    st.subheader("資料集")

    st.metric(
        "商品總數",
        f"{total_count:,} 件",
    )

    c1, c2 = st.columns(2)

    with c1:
        st.metric(
            "GU",
            f"{gu_count:,} 件",
        )

    with c2:
        st.metric(
            "UNIQLO",
            f"{uniqlo_count:,} 件",
        )

    st.divider()

    if st.button(
        "重新讀取資料",
        use_container_width=True,
    ):
        st.cache_data.clear()
        st.rerun()

    st.markdown(
        """
        <div class="sidebar-success">
            資料分析完成
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# 7. 主畫面
# ============================================================

st.title("GU vs UNIQLO 商品資料分析")

st.caption(
    "Fashion Product Data Analysis Dashboard"
)

st.write("")

tabs = st.tabs([
    "📊 總覽",
    "👕 商品類型",
    "💰 價格分析",
    "⚖️ 品牌比較",
    "🔎 商品探索",
    "📋 商品分析總結",
])


# ============================================================
# TAB 1：總覽
# ============================================================

with tabs[0]:

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "GU 平均價格",
        money(gu_avg),
    )

    c2.metric(
        "UNIQLO 平均價格",
        money(uniqlo_avg),
    )

    c3.metric(
        "平均價格差",
        money(abs(price_diff)),
    )

    c4.metric(
        "共同商品類型",
        f"{len(common_categories)} 種",
    )

    st.write("")

    section("品牌分析摘要")

    left, right = st.columns(2)

    with left:

        higher = (
            "UNIQLO"
            if price_diff > 0
            else "GU"
            if price_diff < 0
            else "相同"
        )

        insight(
            "平均價格較高的品牌",
            higher,
            (
                f"GU：{money(gu_avg)}；"
                f"UNIQLO：{money(uniqlo_avg)}"
            ),
        )

    with right:

        insight(
            "UNIQLO 相對 GU 的平均價格差異",
            (
                f"{price_diff_pct:+.1f}%"
                if pd.notna(price_diff_pct)
                else "無資料"
            ),
            "依目前蒐集的商品樣本計算。",
        )

    st.write("")

    left, right = st.columns(2)

    with left:

        section(
            "品牌商品數量",
            "比較目前蒐集到的商品件數。",
        )

        fig = brand_bar_chart(
            [gu_count, uniqlo_count],
            price=False,
        )

        show_chart(fig)

    with right:

        section(
            "品牌平均價格",
            "比較兩個品牌商品的平均售價。",
        )

        fig = brand_bar_chart(
            [gu_avg, uniqlo_avg],
            price=True,
        )

        show_chart(fig)

    st.info(
        "商品數量代表本次蒐集的樣本數，"
        "不是品牌實際販售的全部商品。"
        "平均價格也會受到商品類型比例影響。"
    )


# ============================================================
# TAB 2：商品類型
# ============================================================

with tabs[1]:

    section(
        "各商品類型的商品數量",
        "比較兩個品牌在不同商品類型蒐集到的商品件數。",
    )

    category_limit = st.slider(
        "顯示商品類型數量",
        min_value=1,
        max_value=max(len(categories), 1),
        value=min(10, max(len(categories), 1)),
        step=1,
        format="%d 種",
        key="category_limit",
        help=(
            "調整下方商品數量及商品占比圖表"
            "要顯示多少種商品類型。"
        ),
    )

    st.caption(
        "此設定只影響本分頁的"
        "「商品數量」與「品牌占比」圖表。"
    )

    counts = (
        valid_df
        .dropna(subset=["category"])
        .groupby(["brand", "category"])
        .size()
        .reset_index(name="count")
    )

    top_categories = (
        counts
        .groupby("category")["count"]
        .sum()
        .nlargest(category_limit)
        .index
    )

    display_counts = counts[
        counts["category"].isin(top_categories)
    ].copy()

    if not display_counts.empty:

        fig = horizontal_comparison(
            display_counts,
            value_col="count",
        )

        show_chart(fig)

    else:

        st.info("目前沒有商品類型資料。")

    st.caption(
        "藍色代表 GU，紅色代表 UNIQLO。"
        "同一列的長條越長，代表商品件數越多。"
    )

    st.divider()

    # --------------------------------------------------------
    # 商品類型占比
    # --------------------------------------------------------

    section(
        "各商品類型的品牌占比",
        "比較商品類型在各品牌樣本中所占的比例。",
    )

    totals = (
        valid_df
        .groupby("brand")
        .size()
        .to_dict()
    )

    counts["percentage"] = counts.apply(
        lambda row: (
            row["count"]
            / totals[row["brand"]]
            * 100
            if totals.get(row["brand"], 0) > 0
            else 0
        ),
        axis=1,
    )

    share_df = counts[
        counts["category"].isin(top_categories)
    ].copy()

    if not share_df.empty:

        order = (
            share_df
            .groupby("category")["count"]
            .sum()
            .sort_values(ascending=False)
            .index.tolist()
        )

        fig = px.bar(
            share_df,
            x="percentage",
            y="category",
            color="brand",
            orientation="h",
            barmode="group",
            color_discrete_map=COLORS,
            category_orders={
                "category": order[::-1],
            },
        )

        fig.update_traces(
            texttemplate="%{x:.1f}%",
            textposition="outside",
            cliponaxis=False,
        )

        chart_style(
            fig,
            height=max(
                420,
                len(order) * 55 + 110,
            ),
            left=125,
            right=120,
        )

        maximum = share_df["percentage"].max()

        fig.update_xaxes(
            range=[
                0,
                max(maximum * 1.3, 1),
            ]
        )

        show_chart(fig)

    else:

        st.info("目前沒有商品類型占比資料。")

    st.caption(
        "例如 30% 代表該商品類型"
        "占品牌樣本的三成。"
    )

    st.divider()

    # --------------------------------------------------------
    # 已移除「男女裝商品數量」圖表
    # --------------------------------------------------------

    # --------------------------------------------------------
    # 商品類型統計表
    # --------------------------------------------------------

    section("商品類型統計表")

    table = category_stats.rename(
        columns={
            "brand": "品牌",
            "category": "商品類型",
            "count": "商品數量",
            "avg_price": "平均價格",
            "median_price": "中位數價格",
        }
    ).copy()

    st.dataframe(
        table,
        use_container_width=True,
        hide_index=True,
        column_config={
            "商品數量": st.column_config.NumberColumn(
                "商品數量",
                format="%d",
            ),
            "平均價格": st.column_config.NumberColumn(
                "平均價格",
                format="%.0f",
            ),
            "中位數價格": st.column_config.NumberColumn(
                "中位數價格",
                format="%.0f",
            ),
        },
    )


# ============================================================
# TAB 3：價格分析
# ============================================================

with tabs[2]:

    section(
        "各價格區間的商品占比",
        "觀察兩個品牌的商品主要集中在哪些價位。",
    )

    price_counts = pd.crosstab(
        valid_df["price_range"],
        valid_df["brand"],
    ).reindex(
        PRICE_LABELS,
        fill_value=0,
    )

    for brand in BRANDS:
        if brand not in price_counts.columns:
            price_counts[brand] = 0

    price_share = (
        price_counts[BRANDS]
        .astype(float)
    )

    for brand in BRANDS:

        total = price_share[brand].sum()

        if total > 0:
            price_share[brand] = (
                price_share[brand] / total * 100
            )

    fig = go.Figure()

    for brand in BRANDS:

        fig.add_trace(
            go.Bar(
                name=brand,
                x=PRICE_LABELS,
                y=price_share[brand].tolist(),
                marker_color=COLORS[brand],
                text=[
                    f"{value:.1f}%"
                    for value in price_share[brand]
                ],
                textposition="outside",
                cliponaxis=False,
            )
        )

    chart_style(
        fig,
        height=420,
        bottom=80,
    )

    fig.update_layout(
        barmode="group",
    )

    maximum = float(
        price_share.max().max()
    )

    fig.update_yaxes(
        range=[
            0,
            max(maximum * 1.25, 1),
        ]
    )

    show_chart(fig)

    st.info(
        "百分比代表該品牌有多少比例的商品"
        "落在指定的價格區間。"
    )

    st.divider()

    # --------------------------------------------------------
    # 平均價格與中位數
    # --------------------------------------------------------

    section(
        "平均價格與中位數比較",
        "比較品牌整體平均售價與價格中間值。",
    )

    price_summary = (
        valid_df
        .groupby("brand")["price"]
        .agg(
            avg_price="mean",
            median_price="median",
        )
        .reset_index()
    )

    price_long = price_summary.melt(
        id_vars="brand",
        value_vars=[
            "avg_price",
            "median_price",
        ],
        var_name="statistic",
        value_name="price",
    )

    price_long["statistic"] = (
        price_long["statistic"]
        .replace({
            "avg_price": "平均價格",
            "median_price": "中位數價格",
        })
    )

    fig = px.bar(
        price_long,
        x="statistic",
        y="price",
        color="brand",
        barmode="group",
        color_discrete_map=COLORS,
    )

    fig.update_traces(
        texttemplate="NT$ %{y:,.0f}",
        textposition="outside",
        cliponaxis=False,
    )

    chart_style(fig)

    maximum = price_long["price"].max()

    fig.update_yaxes(
        range=[
            0,
            max(maximum * 1.25, 1),
        ]
    )

    show_chart(fig)

    st.caption(
        "平均價格是所有價格的平均值；"
        "中位數是價格排序後位於中間的數值。"
    )

    st.divider()

    # --------------------------------------------------------
    # 品牌價格統計
    # --------------------------------------------------------

    section("品牌價格統計")

    price_stats = (
        valid_df
        .groupby("brand")["price"]
        .agg(
            商品數量="count",
            平均價格="mean",
            中位數="median",
            最低價格="min",
            最高價格="max",
        )
    )

    price_stats.index.name = "品牌"
    price_stats = price_stats.reset_index()

    st.dataframe(
        price_stats,
        use_container_width=True,
        hide_index=True,
        column_config={
            "商品數量": st.column_config.NumberColumn(
                "商品數量",
                format="%d",
            ),
            "平均價格": st.column_config.NumberColumn(
                "平均價格",
                format="%.0f",
            ),
            "中位數": st.column_config.NumberColumn(
                "中位數",
                format="%.0f",
            ),
            "最低價格": st.column_config.NumberColumn(
                "最低價格",
                format="%.0f",
            ),
            "最高價格": st.column_config.NumberColumn(
                "最高價格",
                format="%.0f",
            ),
        },
    )


# ============================================================
# TAB 4：品牌比較
# ============================================================

with tabs[3]:

    section(
        "相同商品類型的平均價格比較",
        "比較兩個品牌都有資料的商品類型。",
    )

    average_limit = st.slider(
        "顯示比較類型數量",
        min_value=1,
        max_value=max(len(comparison), 1),
        value=min(7, max(len(comparison), 1)),
        step=1,
        format="%d 種",
        key="average_limit",
        help=(
            "控制下方平均價格比較圖表"
            "顯示多少種共同商品類型。"
        ),
    )

    st.caption(
        "此設定只影響下方的"
        "「相同商品類型平均價格比較」圖表。"
    )

    selected = (
        comparison
        .assign(
            sort_value=lambda data: (
                data["GU"] + data["UNIQLO"]
            ) / 2
        )
        .sort_values(
            "sort_value",
            ascending=False,
        )
        .head(average_limit)
    )

    if not selected.empty:

        plot_df = (
            selected[BRANDS]
            .reset_index()
            .melt(
                id_vars="category",
                var_name="brand",
                value_name="avg_price",
            )
        )

        fig = horizontal_comparison(
            plot_df,
            value_col="avg_price",
            price=True,
        )

        show_chart(fig)

    else:

        st.info(
            "目前沒有共同商品類型可比較。"
        )

    st.divider()

    # --------------------------------------------------------
    # 價格差異排行榜
    # --------------------------------------------------------

    section(
        "哪些商品類型價差最大？",
        "依照兩個品牌平均價格的差額排序。",
    )

    if not comparison.empty:

        diff_df = comparison.copy()

        diff_df["absolute_diff"] = (
            diff_df["difference"].abs()
        )

        diff_df = (
            diff_df
            .sort_values(
                "absolute_diff",
                ascending=False,
            )
            .head(10)
            .reset_index()
        )

        diff_df["higher_brand"] = np.where(
            diff_df["difference"] > 0,
            "UNIQLO",
            np.where(
                diff_df["difference"] < 0,
                "GU",
                "相同",
            ),
        )

        diff_df["label"] = (
            diff_df["category"]
            + "（"
            + diff_df["higher_brand"]
            + "較高）"
        )

        fig = px.bar(
            diff_df.iloc[::-1],
            x="absolute_diff",
            y="label",
            color="higher_brand",
            orientation="h",
            color_discrete_map={
                **COLORS,
                "相同": "#8B98AA",
            },
        )

        fig.update_traces(
            texttemplate="NT$ %{x:,.0f}",
            textposition="outside",
            cliponaxis=False,
        )

        chart_style(
            fig,
            height=max(
                420,
                len(diff_df) * 48 + 110,
            ),
            left=175,
            right=120,
        )

        maximum = diff_df["absolute_diff"].max()

        fig.update_xaxes(
            range=[
                0,
                max(maximum * 1.3, 1),
            ]
        )

        show_chart(fig)

    st.caption(
        "此處比較的是平均價格差額，"
        "不代表商品品質或性價比。"
    )

    st.divider()

    # --------------------------------------------------------
    # 品牌價格比較表
    # 價差不顯示負號，新增價格較高品牌
    # --------------------------------------------------------

    section("品牌價格比較表")

    table = comparison.copy()

    # 先判斷哪個品牌平均價格較高
    table["higher_brand"] = np.where(
        table["difference"] > 0,
        "UNIQLO",
        np.where(
            table["difference"] < 0,
            "GU",
            "價格相同",
        ),
    )

    # 僅修改表格副本
    # 原始 comparison 的正負價差不受影響
    table["difference"] = table["difference"].abs()
    table["difference_pct"] = table["difference_pct"].abs()

    table = table.rename(
        columns={
            "GU": "GU 平均價格",
            "UNIQLO": "UNIQLO 平均價格",
            "difference": "價差（元）",
            "difference_pct": "價差（%）",
            "higher_brand": "價格較高品牌",
        }
    )

    table.index.name = "商品類型"
    table = table.reset_index()

    # 指定欄位顯示順序
    table = table[
        [
            "商品類型",
            "GU 平均價格",
            "UNIQLO 平均價格",
            "價差（元）",
            "價差（%）",
            "價格較高品牌",
        ]
    ]

    st.dataframe(
        table,
        use_container_width=True,
        hide_index=True,
        column_config={
            "GU 平均價格": st.column_config.NumberColumn(
                "GU 平均價格",
                format="%.0f",
            ),
            "UNIQLO 平均價格": st.column_config.NumberColumn(
                "UNIQLO 平均價格",
                format="%.0f",
            ),
            "價差（元）": st.column_config.NumberColumn(
                "價差（元）",
                format="%.0f",
            ),
            "價差（%）": st.column_config.NumberColumn(
                "價差（%）",
                format="%.2f%%",
            ),
            "價格較高品牌": st.column_config.TextColumn(
                "價格較高品牌",
            ),
        },
    )

    st.caption(
        "價差顯示兩品牌平均價格的絕對差額；"
        "價差百分比以 GU 平均價格為基準。"
        "「價格較高品牌」用來標示價差方向。"
    )


# ============================================================
# TAB 5：商品探索
# ============================================================

with tabs[4]:

    section(
        "商品搜尋與篩選",
        "依照品牌、類型、名稱及價格尋找商品。",
    )

    c1, c2, c3 = st.columns(3)

    with c1:

        selected_brands = st.multiselect(
            "品牌",
            BRANDS,
            default=BRANDS,
        )

    with c2:

        selected_categories = st.multiselect(
            "商品類型",
            categories,
            placeholder="全部商品類型",
        )

    with c3:

        keyword = st.text_input(
            "商品名稱",
            placeholder="例如：T恤、外套",
        )

    # --------------------------------------------------------
    # 不使用尚未驗證的性別分類篩選器
    # --------------------------------------------------------

    minimum = int(
        valid_df["price"].min()
    )

    maximum = int(
        valid_df["price"].max()
    )

    if minimum < maximum:

        selected_price = st.slider(
            "價格範圍（元）",
            minimum,
            maximum,
            (minimum, maximum),
        )

    else:

        selected_price = (
            minimum,
            maximum,
        )

        st.caption(
            f"目前商品價格皆為 {minimum} 元"
        )

    # --------------------------------------------------------
    # 套用篩選
    # --------------------------------------------------------

    filtered = valid_df[
        valid_df["brand"].isin(selected_brands)
    ].copy()

    if selected_categories:

        filtered = filtered[
            filtered["category"].isin(
                selected_categories
            )
        ]

    if keyword.strip():

        filtered = filtered[
            filtered["product_name"]
            .fillna("")
            .str.contains(
                keyword.strip(),
                case=False,
                regex=False,
            )
        ]

    filtered = filtered[
        filtered["price"].between(
            selected_price[0],
            selected_price[1],
        )
    ]

    st.metric(
        "符合條件商品",
        f"{len(filtered):,} 件",
    )

    st.divider()

    # --------------------------------------------------------
    # 商品資料表
    # --------------------------------------------------------

    section("商品資料瀏覽")

    display = filtered[
        [
            "brand",
            "category",
            "product_name",
            "price",
            "product_id",
            "product_url",
        ]
    ].rename(
        columns={
            "brand": "品牌",
            "category": "商品類型",
            "product_name": "商品名稱",
            "price": "價格",
            "product_id": "商品編號",
            "product_url": "商品網址",
        }
    )

    st.dataframe(
        display,
        use_container_width=True,
        hide_index=True,
        column_config={
            "價格": st.column_config.NumberColumn(
                "價格",
                format="NT$ %.0f",
            ),
            "商品網址": st.column_config.LinkColumn(
                "商品網址",
                display_text="查看商品",
            ),
        },
    )

    st.download_button(
        "📥 下載篩選結果",
        data=filtered.drop(
            columns=["gender"],
            errors="ignore",
        ).to_csv(
            index=False,
        ).encode("utf-8-sig"),
        file_name="fashion_filtered.csv",
        mime="text/csv",
    )

    st.divider()

    # --------------------------------------------------------
    # 商品價格排行榜
    # --------------------------------------------------------

    section(
        "商品價格排行榜",
        "依照目前篩選條件找出最便宜或最昂貴的商品。",
    )

    c1, c2 = st.columns(2)

    with c1:

        ranking_type = st.selectbox(
            "排行榜類型",
            [
                "最便宜商品",
                "最昂貴商品",
            ],
        )

    with c2:

        top_n = st.slider(
            "顯示商品數量",
            5,
            20,
            10,
        )

    ascending = (
        ranking_type == "最便宜商品"
    )

    ranking = (
        filtered
        .sort_values(
            "price",
            ascending=ascending,
        )
        .head(top_n)
        .copy()
    )

    if ranking.empty:

        st.info(
            "目前沒有符合條件的商品。"
        )

    else:

        ranking["short_name"] = (
            ranking["brand"]
            + "｜"
            + ranking["product_name"].fillna("")
        ).str.slice(0, 24)

        ranking["label"] = [
            f"{i + 1}. {name}"
            for i, name in enumerate(
                ranking["short_name"]
            )
        ]

        ranking = ranking.iloc[::-1]

        fig = px.bar(
            ranking,
            x="price",
            y="label",
            color="brand",
            orientation="h",
            color_discrete_map=COLORS,
        )

        fig.update_traces(
            texttemplate="NT$ %{x:,.0f}",
            textposition="outside",
            cliponaxis=False,
        )

        chart_style(
            fig,
            height=max(
                420,
                len(ranking) * 46 + 110,
            ),
            left=235,
            right=125,
        )

        maximum = ranking["price"].max()

        fig.update_xaxes(
            range=[
                0,
                max(maximum * 1.3, 1),
            ]
        )

        show_chart(fig)


# ============================================================
# TAB 6：商品分析總結
# ============================================================

with tabs[5]:

    section(
        "商品分析總結",
        "整理兩個品牌在商品價格及商品數量上的主要差異。",
    )

    if comparison.empty:

        st.info(
            "目前沒有共同商品類型可分析。"
        )

    else:

        uniqlo_higher = int(
            (comparison["difference"] > 0).sum()
        )

        gu_higher = int(
            (comparison["difference"] < 0).sum()
        )

        equal_count = int(
            (comparison["difference"] == 0).sum()
        )

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "UNIQLO 平均價格較高",
            f"{uniqlo_higher} 種",
        )

        c2.metric(
            "GU 平均價格較高",
            f"{gu_higher} 種",
        )

        c3.metric(
            "平均價格相同",
            f"{equal_count} 種",
        )

        st.divider()

        # ----------------------------------------------------
        # 共同商品類型平均價格
        # ----------------------------------------------------

        section(
            "共同商品類型的平均價格",
            "藍色代表 GU，紅色代表 UNIQLO。"
            "同一列長條越長，代表平均價格越高。",
        )

        compare_data = (
            comparison[BRANDS]
            .reset_index()
            .melt(
                id_vars="category",
                var_name="brand",
                value_name="avg_price",
            )
        )

        fig = horizontal_comparison(
            compare_data,
            value_col="avg_price",
            price=True,
            height=max(
                450,
                len(comparison) * 57 + 110,
            ),
        )

        show_chart(fig)

        # ----------------------------------------------------
        # 各商品類型數量比較
        # ----------------------------------------------------

        st.divider()

        section(
            "各商品類型的商品數量",
            "比較兩個品牌在不同類型蒐集到的商品件數。",
        )

        count_data = (
            category_stats
            .pivot_table(
                index="category",
                columns="brand",
                values="count",
                aggfunc="sum",
                fill_value=0,
            )
            .reindex(
                columns=BRANDS,
                fill_value=0,
            )
        )

        count_data["total"] = (
            count_data["GU"]
            + count_data["UNIQLO"]
        )

        count_data = (
            count_data
            .sort_values(
                "total",
                ascending=False,
            )
            .head(10)
        )

        chart_count = (
            count_data[BRANDS]
            .reset_index()
            .melt(
                id_vars="category",
                var_name="brand",
                value_name="count",
            )
        )

        fig = horizontal_comparison(
            chart_count,
            value_col="count",
            price=False,
        )

        show_chart(fig)

        # ----------------------------------------------------
        # 價格差距最大的商品類型
        # ----------------------------------------------------

        st.divider()

        section(
            "價格差距最大的商品類型",
            "找出兩個品牌平均售價相差最多的類型。",
        )

        biggest = comparison.copy()

        biggest["absolute_diff"] = (
            biggest["difference"].abs()
        )

        biggest = biggest.sort_values(
            "absolute_diff",
            ascending=False,
        )

        category_name = biggest.index[0]

        gu_price = biggest.loc[
            category_name,
            "GU",
        ]

        uniqlo_price = biggest.loc[
            category_name,
            "UNIQLO",
        ]

        difference = (
            uniqlo_price - gu_price
        )

        c1, c2, c3 = st.columns(3)

        with c1:

            insight(
                "商品類型",
                category_name,
                "平均價格差距最大的共同商品類型",
            )

        with c2:

            insight(
                "GU 平均價格",
                money(gu_price),
                "GU 商品樣本平均售價",
            )

        with c3:

            insight(
                "UNIQLO 平均價格",
                money(uniqlo_price),
                "UNIQLO 商品樣本平均售價",
            )

        if difference > 0:

            difference_text = (
                "UNIQLO 平均價格比 GU 高"
                f" {money(abs(difference))}"
            )

        elif difference < 0:

            difference_text = (
                "GU 平均價格比 UNIQLO 高"
                f" {money(abs(difference))}"
            )

        else:

            difference_text = (
                "兩品牌平均價格相同"
            )

        st.markdown(
            f"""
            <div class="difference-box">
                <div class="difference-label">
                    平均價格差距
                </div>
                <div class="difference-value">
                    {escape(money(abs(difference)))}
                </div>
                <div class="difference-description">
                    {escape(str(category_name))}：
                    {escape(difference_text)}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # --------------------------------------------------------
    # 分析重點
    # --------------------------------------------------------

    st.divider()

    section(
        "分析重點",
        "整理 GU 與 UNIQLO 商品資料中最值得注意的發現。",
    )

    gu_top = (
        gu_df["category"]
        .dropna()
        .value_counts()
    )

    uniqlo_top = (
        uniqlo_df["category"]
        .dropna()
        .value_counts()
    )

    gu_top_name = (
        gu_top.index[0]
        if not gu_top.empty
        else "無資料"
    )

    gu_top_count = (
        int(gu_top.iloc[0])
        if not gu_top.empty
        else 0
    )

    uniqlo_top_name = (
        uniqlo_top.index[0]
        if not uniqlo_top.empty
        else "無資料"
    )

    uniqlo_top_count = (
        int(uniqlo_top.iloc[0])
        if not uniqlo_top.empty
        else 0
    )

    common_count = len(comparison)

    uniqlo_higher_count = int(
        (comparison["difference"] > 0).sum()
    )

    # 第一排

    col1, col2 = st.columns(2)

    with col1:

        insight(
            "GU 最多商品類型",
            gu_top_name,
            f"共 {gu_top_count} 件商品",
        )

    with col2:

        insight(
            "UNIQLO 最多商品類型",
            uniqlo_top_name,
            f"共 {uniqlo_top_count} 件商品",
        )

    # 第二排

    col3, col4 = st.columns(2)

    with col3:

        insight(
            "UNIQLO 平均價格較高的類型",
            f"{uniqlo_higher_count} / {common_count} 種",
            "僅比較兩品牌都有資料的商品類型",
        )

    with col4:

        insight(
            "整體平均價格差異",
            (
                f"{price_diff_pct:+.1f}%"
                if pd.notna(price_diff_pct)
                else "無資料"
            ),
            "UNIQLO 相對 GU 的平均價格差異",
        )

    # --------------------------------------------------------
    # 主要發現
    # --------------------------------------------------------

    st.write("")

    section("主要發現")

    findings = []

    if not gu_top.empty:

        findings.append(
            f"GU 最常見的商品類型是 {gu_top_name}，"
            f"共有 {gu_top_count} 件。"
        )

    if not uniqlo_top.empty:

        findings.append(
            f"UNIQLO 最常見的商品類型是 {uniqlo_top_name}，"
            f"共有 {uniqlo_top_count} 件。"
        )

    if pd.notna(price_diff_pct):

        if price_diff_pct > 0:

            findings.append(
                "UNIQLO 的整體平均價格比 GU "
                f"高約 {abs(price_diff_pct):.1f}%。"
            )

        elif price_diff_pct < 0:

            findings.append(
                "UNIQLO 的整體平均價格比 GU "
                f"低約 {abs(price_diff_pct):.1f}%。"
            )

        else:

            findings.append(
                "兩個品牌的整體平均價格相同。"
            )

    if common_count > 0:

        findings.append(
            f"在 {common_count} 種共同商品類型中，"
            f"UNIQLO 有 {uniqlo_higher_count} 種"
            "平均價格較高。"
        )

    if findings:

        findings_html = "".join(
            f"<p>{escape(text)}</p>"
            for text in findings
        )

        st.markdown(
            f"""
            <div class="conclusion-box">
                {findings_html}
            </div>
            """,
            unsafe_allow_html=True,
        )

    else:

        st.info(
            "目前沒有足夠資料產生分析結論。"
        )

    st.write("")

    st.caption(
        "註：以上結果僅反映目前蒐集的商品樣本。"
        "價格及商品數量可能受到爬取範圍、"
        "商品類型比例及當時售價影響，"
        "不能直接代表品牌的全部商品或品質差異。"
    )


# ============================================================
# 8. 頁尾
# ============================================================

st.divider()

st.caption(
    f"Fashion Radar | "
    f"GU {gu_count:,} 件 | "
    f"UNIQLO {uniqlo_count:,} 件 | "
    f"總計 {total_count:,} 件 | "
    "Python · Pandas · Plotly · Streamlit"
)
