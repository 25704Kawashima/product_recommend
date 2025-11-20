"""
このファイルは、画面表示に特化した関数定義のファイルです。
"""

############################################################
# ライブラリの読み込み
############################################################
import logging
import streamlit as st
import constants as ct
import utils


############################################################
# 関数定義
############################################################

def display_app_title():
    """
    タイトル表示
    """
    st.markdown(f"## {ct.APP_NAME}")


def display_initial_ai_message():
    """
    AIメッセージの初期表示
    """
    with st.chat_message("assistant", avatar=ct.AI_ICON_FILE_PATH):
        st.markdown("こちらは対話型の商品レコメンド生成AIアプリです。「こんな商品が欲しい」という情報・要望を画面下部のチャット欄から送信いただければ、おすすめの商品をレコメンドいたします。")
        st.markdown("**入力例**")
        st.info("""
        - 「長時間使える、高音質なワイヤレスイヤホン」
        - 「机のライト」
        - 「USBで充電できる加湿器」
        """)


def display_conversation_log():
    """
    会話ログの一覧表示
    """
    for message in st.session_state.messages:
        if message["role"] == "user":
            with st.chat_message("user", avatar=ct.USER_ICON_FILE_PATH):
                st.markdown(message["content"])
        else:
            with st.chat_message("assistant", avatar=ct.AI_ICON_FILE_PATH):
                display_product(message["content"])


def display_product(result):
    """
    商品情報の表示

    Args:
        result: LLMからの回答
    """
    logger = logging.getLogger(ct.LOGGER_NAME)

    # 応答が期待どおりかチェックしてから丁寧にパースする
    try:
        if not result or not isinstance(result, (list, tuple)):
            raise ValueError("レスポンスが空またはリストではありません")
        doc = result[0]
        page = getattr(doc, "page_content", None)
        if not page:
            raise ValueError("page_content が存在しません")

        product_lines = [line.strip() for line in page.splitlines() if line.strip()]
        product = {}
        # ラベルの正規化マップ（必要に応じて追加）
        label_map = {
            "商品名": "name", "name": "name",
            "商品id": "id", "id": "id", "商品ID": "id",
            "価格": "price", "price": "price",
            "商品カテゴリ": "category", "カテゴリ": "category", "category": "category",
            "メーカー": "maker", "maker": "maker",
            "評価": "score", "score": "score",
            "レビュー件数": "review_number", "review_number": "review_number",
            "ファイル名": "file_name", "file_name": "file_name",
            "説明": "description", "商品説明": "description", "description": "description",
            "おすすめ対象": "recommended_people", "こんな方におすすめ": "recommended_people", "recommended_people": "recommended_people"
        }

        last_key = None
        for item in product_lines:
            if ": " in item:
                key, val = item.split(": ", 1)
            elif ":" in item:
                key, val = item.split(":", 1)
            else:
                # コロンがない行は直前のフィールド（例: 説明の続き）に追加
                if last_key:
                    product[last_key] = product.get(last_key, "") + "\n" + item
                continue
            key = key.strip()
            val = val.strip()
            norm_key = label_map.get(key, key).strip().lower()
            product[norm_key] = val
            last_key = norm_key

        # 必須キーの検証
        for k in ("id", "name", "price"):
            if k not in product:
                raise KeyError(k)

    except Exception as e:
        logger.error(f"{ct.LLM_RESPONSE_DISP_ERROR_MESSAGE}\n{e}")
        st.error(utils.build_error_message(ct.LLM_RESPONSE_DISP_ERROR_MESSAGE))
        return

    st.markdown("以下の商品をご提案いたします。")

    # 「商品名」と「価格」
    st.success(f"""
            商品名：{product.get('name','-')}（商品ID: {product.get('id','-')}）\n
            価格：{product.get('price','-')}
    """)

    # 在庫状況によって表示
    if product.get('stock_status') == "残りわずか":
        st.warning("ご好評につき、在庫数残りわずかです。購入を希望の場合、お早めの注文をおすすめします。")
    elif product.get('stock_status') == "なし":
        st.error("申し訳ございませんが、現在在庫切れとなっております。入荷まで今しばらくお待ちください。")

    # 「商品カテゴリ」と「メーカー」と「ユーザー評価」
    st.code(f"""
        商品カテゴリ：{product['category']}\n
        メーカー：{product['maker']}\n
        評価：{product['score']}({product['review_number']}件)
    """, language=None, wrap_lines=True)

    # 商品画像
    st.image(f"images/products/{product['file_name']}", width=400)

    # 商品説明
    st.code(product['description'], language=None, wrap_lines=True)

    # おすすめ対象ユーザー
    st.markdown("**こんな方におすすめ！**")
    st.info(product["recommended_people"])

    # 商品ページのリンク
    st.link_button("商品ページを開く", type="primary", use_container_width=True, url="https://google.com")