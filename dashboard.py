import streamlit as st
from datetime import datetime, timedelta
from db.database import init_db, get_articles, get_stats, toggle_featured, get_featured, get_archive
from config import THEMES

def format_date(date_str):
    """YYYY-MM-DD を年月日形式に変換"""
    if not date_str:
        return ""
    try:
        dt = datetime.strptime(date_str[:10], "%Y-%m-%d")
        return dt.strftime("%Y年%-m月%-d日").replace("%-m", str(dt.month)).replace("%-d", str(dt.day))
    except:
        return date_str

st.set_page_config(
    page_title="Intelligence Agent",
    page_icon="🔍",
    layout="wide",
)

init_db()

# Streamlit Cloud では毎朝7時に GitHub Actions で自動収集されます
# ローカル開発時の自動スケジューラは削除（GitHub Actions に統一）

# エキスパンダーの見出しを大きく・濃くするCSS
st.markdown("""
<style>
/* エキスパンダーのラベル文字 */
[data-testid="stExpander"] summary p {
    font-size: 17px !important;
    font-weight: 700 !important;
    color: #111111 !important;
    line-height: 1.5 !important;
}
[data-testid="stExpander"] summary:hover p {
    color: #333333 !important;
}
</style>
""", unsafe_allow_html=True)

# スケジューラは GitHub Actions で管理（毎朝7時 UTC に collect を実行）

# ─── サイドバー ───────────────────────────────────────────
st.sidebar.title("🔍 Intelligence Agent")
st.sidebar.caption("テーマ別トレンド収集＆提案ヒント")

theme_options = ["すべて"] + list(THEMES.keys())
selected_theme = st.sidebar.radio("テーマを選択", theme_options)

st.sidebar.divider()
stats = get_stats()
st.sidebar.metric("総収集件数", stats["total"])
for t, cnt in stats["by_theme"].items():
    color = THEMES[t]["color"]
    st.sidebar.markdown(f'<span style="color:{color}">●</span> {t}: **{cnt}件**', unsafe_allow_html=True)

st.sidebar.divider()
if st.sidebar.button("🔄 今すぐ収集する"):
    with st.spinner("収集中（1〜2分）..."):
        try:
            from collectors.rss import collect_rss
            from collectors.arxiv import collect_arxiv
            rss_count = collect_rss()
            arxiv_count = collect_arxiv()
            st.sidebar.success(f"収集完了！ RSS:{rss_count}件, arXiv:{arxiv_count}件")
        except Exception as e:
            st.sidebar.error(f"エラー: {str(e)[:80]}")
            import traceback
            st.sidebar.write(traceback.format_exc()[:200])
    st.rerun()

# ─── ヘルパー ─────────────────────────────────────────────
def badge(theme, color):
    return (
        f'<span style="display:inline-block;background:{color};color:#fff;'
        f'font-size:12px;font-weight:bold;padding:3px 10px;border-radius:12px;'
        f'margin-right:6px;">{theme}</span>'
    )

def source_chip(source):
    return (
        f'<span style="display:inline-block;background:#f0f0f0;color:#444;'
        f'font-size:12px;padding:2px 8px;border-radius:8px;margin-right:4px;">'
        f'📰 {source}</span>'
    )

def render_card(art):
    color = THEMES.get(art["theme"], {}).get("color", "#888")
    title_ja = art.get("title_ja") or art["title"]
    title_en = art["title"].replace("[論文] ", "")
    pub = format_date(art.get("published_at", ""))
    src = art.get("source", "")
    return f"""
<div style="border-left:4px solid {color};padding:14px 18px;margin-bottom:12px;background:#fafafa;border-radius:6px;">
  <div style="margin-bottom:8px;">{badge(art['theme'], color)}{source_chip(src)}<span style="font-size:13px;color:#666;font-weight:500;">{pub}</span></div>
  <div style="font-size:21px;font-weight:bold;color:#111;margin-bottom:4px;line-height:1.4;">{title_ja[:80]}</div>
  <div style="font-size:14px;color:#888;margin-bottom:10px;">{title_en[:90]}</div>
  <a href="{art['url']}" target="_blank" style="font-size:14px;color:{color};text-decoration:none;font-weight:bold;">元記事を読む →</a>
</div>
"""

# ─── メインエリア ─────────────────────────────────────────
title = selected_theme if selected_theme != "すべて" else "全テーマ"
st.title(f"📊 {title} — 最新インテリジェンス")

articles = get_articles(theme=selected_theme, limit=60)

if not articles:
    st.info("まだデータがありません。サイドバーの「今すぐ収集する」を押してください。")
    st.stop()

papers = [a for a in articles if a["content_type"] == "paper"]
news   = [a for a in articles if a["content_type"] == "news"]

# ─── ハイライト ───────────────────────────────────────────
st.subheader("⚡ 今週のハイライト")
highlights = news[:6]
if highlights:
    cols = st.columns(min(len(highlights), 3))
    for i, art in enumerate(highlights):
        with cols[i % 3]:
            st.markdown(render_card(art), unsafe_allow_html=True)
else:
    st.caption("最新ニュースはまだ収集されていません。論文は下のセクションをご覧ください。")

st.divider()

# ─── ニュース一覧＋提案ヒント ────────────────────────────
st.subheader("📰 ニュース一覧＋提案ヒント")

themes_to_show = [selected_theme] if selected_theme != "すべて" else list(THEMES.keys())

for theme in themes_to_show:
    # ニュースがなければ論文も含めて表示
    theme_news = [a for a in news if a["theme"] == theme]
    theme_papers = [a for a in papers if a["theme"] == theme]
    theme_all = theme_news + theme_papers
    if not theme_all:
        continue

    color = THEMES[theme]["color"]
    st.markdown(f'<h3 style="color:{color}">● {theme}</h3>', unsafe_allow_html=True)

    for art in theme_all[:12]:
        title_ja = art.get("title_ja") or art["title"]
        title_en = art["title"]
        icon = "🔬" if art["content_type"] == "paper" else "📄"
        is_featured = bool(art.get("featured"))
        star = "⭐" if is_featured else "☆"
        with st.expander(f"{icon} {title_ja[:60]}  ／  {title_en[:60]}"):
            color2 = THEMES.get(art["theme"], {}).get("color", "#888")
            col_meta, col_btn = st.columns([5, 1])
            with col_meta:
                st.markdown(
                    f'{badge(art["theme"], color2)}{source_chip(art["source"])}'
                    f'<span style="font-size:13px;color:#666;font-weight:500;">{format_date(art["published_at"])}</span>',
                    unsafe_allow_html=True
                )
            with col_btn:
                btn_label = f"{star} 注目"
                if st.button(btn_label, key=f"feat_{art['id']}"):
                    toggle_featured(art["id"])
                    st.rerun()
            st.markdown(
                f'<div style="font-size:20px;font-weight:bold;color:#111;margin:10px 0 4px;">{title_ja}</div>'
                f'<div style="font-size:13px;color:#888;margin-bottom:12px;">{title_en}</div>',
                unsafe_allow_html=True
            )
            st.markdown(f"**要旨：** {art['summary']}")
            st.markdown(f"**🎯 提案資料/メルマガへの示唆：** {art['action_hint']}")
            link_label = "論文を読む →" if art["content_type"] == "paper" else "元記事を読む →"
            st.markdown(f"[{link_label}]({art['url']})")

st.divider()

# ─── 論文ピックアップ ────────────────────────────────────
paper_list = [a for a in papers if a["theme"] not in [t for t in themes_to_show]]
if paper_list:
    st.subheader("📚 論文ピックアップ（arXiv）")
    for art in paper_list[:9]:
        color = THEMES.get(art["theme"], {}).get("color", "#888")
        title_ja = art.get("title_ja") or art["title"]
        title_en = art["title"].replace("[論文] ", "")
        is_featured = bool(art.get("featured"))
        star = "⭐" if is_featured else "☆"
        with st.expander(f"🔬 {title_ja[:55]}  ／  {title_en[:55]}"):
            col_meta, col_btn = st.columns([5, 1])
            with col_meta:
                st.markdown(
                    f'{badge(art["theme"], color)}{source_chip("arXiv")}'
                    f'<span style="font-size:12px;color:#aaa;">{art["published_at"]}</span>',
                    unsafe_allow_html=True
                )
            with col_btn:
                if st.button(f"{star} 注目", key=f"feat_p_{art['id']}"):
                    toggle_featured(art["id"])
                    st.rerun()
            st.markdown(f"**要旨：** {art['summary']}")
            st.markdown(f"**🎯 提案への示唆：** {art['action_hint']}")
            st.markdown(f"[論文を読む →]({art['url']})")

st.divider()

# ─── 過去コーナー（自動キュレーション） ────────────────
st.header("📌 過去のおすすめ")
st.caption("収集した記事・論文の中からスコアが高いものを自動的にピックアップしています。⭐ボタンで永久保存もできます。")

tab_auto, tab_saved = st.tabs(["🤖 自動ピックアップ", "⭐ 保存済み"])

with tab_auto:
    archive = get_archive(theme=selected_theme, limit=5)
    if not archive:
        st.info("まだデータが蓄積されていません。収集を重ねるとここに良い記事が自動選出されます。")
    else:
        archive_by_theme = {}
        for a in archive:
            archive_by_theme.setdefault(a["theme"], []).append(a)

        for theme, arts in archive_by_theme.items():
            color = THEMES.get(theme, {}).get("color", "#888")
            st.markdown(f'<h3 style="color:{color}">● {theme}</h3>', unsafe_allow_html=True)
            for art in arts:
                title_ja = art.get("title_ja") or art["title"]
                title_en = art["title"].replace("[論文] ", "")
                icon = "🔬" if art["content_type"] == "paper" else "📄"
                sc = art.get("score", 0)
                is_featured = bool(art.get("featured"))
                star = "⭐" if is_featured else "☆"
                with st.expander(f"{icon} {title_ja[:65]}  ／  {title_en[:65]}"):
                    col_meta, col_btn = st.columns([5, 1])
                    with col_meta:
                        st.markdown(
                            f'{badge(theme, color)}{source_chip(art["source"])}'
                            f'<span style="font-size:12px;color:#aaa;">{art["published_at"]} · スコア {sc}</span>',
                            unsafe_allow_html=True
                        )
                    with col_btn:
                        if st.button(f"{star} 保存", key=f"arc_feat_{art['id']}"):
                            toggle_featured(art["id"])
                            st.rerun()
                    st.markdown(
                        f'<div style="font-size:20px;font-weight:bold;color:#111;margin:10px 0 4px;">{title_ja}</div>'
                        f'<div style="font-size:13px;color:#888;margin-bottom:12px;">{title_en}</div>',
                        unsafe_allow_html=True
                    )
                    st.markdown(f"**要旨：** {art['summary']}")
                    st.markdown(f"**🎯 提案資料/メルマガへの示唆：** {art['action_hint']}")
                    link_label = "論文を読む →" if art["content_type"] == "paper" else "元記事を読む →"
                    st.markdown(f"[{link_label}]({art['url']})")

with tab_saved:
    featured_all = get_featured(theme=selected_theme)
    if not featured_all:
        st.info("まだ保存済み記事がありません。自動ピックアップや各記事の「☆ 注目」ボタンで保存できます。")
    else:
        featured_by_theme = {}
        for a in featured_all:
            featured_by_theme.setdefault(a["theme"], []).append(a)

        for theme, arts in featured_by_theme.items():
            color = THEMES.get(theme, {}).get("color", "#888")
            st.markdown(f'<h3 style="color:{color}">⭐ {theme}</h3>', unsafe_allow_html=True)
            for art in arts:
                title_ja = art.get("title_ja") or art["title"]
                title_en = art["title"].replace("[論文] ", "")
                icon = "🔬" if art["content_type"] == "paper" else "📄"
                with st.expander(f"{icon} {title_ja[:65]}  ／  {title_en[:65]}"):
                    col_meta, col_btn = st.columns([5, 1])
                    with col_meta:
                        st.markdown(
                            f'{badge(theme, color)}{source_chip(art["source"])}'
                            f'<span style="font-size:12px;color:#aaa;">{art["published_at"]}</span>',
                            unsafe_allow_html=True
                        )
                    with col_btn:
                        if st.button("⭐ 解除", key=f"unfeat_{art['id']}"):
                            toggle_featured(art["id"])
                            st.rerun()
                    st.markdown(
                        f'<div style="font-size:20px;font-weight:bold;color:#111;margin:10px 0 4px;">{title_ja}</div>'
                        f'<div style="font-size:13px;color:#888;margin-bottom:12px;">{title_en}</div>',
                        unsafe_allow_html=True
                    )
                    st.markdown(f"**要旨：** {art['summary']}")
                    st.markdown(f"**🎯 提案資料/メルマガへの示唆：** {art['action_hint']}")
                    link_label = "論文を読む →" if art["content_type"] == "paper" else "元記事を読む →"
                    st.markdown(f"[{link_label}]({art['url']})")
