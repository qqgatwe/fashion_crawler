import re
import time
import numpy as np
import pandas as pd

from datetime import datetime
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# ============================================================
# 0. 設定專案路徑
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"

# 如果 raw 資料夾不存在，自動建立
RAW_DIR.mkdir(
    parents=True,
    exist_ok=True
)

OUTPUT_FILE = (
    RAW_DIR /
    "uniqlo_products.csv"
)


# ============================================================
# 1. UNIQLO 要爬取的分類
# ============================================================

CATEGORY_URLS = {

    "T恤／背心／休閒":
        "https://www.uniqlo.com/tw/zh_TW/c/all_women-tops.html",

    "襯衫／設計上衣／POLO衫":
        "https://www.uniqlo.com/tw/zh_TW/c/all_women-shirts.html",

    "針織衫／開襟外套":
        "https://www.uniqlo.com/tw/zh_TW/c/all_women-knit.html",

    "外套":
        "https://www.uniqlo.com/tw/zh_TW/c/all_women-outer.html"
}


# ============================================================
# 2. 開啟 Chrome
# ============================================================

print()
print("=" * 60)
print("正在啟動 Chrome...")
print("=" * 60)
print()

driver = webdriver.Chrome()

driver.maximize_window()

data = []


# ============================================================
# 3. 自動往下捲動頁面
# ============================================================

def scroll_page():

    print()
    print("開始往下捲動頁面...")

    last_height = driver.execute_script(
        "return document.body.scrollHeight"
    )

    no_change_count = 0

    scroll_count = 0

    while True:

        # 往最下面捲
        driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);"
        )

        scroll_count += 1

        print(
            f"頁面捲動第 {scroll_count} 次..."
        )

        # 等待商品載入
        time.sleep(2)

        new_height = driver.execute_script(
            "return document.body.scrollHeight"
        )

        # 如果高度沒有變
        if new_height == last_height:

            no_change_count += 1

        else:

            no_change_count = 0

        # 連續三次高度沒有改變
        # 判斷已經載入到底
        if no_change_count >= 3:

            print(
                "頁面高度已連續 3 次沒有變化"
            )

            print(
                "判斷商品已載入完成"
            )

            break

        last_height = new_height

    # 回到頁面最上方
    driver.execute_script(
        "window.scrollTo(0, 0);"
    )

    time.sleep(1)

    print("頁面捲動完成")
    print()


# ============================================================
# 4. 爬取單一分類
# ============================================================

def crawl_category(
    category_name,
    url
):

    print()
    print("=" * 60)
    print("開始爬取分類：", category_name)
    print("=" * 60)
    print()

    print("網址：")
    print(url)
    print()

    # --------------------------------------------------------
    # 開啟網頁
    # --------------------------------------------------------

    driver.get(url)

    print("網頁已開啟")
    print()

    print(
        "目前網址：",
        driver.current_url
    )

    print(
        "網頁標題：",
        driver.title
    )

    print()


    # --------------------------------------------------------
    # 等待商品載入
    # --------------------------------------------------------

    print("等待商品載入...")

    WebDriverWait(
        driver,
        30
    ).until(

        EC.presence_of_element_located(
            (
                By.CSS_SELECTOR,
                "li.product-li"
            )
        )
    )

    time.sleep(3)

    print("商品已載入")


    # --------------------------------------------------------
    # 自動捲動
    # --------------------------------------------------------

    scroll_page()


    # --------------------------------------------------------
    # 找到所有商品
    # --------------------------------------------------------

    products = driver.find_elements(
        By.CSS_SELECTOR,
        "li.product-li"
    )

    print(
        "目前頁面找到商品數量：",
        len(products)
    )

    print()


    # --------------------------------------------------------
    # 建立此分類暫存資料
    # --------------------------------------------------------

    category_data = []


    # --------------------------------------------------------
    # 逐一抓取商品
    # --------------------------------------------------------

    for i, product in enumerate(
        products,
        start=1
    ):

        try:

            # ==================================================
            # 商品名稱
            # ==================================================

            name_element = (
                product.find_element(
                    By.CSS_SELECTOR,
                    ".product-name"
                )
            )

            raw_name = (
                name_element
                .get_attribute(
                    "textContent"
                )
                .strip()
            )


            # ==================================================
            # 商品價格
            # ==================================================

            price_element = (
                product.find_element(
                    By.CSS_SELECTOR,
                    ".product-price span"
                )
            )

            raw_price = (
                price_element
                .get_attribute(
                    "textContent"
                )
                .strip()
            )


            # ==================================================
            # 商品網址
            # ==================================================

            link_element = (
                product.find_element(
                    By.CSS_SELECTOR,
                    "a.h-a-label"
                )
            )

            product_url = (
                link_element
                .get_attribute(
                    "href"
                )
            )


            # ==================================================
            # 商品編號
            # ==================================================

            product_ids = re.findall(
                r"\d{6}",
                raw_name
            )

            if product_ids:

                # 最後一組六位數字
                # 當成商品編號

                product_id = (
                    product_ids[-1]
                )


                # 移除商品名稱後面的商品編號

                product_name = re.sub(
                    r"\s+\d{6}(\s+\d{6})*$",
                    "",
                    raw_name
                ).strip()

            else:

                product_id = ""

                product_name = (
                    raw_name
                )


            # ==================================================
            # 價格清理
            # ==================================================

            price_match = re.search(
                r"\d+",
                raw_price.replace(
                    ",",
                    ""
                )
            )

            if price_match:

                price = int(
                    price_match.group()
                )

            else:

                price = None


            # ==================================================
            # 爬取時間
            # ==================================================

            crawl_time = (
                datetime.now()
                .strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            )


            # ==================================================
            # 建立商品資料
            # ==================================================

            record = {

                "brand":
                    "UNIQLO",

                "product_name":
                    product_name,

                "product_id":
                    product_id,

                "price":
                    price,

                "product_url":
                    product_url,

                "crawl_time":
                    crawl_time,

                "source_category":
                    category_name
            }


            # ==================================================
            # 加入分類資料
            # ==================================================

            category_data.append(
                record
            )


            # ==================================================
            # 顯示目前進度
            # ==================================================

            print(
                f"[{category_name}] "
                f"{i}/{len(products)}："
                f"{product_name}"
            )


        except Exception as e:

            print(
                f"[{category_name}] "
                f"第 {i} 個商品處理失敗："
            )

            print(e)


    # --------------------------------------------------------
    # 此分類完成
    # --------------------------------------------------------

    print()

    print(
        category_name,
        "成功取得：",
        len(category_data),
        "筆"
    )

    print()

    return category_data


# ============================================================
# 5. 開始爬取全部分類
# ============================================================

try:

    print()
    print("=" * 60)
    print("UNIQLO 女裝商品爬蟲開始")
    print("=" * 60)
    print()

    print(
        "本次共需要爬取",
        len(CATEGORY_URLS),
        "個分類"
    )

    print()


    # --------------------------------------------------------
    # 逐一處理分類
    # --------------------------------------------------------

    for index, (
        category_name,
        url
    ) in enumerate(
        CATEGORY_URLS.items(),
        start=1
    ):

        print()
        print(
            f"目前分類："
            f"{index}/{len(CATEGORY_URLS)}"
        )

        try:

            category_result = (
                crawl_category(
                    category_name,
                    url
                )
            )

            data.extend(
                category_result
            )

        except Exception as e:

            print()
            print("=" * 60)
            print(
                "分類爬取失敗：",
                category_name
            )
            print("=" * 60)

            print(
                "錯誤：",
                e
            )

            print()
            print(
                "程式將繼續爬下一個分類..."
            )

        # 分類與分類之間休息
        time.sleep(3)


# ============================================================
# 6. 關閉瀏覽器
# ============================================================

finally:

    driver.quit()

    print()
    print("=" * 60)
    print("瀏覽器已關閉")
    print("=" * 60)


# ============================================================
# 7. 建立 DataFrame
# ============================================================

df = pd.DataFrame(
    data
)


# ============================================================
# 8. 顯示原始爬取結果
# ============================================================

print()
print("=" * 60)
print("原始爬取結果")
print("=" * 60)
print()

print(
    "原始資料筆數：",
    len(df)
)

print()


# ============================================================
# 9. 檢查是否有資料
# ============================================================

if df.empty:

    print(
        "沒有抓到任何商品資料。"
    )

    print(
        "請檢查網頁結構或 CSS Selector。"
    )

    raise SystemExit


# ============================================================
# 10. 價格轉成數字
# ============================================================

df["price"] = pd.to_numeric(
    df["price"],
    errors="coerce"
)


# ============================================================
# 11. 商品編號轉成字串
# ============================================================

df["product_id"] = (
    df["product_id"]
    .fillna("")
    .astype(str)
)


# ============================================================
# 12. 商品名稱清理
# ============================================================

df["product_name"] = (
    df["product_name"]
    .fillna("")
    .astype(str)
    .str.strip()
)


# ============================================================
# 13. 移除商品網址為空的資料
# ============================================================

before_url_clean = len(df)

df = df.dropna(
    subset=[
        "product_url"
    ]
)

after_url_clean = len(df)

removed_url_count = (
    before_url_clean
    -
    after_url_clean
)


print()
print("=" * 60)
print("商品網址檢查")
print("=" * 60)
print()

print(
    "移除商品網址為空：",
    removed_url_count,
    "筆"
)


# ============================================================
# 14. 移除完全重複資料
# ============================================================

before_exact_dedup = len(df)

df = df.drop_duplicates()

after_exact_dedup = len(df)

exact_duplicate_count = (
    before_exact_dedup
    -
    after_exact_dedup
)


print()
print("=" * 60)
print("完全重複資料檢查")
print("=" * 60)
print()

print(
    "完全重複資料：",
    exact_duplicate_count,
    "筆"
)


# ============================================================
# 15. 顯示各分類原始商品數
# ============================================================

print()
print("=" * 60)
print("各分類原始商品數")
print("=" * 60)
print()

category_counts_before = (
    df["source_category"]
    .value_counts()
)

print(
    category_counts_before
)


# ============================================================
# 16. 建立商品去重 Key
# ============================================================

# 有商品編號：
# 使用 product_id
#
# 沒有商品編號：
# 使用 product_url

df["dedup_key"] = np.where(

    df["product_id"]
    .str
    .strip() != "",

    "ID_"
    +
    df["product_id"],

    "URL_"
    +
    df["product_url"]
    .astype(str)
)


# ============================================================
# 17. 商品去重
# ============================================================

before_dedup = len(df)

df = df.drop_duplicates(
    subset=[
        "dedup_key"
    ],
    keep="first"
)

after_dedup = len(df)

duplicate_count = (
    before_dedup
    -
    after_dedup
)


# ============================================================
# 18. 移除暫時使用的 dedup_key
# ============================================================

df = df.drop(
    columns=[
        "dedup_key"
    ]
)


# ============================================================
# 19. 顯示商品去重結果
# ============================================================

print()
print("=" * 60)
print("商品去重結果")
print("=" * 60)
print()

print(
    "去重前：",
    before_dedup,
    "筆"
)

print(
    "重複商品：",
    duplicate_count,
    "筆"
)

print(
    "去重後：",
    after_dedup,
    "筆"
)


# ============================================================
# 20. 缺失值檢查
# ============================================================

print()
print("=" * 60)
print("缺失值")
print("=" * 60)
print()

print(
    df.isnull().sum()
)


# ============================================================
# 21. 最終各來源分類商品數
# ============================================================

print()
print("=" * 60)
print("最終各來源分類商品數")
print("=" * 60)
print()

final_category_counts = (
    df["source_category"]
    .value_counts()
)

print(
    final_category_counts
)


# ============================================================
# 22. 價格基本統計
# ============================================================

print()
print("=" * 60)
print("商品價格基本統計")
print("=" * 60)
print()

print(
    "最低價格：",
    df["price"].min()
)

print(
    "最高價格：",
    df["price"].max()
)

print(
    "平均價格：",
    round(
        df["price"].mean(),
        2
    )
)


# ============================================================
# 23. 排序
# ============================================================

df = df.sort_values(
    by=[
        "source_category",
        "product_name"
    ]
)

df = df.reset_index(
    drop=True
)


# ============================================================
# 24. 調整欄位順序
# ============================================================

column_order = [

    "brand",

    "product_name",

    "product_id",

    "price",

    "product_url",

    "crawl_time",

    "source_category"
]

df = df[
    column_order
]


# ============================================================
# 25. 顯示最終資料
# ============================================================

print()
print("=" * 60)
print("最終資料預覽")
print("=" * 60)
print()

print(
    df.head(10)
)

print()


# ============================================================
# 26. 儲存 CSV
# ============================================================

df.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8-sig"
)


# ============================================================
# 27. 完成
# ============================================================

print()
print("=" * 60)
print("UNIQLO 女裝商品爬取完成")
print("=" * 60)
print()

print(
    "最終商品數：",
    len(df),
    "件"
)

print()

print(
    "CSV 儲存位置："
)

print(
    OUTPUT_FILE
)

print()

print(
    "資料欄位："
)

print(
    df.columns.tolist()
)

print()

print("=" * 60)
print("爬蟲完成！")
print("=" * 60)