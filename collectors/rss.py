import feedparser
import requests
import re
from datetime import datetime
from config import get_theme_rss, get_theme_keywords_default, THEMES
from db.database import save_article, get_themes, get_keywords
from analyzer.gemini import generate_hint
from collectors.summarizer import build_summary, translate_to_ja
from analyzer.scorer import score_article


def _build_theme_config() -> dict:
    """Supabase から動的にテーマ設定を構築する。失敗時は config.py にフォールバック。"""
    db_themes = get_themes()
    if not db_themes:
        return THEMES

    result = {}
    for t in db_themes:
        name = t["name"]
        color = t.get("color", "#888888")
        db_kws = [k["keyword"] for k in get_keywords(name)]
        keywords = db_kws if db_kws else get_theme_keywords_default(name)
        result[name] = {
            "keywords": keywords,
            "color": color,
            "rss_feeds": get_theme_rss(name),
        }
    return result


def _strip_html(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _matches_keywords(text: str, keywords: list[str]) -> bool:
    text_lower = text.lower()
    # Match if ANY keyword is found (英語キーワード優先）
    for kw in keywords:
        if kw.lower() in text_lower:
            return True
    return False


def _parse_date(entry) -> str:
    for attr in ("published", "updated"):
        val = getattr(entry, attr, None)
        if val:
            return val[:10] if len(val) >= 10 else val
    return datetime.now().strftime("%Y-%m-%d")


def collect_rss():
    saved = 0
    themes = _build_theme_config()
    for theme, cfg in themes.items():
        keywords = cfg["keywords"]
        for source_name, url in cfg["rss_feeds"]:
            try:
                feed = feedparser.parse(url)
            except Exception as e:
                print(f"  [skip] {source_name}: {e}")
                continue

            for entry in feed.entries[:20]:
                title = _strip_html(entry.get("title", ""))
                link = entry.get("link", "")
                raw_summary = entry.get("summary", entry.get("description", ""))
                summary = build_summary(raw_summary, link)

                if not link:
                    continue
                if not _matches_keywords(title + " " + summary, keywords):
                    continue

                title_ja = translate_to_ja(title)
                action_hint = generate_hint(theme, title=title, summary=summary)
                pub_date = _parse_date(entry)
                sc = score_article(theme, title, summary, source_name)

                try:
                    ok = save_article(
                        theme=theme,
                        title=title,
                        title_ja=title_ja,
                        url=link,
                        source=source_name,
                        published_at=pub_date,
                        score=sc,
                        summary=summary,
                        action_hint=action_hint,
                        content_type="news",
                    )
                    if ok:
                        saved += 1
                        print(f"  [saved] [{theme}] {title[:60]}")
                    else:
                        print(f"  [failed] {source_name}: {title[:50]}")
                except Exception as e:
                    print(f"  [error] {source_name}: {str(e)[:60]}")

    print(f"RSS収集完了: {saved}件保存")
    return saved
