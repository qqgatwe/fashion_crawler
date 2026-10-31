import re
import time
import pandas as pd

from pathlib import Path
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# ============================================================
# 0. 專案路徑設定
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

RAW_DIR = BASE_DIR / "data" / "raw"
CLEANED_DIR = BASE_DIR / "data" / "cleaned"

RAW_DIR.mkdir(
    parents=True,
    exist_ok=True
)

CLEANED_DIR.mkdir(
    parents=True,
    exist_ok=True
)

RAW_FILE = (
    RAW_DIR /
    "gu_products_raw.csv"
)

CLEANED_FILE = (
    CLEANED_DIR /
    "gu_products.csv"
)


# ============================================================
# 1. GU 女裝分類網址
# ============================================================

CATEGORY_URLS = {

    "T恤・背心・TUNIC裙襬上衣":
        "https://www.gu-global.com/tw/zh_TW/c/women_tshirtsweat.html",

    "襯衫・設計上衣":
        "https://www.gu-global.com/tw/zh_TW/c/women_shirtsandblouses_shirtsandblouses.html",

    "針織上衣・開襟外套":
        "https://www.gu-global.com/tw/zh_TW/c/women_knitandcardigan.html",

    "外套":
        "https://www.gu-global.com/tw/zh_TW/c/women_outer.html"
}


# ============================================================
# 2. 建立 Chrome
# ============================================================

def create_driver():

    options = Options()

    # --------------------------------------------------------
    # 目前先不要使用 headless
    # 方便確認網頁是否正常載入
    # --------------------------------------------------------

    options.add_argument(
        "--start-maximized"
    )

    options.add_argument(
        "--disable-blink-features=AutomationControlled"
    )

    options.add_argument(
        "--disable-notifications"
    )

    options.add_argument(
        "--disable-popup-blocking"
    )

    options.add_argument(
        "--no-sandbox"
    )

    options.add_argument(
        "--disable-dev-shm-usage"
    )

    options.add_argument(
        "--user-agent="
        "Mozilla/5.0 "
        "(Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/140.0.0.0 "
        "Safari/537.36"
    )

    driver = webdriver.Chrome(
        options=options
    )

    driver.set_page_load_timeout(
        60
    )

    return driver


# ============================================================
# 3. 清理文字
# ============================================================

def clean_text(text):

    if text is None:

        return ""

    text = str(text)

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ============================================================
# 4. 自動捲動頁面
# ============================================================

def auto_scroll(driver):

    print()
    print("開始自動捲動頁面...")

    last_height = 0
    stable_count = 0

    for scroll_count in range(
        1,
        31
    ):

        try:

            current_height = (
                driver.execute_script(
                    "return document.body.scrollHeight"
                )
            )

            driver.execute_script(
                "window.scrollTo("
                "0, document.body.scrollHeight"
                ");"
            )

            time.sleep(
                2
            )

            new_height = (
                driver.execute_script(
                    "return document.body.scrollHeight"
                )
            )

            print(
                f"捲動第 {scroll_count} 次"
                f" | 頁面高度：{new_height}"
            )

            if new_height == last_height:

                stable_count += 1

            else:

                stable_count = 0

            last_height = new_height

            # ------------------------------------------------
            # 連續三次高度沒有變化
            # ------------------------------------------------

            if stable_count >= 3:

                print(
                    "頁面高度已穩定，停止捲動。"
                )

                break

        except Exception as e:

            print(
                "捲動發生錯誤：",
                e
            )

            break

    # --------------------------------------------------------
    # 回到最上方
    # --------------------------------------------------------

    driver.execute_script(
        "window.scrollTo(0, 0);"
    )

    time.sleep(
        1
    )

    print(
        "頁面捲動完成！"
    )


# ============================================================
# 5. 從分類頁取得商品網址
# ============================================================

def get_product_links(driver):

    links = []

    # --------------------------------------------------------
    # 抓頁面所有有 href 的 a 標籤
    # --------------------------------------------------------

    elements = driver.find_elements(
        By.CSS_SELECTOR,
        "a[href]"
    )

    print()
    print(
        "頁面找到全部連結：",
        len(elements),
        "個"
    )

    all_gu_links = []

    # --------------------------------------------------------
    # 第一階段：
    # 先取得所有 GU 網站連結
    # --------------------------------------------------------

    for element in elements:

        try:

            href = element.get_attribute(
                "href"
            )

            if not href:

                continue

            href = href.strip()

            if "gu-global.com/tw/" not in href:

                continue

            href = href.split(
                "#"
            )[0]

            all_gu_links.append(
                href
            )

        except Exception:

            continue

    # --------------------------------------------------------
    # 去除重複網址
    # --------------------------------------------------------

    all_gu_links = list(
        dict.fromkeys(
            all_gu_links
        )
    )

    print(
        "其中 GU 網站連結：",
        len(all_gu_links),
        "個"
    )

    # --------------------------------------------------------
    # 第二階段：
    # 判斷哪些可能是商品頁
    # --------------------------------------------------------

    for href in all_gu_links:

        # ----------------------------------------------------
        # 分類頁直接排除
        # ----------------------------------------------------

        if "/c/" in href:

            continue

        # ----------------------------------------------------
        # 排除常見非商品頁
        # ----------------------------------------------------

        exclude_keywords = [

            "/login",

            "/cart",

            "/search",

            "/member",

            "/account",

            "/category",

            "/faq",

            "/help",

            "/guide",

            "/about",

            "/news",

            "/feature",

            "/special"
        ]

        if any(
            keyword in href.lower()
            for keyword in exclude_keywords
        ):

            continue

        # ----------------------------------------------------
        # 判斷網址是否有 6 位商品編號
        # ----------------------------------------------------

        product_id_match = re.search(
            r"(?<!\d)(\d{6})(?!\d)",
            href
        )

        # ----------------------------------------------------
        # 商品網址特徵
        #
        # GU 網址結構可能調整，
        # 因此使用多種方式判斷
        # ----------------------------------------------------

        possible_product_url = (

            product_id_match is not None

            or "/products/" in href.lower()

            or "/product/" in href.lower()

            or "productdetail" in href.lower()

            or "product-detail" in href.lower()

            or "productid=" in href.lower()

            or "productcode=" in href.lower()
        )

        if possible_product_url:

            links.append(
                href
            )

    # --------------------------------------------------------
    # 去除重複網址
    # --------------------------------------------------------

    links = list(
        dict.fromkeys(
            links
        )
    )

    print(
        "篩選後商品網址：",
        len(links),
        "個"
    )

    # --------------------------------------------------------
    # 有找到商品網址
    # --------------------------------------------------------

    if links:

        print()
        print(
            "前 5 個商品網址："
        )

        for link in links[:5]:

            print(
                " -",
                link
            )

    # --------------------------------------------------------
    # 完全沒找到時
    #
    # 顯示部分 GU 網址協助確認網站結構
    # --------------------------------------------------------

    else:

        print()
        print(
            "⚠ 沒有找到商品網址。"
        )

        print()
        print(
            "以下顯示前 20 個 GU 網站網址："
        )

        for link in all_gu_links[:20]:

            print(
                " -",
                link
            )

    return links


# ============================================================
# 6. 從商品名稱取得商品 ID
# ============================================================

def extract_id_from_name(
    product_name
):

    if not product_name:

        return None

    matches = re.findall(
        r"(?<!\d)(\d{6})(?!\d)",
        str(product_name)
    )

    if matches:

        # ----------------------------------------------------
        # 如果名稱有多個商品編號
        # 先使用最後一個
        # ----------------------------------------------------

        return matches[-1]

    return None


# ============================================================
# 7. 從網址取得商品 ID
# ============================================================

def extract_id_from_url(
    url
):

    if not url:

        return None

    patterns = [

        r"/product/(\d{6})",

        r"/products/(\d{6})",

        r"productCode=(\d{6})",

        r"productId=(\d{6})",

        r"(?<!\d)(\d{6})(?!\d)"
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            str(url),
            flags=re.IGNORECASE
        )

        if match:

            return match.group(
                1
            )

    return None


# ============================================================
# 8. 移除商品名稱尾端 ID
# ============================================================

def remove_id_from_name(
    product_name
):

    if not product_name:

        return ""

    product_name = clean_text(
        product_name
    )

    # --------------------------------------------------------
    # 移除名稱尾端商品編號
    #
    # 例如：
    #
    # 女裝 牛津短版襯衫 357534
    #
    # →
    #
    # 女裝 牛津短版襯衫
    # --------------------------------------------------------

    product_name = re.sub(
        r"\s+\d{6}\s*$",
        "",
        product_name
    )

    return product_name.strip()


# ============================================================
# 9. 取得商品名稱
# ============================================================

def get_product_name(
    driver
):

    selectors = [

        "h1",

        "[class*='product-name']",

        "[class*='productName']",

        "[class*='ProductName']",

        "[data-testid*='product-name']",

        "[data-test*='product-name']"
    ]

    for selector in selectors:

        try:

            elements = driver.find_elements(
                By.CSS_SELECTOR,
                selector
            )

            for element in elements:

                text = clean_text(
                    element.text
                )

                if not text:

                    continue

                invalid_names = [

                    "商品詳情",

                    "商品說明",

                    "商品資訊",

                    "GU",

                    "購物車"
                ]

                if text in invalid_names:

                    continue

                if len(text) >= 4:

                    return text

        except Exception:

            continue

    # --------------------------------------------------------
    # 備援：使用網頁標題
    # --------------------------------------------------------

    try:

        title = clean_text(
            driver.title
        )

        title = re.sub(
            r"\s*[｜|]\s*GU.*$",
            "",
            title
        )

        if len(title) >= 4:

            return title

    except Exception:

        pass

    return None


# ============================================================
# 10. 取得商品價格
# ============================================================

def get_price(
    driver
):

    price_candidates = []

    selectors = [

        "[class*='price']",

        "[class*='Price']",

        "[data-testid*='price']",

        "[data-test*='price']"
    ]

    for selector in selectors:

        try:

            elements = driver.find_elements(
                By.CSS_SELECTOR,
                selector
            )

            for element in elements:

                text = clean_text(
                    element.text
                )

                if text:

                    price_candidates.append(
                        text
                    )

        except Exception:

            continue

    # --------------------------------------------------------
    # 優先找有 NT$ 的價格
    # --------------------------------------------------------

    patterns = [

        r"NT\$\s*([\d,]+)",

        r"NT\s*\$\s*([\d,]+)",

        r"NTD\s*([\d,]+)",

        r"\$\s*([\d,]+)"
    ]

    for text in price_candidates:

        for pattern in patterns:

            match = re.search(
                pattern,
                text,
                flags=re.IGNORECASE
            )

            if match:

                try:

                    price = int(
                        match
                        .group(1)
                        .replace(",", "")
                    )

                    if 50 <= price <= 20000:

                        return price

                except ValueError:

                    continue

    # --------------------------------------------------------
    # 備援：
    # 從整個頁面尋找 NT$ 價格
    # --------------------------------------------------------

    try:

        body_text = (
            driver.find_element(
                By.TAG_NAME,
                "body"
            )
            .text
        )

        matches = re.findall(
            r"NT\s*\$?\s*([\d,]+)",
            body_text,
            flags=re.IGNORECASE
        )

        for value in matches:

            try:

                price = int(
                    value.replace(
                        ",",
                        ""
                    )
                )

                if 50 <= price <= 20000:

                    return price

            except ValueError:

                continue

    except Exception:

        pass

    return None


# ============================================================
# 11. 判斷是否為女裝
# ============================================================

def is_women_product(
    product_name
):

    if not product_name:

        return False

    name = str(
        product_name
    )

    # --------------------------------------------------------
    # 排除男裝
    # --------------------------------------------------------

    exclude_keywords = [

        "男裝",

        "男款",

        "MEN",

        "Men",

        "men"
    ]

    for keyword in exclude_keywords:

        if keyword in name:

            # ------------------------------------------------
            # 如果明確寫女裝，就不要因為其他文字誤殺
            # ------------------------------------------------

            if "女裝" not in name:

                return False

    # --------------------------------------------------------
    # 男女適穿目前排除
    #
    # 因為我們要拿 GU 女裝跟 UNIQLO 女裝比較
    # --------------------------------------------------------

    if "男女適穿" in name:

        return False

    return True


# ============================================================
# 12. 爬取單一商品
# ============================================================

def scrape_product(
    driver,
    product_url,
    source_category
):

    try:

        driver.get(
            product_url
        )

        WebDriverWait(
            driver,
            20
        ).until(

            EC.presence_of_element_located(

                (
                    By.TAG_NAME,
                    "body"
                )

            )

        )

        time.sleep(
            1.5
        )

        # ----------------------------------------------------
        # 商品名稱
        # ----------------------------------------------------

        raw_name = get_product_name(
            driver
        )

        if not raw_name:

            print(
                "找不到商品名稱"
            )

            return None

        # ----------------------------------------------------
        # 商品 ID
        # ----------------------------------------------------

        product_id = extract_id_from_name(
            raw_name
        )

        if not product_id:

            product_id = extract_id_from_url(
                product_url
            )

        # ----------------------------------------------------
        # 清理商品名稱
        # ----------------------------------------------------

        product_name = remove_id_from_name(
            raw_name
        )

        # ----------------------------------------------------
        # 價格
        # ----------------------------------------------------

        price = get_price(
            driver
        )

        # ----------------------------------------------------
        # 爬取時間
        # ----------------------------------------------------

        crawl_time = (
            datetime.now()
            .strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        )

        return {

            "brand":
                "GU",

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
                source_category
        }

    except Exception as e:

        print(
            "商品讀取失敗：",
            product_url
        )

        print(
            "錯誤：",
            e
        )

        return None


# ============================================================
# 13. 清理 GU 資料
# ============================================================

def clean_gu_data(
    df
):

    print()
    print("=" * 60)
    print("開始清理 GU 商品資料")
    print("=" * 60)
    print()

    original_count = len(
        df
    )

    print(
        "原始資料：",
        original_count,
        "件"
    )

    # ========================================================
    # 商品名稱
    # ========================================================

    df["product_name"] = (

        df["product_name"]
        .astype(str)
        .str.strip()

    )

    # ========================================================
    # 移除錯誤商品名稱
    # ========================================================

    invalid_names = [

        "",

        "None",

        "nan",

        "商品詳情",

        "商品資訊",

        "商品說明"
    ]

    before = len(
        df
    )

    df = df[

        ~df["product_name"].isin(
            invalid_names
        )

    ].copy()

    print(
        "移除錯誤商品名稱：",
        before - len(df),
        "件"
    )

    # ========================================================
    # 修復商品 ID
    # ========================================================

    def repair_product_id(
        row
    ):

        value = row[
            "product_id"
        ]

        if pd.isna(value):

            product_id = ""

        else:

            product_id = str(
                value
            ).strip()

        invalid_ids = [

            "",

            "000000",

            "None",

            "none",

            "nan",

            "NaN"
        ]

        if product_id in invalid_ids:

            # ------------------------------------------------
            # 先從商品名稱找
            # ------------------------------------------------

            new_id = extract_id_from_name(
                row["product_name"]
            )

            if new_id:

                return new_id

            # ------------------------------------------------
            # 再從網址找
            # ------------------------------------------------

            new_id = extract_id_from_url(
                row["product_url"]
            )

            if new_id:

                return new_id

            return None

        # ----------------------------------------------------
        # Excel / pandas 有時會變成 357534.0
        # ----------------------------------------------------

        product_id = re.sub(
            r"\.0$",
            "",
            product_id
        )

        return product_id

    df["product_id"] = df.apply(
        repair_product_id,
        axis=1
    )

    # ========================================================
    # 再次清理商品名稱中的 ID
    # ========================================================

    df["product_name"] = (

        df["product_name"]
        .apply(
            remove_id_from_name
        )

    )

    # ========================================================
    # 移除沒有商品 ID
    # ========================================================

    before = len(
        df
    )

    df = df[

        df["product_id"]
        .notna()

    ].copy()

    print(
        "移除沒有商品 ID：",
        before - len(df),
        "件"
    )

    # ========================================================
    # 價格轉數字
    # ========================================================

    df["price"] = pd.to_numeric(

        df["price"],

        errors="coerce"

    )

    # ========================================================
    # 移除沒有價格
    # ========================================================

    before = len(
        df
    )

    df = df[

        df["price"]
        .notna()

    ].copy()

    print(
        "移除沒有價格：",
        before - len(df),
        "件"
    )

    df["price"] = (

        df["price"]
        .astype(int)

    )

    # ========================================================
    # 排除男裝 / 男女適穿
    # ========================================================

    before = len(
        df
    )

    df = df[

        df["product_name"]
        .apply(
            is_women_product
        )

    ].copy()

    print(
        "移除男裝 / 男女適穿：",
        before - len(df),
        "件"
    )

    # ========================================================
    # 檢查跨分類重複商品
    # ========================================================

    duplicated = df[

        df.duplicated(
            subset=[
                "product_id"
            ],
            keep=False
        )

    ].copy()

    print()
    print("=" * 60)
    print("跨分類重複商品檢查")
    print("=" * 60)
    print()

    print(
        "重複紀錄：",
        len(duplicated),
        "筆"
    )

    if not duplicated.empty:

        print()

        print(

            duplicated[

                [
                    "product_id",
                    "product_name",
                    "price",
                    "source_category"
                ]

            ]
            .sort_values(
                by="product_id"
            )
            .to_string(
                index=False
            )

        )

    # ========================================================
    # 移除重複商品
    # ========================================================

    before = len(
        df
    )

    df = df.drop_duplicates(

        subset=[
            "product_id"
        ],

        keep="first"

    ).copy()

    print()
    print(
        "移除重複商品：",
        before - len(df),
        "件"
    )

    # ========================================================
    # 統一 gender
    # ========================================================

    df["gender"] = "女裝"

    # ========================================================
    # 排序
    # ========================================================

    df = df.sort_values(

        by=[
            "source_category",
            "product_id"
        ]

    )

    df = df.reset_index(
        drop=True
    )

    print()
    print("=" * 60)
    print("清理完成")
    print("=" * 60)
    print()

    print(
        "原始商品數：",
        original_count
    )

    print(
        "最終女裝商品數：",
        len(df)
    )

    return df


# ============================================================
# 14. 主程式
# ============================================================

def main():

    print()
    print("=" * 60)
    print("GU 女裝商品爬蟲")
    print("=" * 60)
    print()

    print(
        "共有",
        len(CATEGORY_URLS),
        "個分類"
    )

    driver = create_driver()

    all_products = []

    try:

        # ====================================================
        # 逐分類爬取
        # ====================================================

        for category_index, (
            category_name,
            category_url
        ) in enumerate(
            CATEGORY_URLS.items(),
            start=1
        ):

            print()
            print("=" * 60)

            print(
                f"[{category_index}/"
                f"{len(CATEGORY_URLS)}]"
            )

            print()

            print(
                "正在爬取分類：",
                category_name
            )

            print(
                "網址：",
                category_url
            )

            print("=" * 60)

            # =================================================
            # 開啟分類頁
            # =================================================

            driver.get(
                category_url
            )

            WebDriverWait(
                driver,
                30
            ).until(

                EC.presence_of_element_located(

                    (
                        By.TAG_NAME,
                        "body"
                    )

                )

            )

            time.sleep(
                3
            )

            print()
            print(
                "目前網址：",
                driver.current_url
            )

            print(
                "網頁標題：",
                driver.title
            )

            # =================================================
            # 自動捲動
            # =================================================

            auto_scroll(
                driver
            )

            # =================================================
            # 找商品網址
            # =================================================

            product_links = get_product_links(
                driver
            )

            print()
            print(
                "找到商品網址：",
                len(product_links),
                "個"
            )

            # =================================================
            # 如果沒有商品網址
            # 不要讓整個程式失敗
            # =================================================

            if not product_links:

                print()
                print(
                    "⚠ 此分類沒有找到商品網址，"
                    "跳到下一個分類。"
                )

                continue

            category_success = 0

            # =================================================
            # 逐商品爬取
            # =================================================

            for product_index, product_url in enumerate(
                product_links,
                start=1
            ):

                print()
                print(
                    f"[{product_index}/"
                    f"{len(product_links)}] "
                    "正在讀取商品..."
                )

                product = scrape_product(

                    driver,

                    product_url,

                    category_name

                )

                if product is None:

                    print(
                        "商品讀取失敗"
                    )

                    continue

                print(
                    "商品名稱：",
                    product[
                        "product_name"
                    ]
                )

                print(
                    "商品編號：",
                    product[
                        "product_id"
                    ]
                )

                print(
                    "商品價格：",
                    product[
                        "price"
                    ]
                )

                # ------------------------------------------------
                # 女裝判斷
                # ------------------------------------------------

                if not is_women_product(
                    product[
                        "product_name"
                    ]
                ):

                    print(
                        "→ 男裝 / 男女適穿，"
                        "之後會排除"
                    )

                all_products.append(
                    product
                )

                category_success += 1

            print()
            print("-" * 60)

            print(
                category_name,
                "完成"
            )

            print(
                "成功取得：",
                category_success,
                "件"
            )

            print("-" * 60)

    finally:

        driver.quit()

        print()
        print(
            "Chrome 已關閉。"
        )

    # ========================================================
    # 檢查是否有資料
    # ========================================================

    print()
    print("=" * 60)
    print("建立 GU 商品資料...")
    print("=" * 60)
    print()

    if not all_products:

        print(
            "沒有取得任何商品資料。"
        )

        print()
        print(
            "請查看上方「前 20 個 GU 網站網址」，"
            "確認 GU 現在實際使用的商品網址格式。"
        )

        return

    # ========================================================
    # 建立 DataFrame
    # ========================================================

    df_raw = pd.DataFrame(
        all_products
    )

    # ========================================================
    # RAW 資料
    # ========================================================

    df_raw.to_csv(

        RAW_FILE,

        index=False,

        encoding="utf-8-sig"

    )

    print(
        "RAW 資料已儲存："
    )

    print(
        RAW_FILE
    )

    # ========================================================
    # RAW 基本資訊
    # ========================================================

    print()
    print("=" * 60)
    print("RAW 資料資訊")
    print("=" * 60)
    print()

    print(
        "RAW 商品數：",
        len(df_raw)
    )

    print()
    print(
        "資料欄位："
    )

    print(
        list(
            df_raw.columns
        )
    )

    print()
    print(
        "缺失值："
    )

    print(
        df_raw.isnull().sum()
    )

    # ========================================================
    # 清理資料
    # ========================================================

    df_clean = clean_gu_data(
        df_raw.copy()
    )

    # ========================================================
    # 儲存 cleaned
    # ========================================================

    df_clean.to_csv(

        CLEANED_FILE,

        index=False,

        encoding="utf-8-sig"

    )

    # ========================================================
    # 各分類商品數
    # ========================================================

    print()
    print("=" * 60)
    print("各分類商品數")
    print("=" * 60)
    print()

    category_counts = (

        df_clean[
            "source_category"
        ]
        .value_counts()

    )

    print(
        category_counts
    )

    # ========================================================
    # 價格統計
    # ========================================================

    if not df_clean.empty:

        print()
        print("=" * 60)
        print("價格統計")
        print("=" * 60)
        print()

        print(
            "平均價格：",
            round(
                df_clean[
                    "price"
                ].mean(),
                2
            ),
            "元"
        )

        print(
            "中位數價格：",
            df_clean[
                "price"
            ].median(),
            "元"
        )

        print(
            "最低價格：",
            int(
                df_clean[
                    "price"
                ].min()
            ),
            "元"
        )

        print(
            "最高價格：",
            int(
                df_clean[
                    "price"
                ].max()
            ),
            "元"
        )

    # ========================================================
    # 商品 ID 檢查
    # ========================================================

    print()
    print("=" * 60)
    print("商品 ID 檢查")
    print("=" * 60)
    print()

    invalid_id_count = (

        df_clean[
            "product_id"
        ]
        .astype(str)
        .isin(
            [
                "000000",
                "",
                "nan",
                "None"
            ]
        )
        .sum()

    )

    print(
        "錯誤商品 ID 數量：",
        invalid_id_count
    )

    # ========================================================
    # 顯示前 20 筆
    # ========================================================

    print()
    print("=" * 60)
    print("清理後前 20 筆商品")
    print("=" * 60)
    print()

    display_columns = [

        "brand",

        "gender",

        "source_category",

        "product_name",

        "product_id",

        "price"
    ]

    print(

        df_clean[
            display_columns
        ]
        .head(20)
        .to_string(
            index=False
        )

    )

    # ========================================================
    # 完成
    # ========================================================

    print()
    print("=" * 60)
    print("GU 女裝商品爬蟲完成")
    print("=" * 60)
    print()

    print(
        "原始資料：",
        len(df_raw),
        "件"
    )

    print(
        "清理後女裝資料：",
        len(df_clean),
        "件"
    )

    print()

    print(
        "RAW 檔案："
    )

    print(
        RAW_FILE
    )

    print()

    print(
        "CLEANED 檔案："
    )

    print(
        CLEANED_FILE
    )

    print()
    print(
        "GU 資料處理完成！"
    )


# ============================================================
# 15. 執行程式
# ============================================================

if __name__ == "__main__":

    main()