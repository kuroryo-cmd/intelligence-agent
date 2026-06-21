import streamlit as st
from datetime import datetime, timedelta
from db.database import (
    init_db, get_articles, get_stats, toggle_featured, get_featured, get_archive,
    get_keywords, add_keyword, delete_keyword,
    get_competitors, add_competitor, delete_competitor,
    get_themes, add_theme, update_theme, delete_theme,
)
from config import THEMES as THEMES_FALLBACK


def _load_themes() -> dict:
    """Supabase からテーマを動的に読み込む。失敗時は config フォールバック。"""
    db_themes = get_themes()
    if not db_themes:
        return THEMES_FALLBACK
    return {t["name"]: {"color": t.get("color", "#888"), "description": t.get("description", "")} for t in db_themes}


THEMES = _load_themes()

def format_date(date_str):
    """複数の日付形式に対応して年月日形式に変換"""
    if not date_str:
        return ""
    try:
        # ISO形式（YYYY-MM-DD）
        try:
            dt = datetime.strptime(date_str[:10], "%Y-%m-%d")
        except:
            # RFC形式（Tue, 13 Jan 2026...）
            dt = datetime.strptime(date_str[:16], "%a, %d %b %Y")

        return f"{dt.year}年{dt.month}月{dt.day}日"
    except:
        return date_str[:10]

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
    color = THEMES.get(t, {}).get("color", "#888")
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
    score = art.get("score", 0)

    # スコアに応じた背景色（重要度の可視化）
    if score >= 4.0:
        bg_color = "#fffbf0"
    elif score >= 3.0:
        bg_color = "#fafafa"
    else:
        bg_color = "#ffffff"

    return f"""
<div style="border-left:6px solid {color};padding:16px 20px;margin-bottom:14px;background:{bg_color};border-radius:8px;box-shadow:0 1px 3px rgba(0,0,0,0.08);">
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
    <div>{badge(art['theme'], color)}{source_chip(src)}</div>
    <span style="font-size:11px;color:#aaa;font-weight:600;">{pub}</span>
  </div>
  <div style="font-size:23px;font-weight:900;color:#222;margin-bottom:6px;line-height:1.35;letter-spacing:-0.5px;">{title_ja[:85]}</div>
  <div style="font-size:13px;color:#999;margin-bottom:12px;line-height:1.5;">{title_en[:95]}</div>
  <div style="display:flex;gap:12px;align-items:center;">
    <a href="{art['url']}" target="_blank" style="font-size:13px;color:{color};text-decoration:none;font-weight:bold;padding:6px 10px;border:1.5px solid {color};border-radius:4px;display:inline-block;">記事を読む</a>
    <span style="font-size:11px;color:#bbb;font-weight:600;">★ スコア {score:.1f}</span>
  </div>
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
        icon = "🔬" if art["content_type"] == "paper" else "📰"
        is_featured = bool(art.get("featured"))
        star = "⭐" if is_featured else "☆"
        score = art.get("score", 0)

        # スコアに応じた背景色
        if score >= 4.0:
            score_color = "#FF6B6B"
        elif score >= 3.0:
            score_color = "#FFA500"
        else:
            score_color = "#999"

        with st.expander(f"{icon} {title_ja[:58]}  ／  {title_en[:50]}"):
            color2 = THEMES.get(art["theme"], {}).get("color", "#888")

            # メタデータ行
            st.markdown(
                f'{badge(art["theme"], color2)}{source_chip(art["source"])}'
                f'<span style="font-size:12px;color:{score_color};font-weight:700;">◆ {score:.1f}点</span>',
                unsafe_allow_html=True
            )
            st.caption(format_date(art["published_at"]))

            # タイトル
            st.markdown(
                f'<div style="font-size:22px;font-weight:900;color:#222;margin:12px 0 4px;letter-spacing:-0.5px;">{title_ja}</div>'
                f'<div style="font-size:13px;color:#888;margin-bottom:14px;">{title_en}</div>',
                unsafe_allow_html=True
            )

            # 要旨
            st.markdown(f"**📌 要旨**\n\n{art['summary']}")

            # 提案（背景色付き）
            st.markdown(
                f'<div style="background:#f9f4e6;border-left:3px solid {color2};padding:12px 14px;border-radius:4px;margin:12px 0;">'
                f'<div style="font-weight:700;color:#222;margin-bottom:4px;">💡 提案資料・メルマガへの使い方</div>'
                f'<div style="color:#555;font-size:14px;line-height:1.6;">{art["action_hint"]}</div>'
                f'</div>',
                unsafe_allow_html=True
            )

            # ボタン行
            col_link, col_star = st.columns([3, 1])
            with col_link:
                link_label = "論文を読む" if art["content_type"] == "paper" else "元記事を読む"
                st.markdown(f"[🔗 {link_label}]({art['url']})")
            with col_star:
                btn_label = f"{star} {'保存済' if is_featured else '注目'}"
                if st.button(btn_label, key=f"feat_{art['id']}"):
                    toggle_featured(art["id"])
                    st.rerun()

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
        sc = art.get("score", 0)

        # スコアに応じた背景色
        if sc >= 4.0:
            score_color = "#FF6B6B"
        elif sc >= 3.0:
            score_color = "#FFA500"
        else:
            score_color = "#999"

        with st.expander(f"🔬 {title_ja[:55]}  ／  {title_en[:55]}"):
            st.markdown(
                f'{badge(art["theme"], color)}{source_chip("arXiv")}'
                f'<span style="font-size:12px;color:{score_color};font-weight:700;">◆ {sc:.1f}点</span>',
                unsafe_allow_html=True
            )
            st.caption(format_date(art["published_at"]))

            st.markdown(
                f'<div style="font-size:22px;font-weight:900;color:#222;margin:12px 0 4px;letter-spacing:-0.5px;">{title_ja}</div>'
                f'<div style="font-size:13px;color:#888;margin-bottom:14px;">{title_en}</div>',
                unsafe_allow_html=True
            )
            st.markdown(f"**📌 要旨**\n\n{art['summary']}")
            st.markdown(
                f'<div style="background:#f9f4e6;border-left:3px solid {color};padding:12px 14px;border-radius:4px;margin:12px 0;">'
                f'<div style="font-weight:700;color:#222;margin-bottom:4px;">💡 提案資料・メルマガへの使い方</div>'
                f'<div style="color:#555;font-size:14px;line-height:1.6;">{art["action_hint"]}</div>'
                f'</div>',
                unsafe_allow_html=True
            )
            col_link, col_star = st.columns([3, 1])
            with col_link:
                st.markdown(f"[🔗 論文を読む]({art['url']})")
            with col_star:
                if st.button(f"{star} {'保存済' if is_featured else '注目'}", key=f"feat_p_{art['id']}"):
                    toggle_featured(art["id"])
                    st.rerun()

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
                icon = "🔬" if art["content_type"] == "paper" else "📰"
                sc = art.get("score", 0)
                is_featured = bool(art.get("featured"))
                star = "⭐" if is_featured else "☆"

                # スコアに応じた背景色
                if sc >= 4.0:
                    score_color = "#FF6B6B"
                elif sc >= 3.0:
                    score_color = "#FFA500"
                else:
                    score_color = "#999"

                with st.expander(f"{icon} {title_ja[:60]}  ／  {title_en[:60]}"):
                    st.markdown(
                        f'{badge(theme, color)}{source_chip(art["source"])}'
                        f'<span style="font-size:12px;color:{score_color};font-weight:700;">◆ {sc:.1f}点</span>',
                        unsafe_allow_html=True
                    )
                    st.caption(format_date(art["published_at"]))

                    st.markdown(
                        f'<div style="font-size:22px;font-weight:900;color:#222;margin:12px 0 4px;letter-spacing:-0.5px;">{title_ja}</div>'
                        f'<div style="font-size:13px;color:#888;margin-bottom:14px;">{title_en}</div>',
                        unsafe_allow_html=True
                    )
                    st.markdown(f"**📌 要旨**\n\n{art['summary']}")
                    st.markdown(
                        f'<div style="background:#f9f4e6;border-left:3px solid {color};padding:12px 14px;border-radius:4px;margin:12px 0;">'
                        f'<div style="font-weight:700;color:#222;margin-bottom:4px;">💡 提案資料・メルマガへの使い方</div>'
                        f'<div style="color:#555;font-size:14px;line-height:1.6;">{art["action_hint"]}</div>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                    col_link, col_star = st.columns([3, 1])
                    with col_link:
                        link_label = "論文を読む" if art["content_type"] == "paper" else "元記事を読む"
                        st.markdown(f"[🔗 {link_label}]({art['url']})")
                    with col_star:
                        if st.button(f"{star} {'保存済' if is_featured else '保存'}", key=f"arc_feat_{art['id']}"):
                            toggle_featured(art["id"])
                            st.rerun()

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
                icon = "🔬" if art["content_type"] == "paper" else "📰"
                sc = art.get("score", 0)

                # スコアに応じた背景色
                if sc >= 4.0:
                    score_color = "#FF6B6B"
                elif sc >= 3.0:
                    score_color = "#FFA500"
                else:
                    score_color = "#999"

                with st.expander(f"{icon} {title_ja[:60]}  ／  {title_en[:60]}"):
                    st.markdown(
                        f'{badge(theme, color)}{source_chip(art["source"])}'
                        f'<span style="font-size:12px;color:{score_color};font-weight:700;">◆ {sc:.1f}点</span>',
                        unsafe_allow_html=True
                    )
                    st.caption(format_date(art["published_at"]))

                    st.markdown(
                        f'<div style="font-size:22px;font-weight:900;color:#222;margin:12px 0 4px;letter-spacing:-0.5px;">{title_ja}</div>'
                        f'<div style="font-size:13px;color:#888;margin-bottom:14px;">{title_en}</div>',
                        unsafe_allow_html=True
                    )
                    st.markdown(f"**📌 要旨**\n\n{art['summary']}")
                    st.markdown(
                        f'<div style="background:#f9f4e6;border-left:3px solid {color};padding:12px 14px;border-radius:4px;margin:12px 0;">'
                        f'<div style="font-weight:700;color:#222;margin-bottom:4px;">💡 提案資料・メルマガへの使い方</div>'
                        f'<div style="color:#555;font-size:14px;line-height:1.6;">{art["action_hint"]}</div>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                    col_link, col_star = st.columns([3, 1])
                    with col_link:
                        link_label = "論文を読む" if art["content_type"] == "paper" else "元記事を読む"
                        st.markdown(f"[🔗 {link_label}]({art['url']})")
                    with col_star:
                        if st.button("⭐ 解除", key=f"unfeat_{art['id']}"):
                            toggle_featured(art["id"])
                            st.rerun()

st.divider()

# ─── 設定画面（⚙️ Settings） ──────────────────────────────
with st.expander("⚙️ 設定（テーマ・キーワード・競合管理）"):
    st.subheader("🔧 管理画面")
    tab_theme, tab_kw, tab_comp = st.tabs(["🌐 テーマ管理", "🔑 キーワード管理", "🎯 競合管理"])

    # ─── テーマ管理 ────────────────────────────────────────
    with tab_theme:
        st.markdown("### テーマの追加・編集・削除")

        # 新規追加フォーム
        with st.form("add_theme_form"):
            st.markdown("**新しいテーマを追加**")
            col_name, col_color = st.columns([2, 1])
            with col_name:
                new_theme_name = st.text_input("テーマ名", placeholder="例：MaaS, Web3, 量子コンピュータ")
            with col_color:
                new_theme_color = st.color_picker("テーマカラー", value="#4F8EF7")
            new_theme_desc = st.text_input("説明（オプション）", placeholder="例：mobility as a service, smart mobility")
            submitted = st.form_submit_button("🌐 テーマ追加")
            if submitted:
                if new_theme_name.strip():
                    ok = add_theme(new_theme_name.strip(), new_theme_color, new_theme_desc.strip())
                    if ok:
                        st.success(f"✅ 「{new_theme_name}」を追加しました。config.py に RSS/arXiv クエリを追加することで収集が有効になります。")
                        st.rerun()
                    else:
                        st.error("⚠️ 追加に失敗しました（テーマ名が重複している可能性）")
                else:
                    st.warning("テーマ名を入力してください")

        st.divider()

        # 現在のテーマ一覧（編集・削除）
        st.markdown("### 現在のテーマ一覧")
        db_themes_list = get_themes()
        if db_themes_list:
            for t in db_themes_list:
                col_color_prev, col_info, col_edit, col_del = st.columns([0.3, 3, 1.5, 0.8])
                with col_color_prev:
                    st.markdown(
                        f'<div style="width:28px;height:28px;background:{t["color"]};border-radius:50%;margin-top:6px;"></div>',
                        unsafe_allow_html=True
                    )
                with col_info:
                    st.markdown(f"**{t['name']}**")
                    if t.get("description"):
                        st.caption(t["description"])
                with col_edit:
                    if st.button("✏️ 編集", key=f"edit_theme_{t['id']}"):
                        st.session_state[f"editing_theme_{t['id']}"] = True

                    if st.session_state.get(f"editing_theme_{t['id']}"):
                        with st.form(f"edit_theme_form_{t['id']}"):
                            e_name  = st.text_input("テーマ名", value=t["name"])
                            e_color = st.color_picker("カラー", value=t["color"])
                            e_desc  = st.text_input("説明", value=t.get("description", ""))
                            if st.form_submit_button("保存"):
                                ok = update_theme(t["id"], e_name.strip(), e_color, e_desc.strip())
                                if ok:
                                    st.success("✅ 更新しました")
                                    st.session_state.pop(f"editing_theme_{t['id']}", None)
                                    st.rerun()
                                else:
                                    st.error("更新に失敗しました")
                with col_del:
                    if st.button("🗑️", key=f"del_theme_{t['id']}"):
                        ok = delete_theme(t["id"])
                        if ok:
                            st.success("削除しました")
                            st.rerun()

        else:
            st.info("テーマが登録されていません")

        st.info("💡 **新テーマ追加後**: `config.py` の `THEMES_RSS` と `THEMES_ARXIV` にそのテーマ名でRSSフィード・arXivクエリを追加すると収集が有効になります。")


    # ─── キーワード管理 ───────────────────────────────
    with tab_kw:
        st.markdown("### キーワードの追加・削除")
        theme_names = [t["name"] for t in get_themes()] or list(THEMES.keys())
        col_theme, col_kw = st.columns([1, 2])
        with col_theme:
            theme_sel = st.selectbox("テーマ", theme_names, key="kw_theme")
        with col_kw:
            new_kw = st.text_input("新しいキーワード", placeholder="例：langchain, agent framework")

        if st.button("🔑 キーワード追加", key="add_kw"):
            if new_kw.strip():
                ok = add_keyword(theme_sel, new_kw.strip())
                if ok:
                    st.success(f"✅ '{new_kw}' を {theme_sel} に追加しました")
                    st.rerun()
                else:
                    st.error("⚠️ 追加に失敗しました（重複の可能性）")
            else:
                st.warning("キーワードを入力してください")

        st.divider()
        st.markdown("### 現在のキーワード一覧")
        all_keywords = get_keywords()
        if all_keywords:
            for theme in theme_names:
                theme_kws = [k for k in all_keywords if k["theme"] == theme]
                if theme_kws:
                    color = THEMES.get(theme, {}).get("color", "#888")
                    st.markdown(f'<h4 style="color:{color}">● {theme}</h4>', unsafe_allow_html=True)
                    for kw in theme_kws:
                        col_kw_name, col_del = st.columns([4, 1])
                        with col_kw_name:
                            st.caption(f"• {kw['keyword']}")
                        with col_del:
                            if st.button("🗑️", key=f"del_kw_{kw['id']}"):
                                ok = delete_keyword(kw["id"])
                                if ok:
                                    st.success("削除しました")
                                    st.rerun()
        else:
            st.info("まだキーワードが登録されていません")

    # ─── 競合管理 ──────────────────────────────────────
    with tab_comp:
        st.markdown("### 競合の追加・削除")
        col_name, col_url = st.columns([1.5, 2])
        with col_name:
            comp_name = st.text_input("競合名", placeholder="例：Notionai, Kernal")
        with col_url:
            comp_url = st.text_input("URL", placeholder="https://example.com")

        comp_memo = st.text_area("メモ", placeholder="競合の特徴、提供内容など")

        if st.button("🎯 競合追加", key="add_comp"):
            if comp_name.strip():
                ok = add_competitor(comp_name.strip(), comp_url.strip(), comp_memo.strip())
                if ok:
                    st.success(f"✅ '{comp_name}' を追加しました")
                    st.rerun()
                else:
                    st.error("⚠️ 追加に失敗しました（重複の可能性）")
            else:
                st.warning("競合名を入力してください")

        st.divider()
        st.markdown("### 競合一覧")
        competitors = get_competitors()
        if competitors:
            for comp in competitors:
                col_info, col_del = st.columns([4, 1])
                with col_info:
                    st.markdown(f"**{comp['name']}**")
                    if comp["url"]:
                        st.caption(f"🔗 {comp['url']}")
                    if comp["memo"]:
                        st.caption(f"📝 {comp['memo']}")
                with col_del:
                    if st.button("🗑️", key=f"del_comp_{comp['id']}"):
                        ok = delete_competitor(comp["id"])
                        if ok:
                            st.success("削除しました")
                            st.rerun()
        else:
            st.info("まだ競合が登録されていません")
