import streamlit as st
import pandas as pd
from data_fetcher import main_fetch_all

# ページ全体をワイド表示に
st.set_page_config(layout="wide")

def load_data() -> pd.DataFrame:
    """CSV を読み込む。ない場合は空DataFrameを返す"""
    try:
        return pd.read_csv("sheet_query_data.csv", encoding="utf-8-sig")
    except:
        return pd.DataFrame()

def streamlit_main():
    # -- ページ先頭で書式を定義するCSS --
    #   ここで table.customtable に対して border-radius 等を設定
    st.markdown(
        """
        <style>
        /* テキストボックスの幅を狭く */
        input[type=text] {
            width: 150px !important;
        }

        /* HTMLテーブルの角丸・枠線などのスタイル */
        table.customtable {
            border-collapse: separate;
            border-spacing: 0;
            border: 1px solid #ddd;
            border-radius: 8px;
            overflow: hidden; /* 角丸を適用するため */
            width: 100%;
        }
        table.customtable thead tr:first-child th:first-child {
            border-top-left-radius: 8px;
        }
        table.customtable thead tr:first-child th:last-child {
            border-top-right-radius: 8px;
        }
        table.customtable tbody tr:last-child td:first-child {
            border-bottom-left-radius: 8px;
        }
        table.customtable tbody tr:last-child td:last-child {
            border-bottom-right-radius: 8px;
        }

        /* 各セルの最小幅を抑えたい場合、max-width等を追加で指定可 */
        table.customtable td, table.customtable th {
            padding: 6px 8px;
            max-width: 150px;       /* 必要に応じて幅を固定 */
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown("## 項目の定義\n- **CV** : コンバージョン（アプリのダウンロード数 等）")

    # CSV をロード
    df = load_data()
    if df.empty:
        st.warning("まだデータがありません。CSVが空か、データ取得がまだかもしれません。")
        return

    # 数値列を小数点以下1桁に丸める
    numeric_cols = df.select_dtypes(include=['float','int']).columns
    df[numeric_cols] = df[numeric_cols].round(1)

    # page_view の合計を上部に表示
    if "page_view" in df.columns:
        df["page_view_numeric"] = pd.to_numeric(df["page_view"], errors="coerce").fillna(0)
        total_pv = df["page_view_numeric"].sum()
        st.metric("page_view の合計", f"{total_pv}")

    # タイトル検索（部分一致）
    title_search = st.text_input("タイトル検索（部分一致）")
    if title_search and "title" in df.columns:
        df = df[df["title"].astype(str).str.contains(title_search, na=False)]

    # ID検索（部分一致）
    id_search = st.text_input("ID検索（部分一致）")
    if id_search and "id" in df.columns:
        df = df[df["id"].astype(str).str.contains(id_search, na=False)]

    # カテゴリ分割とプルダウンフィルタ
    if "category" in df.columns:
        df["split_categories"] = df["category"].fillna("").apply(
            lambda x: [c.strip() for c in x.split(",") if c.strip()]
        )
        cat_set = set()
        for cats in df["split_categories"]:
            cat_set.update(cats)
        unique_cats = sorted(cat_set)
        category_selected = st.selectbox("category を絞り込み", ["すべて"] + unique_cats)
        if category_selected != "すべて":
            df = df[df["split_categories"].apply(lambda catlist: category_selected in catlist)]

    st.write("### query_貼付 シート CSV のビューワー")

    # URLをクリック可能に (HTMLリンク化)
    if "URL" in df.columns:
        def make_clickable(url):
            url = str(url)
            if url.startswith("http"):
                return f'<a href="{url}" target="_blank">{url}</a>'
            else:
                return url
        df["URL"] = df["URL"].apply(make_clickable)

    # HTMLテーブルとして表示し、CSSクラスを customtable に
    html_table = df.to_html(
        escape=False,
        index=False,
        classes=["customtable"]  # 角丸CSSを適用するため
    )
    st.write(html_table, unsafe_allow_html=True)

if __name__ == "__main__":
    streamlit_main()
