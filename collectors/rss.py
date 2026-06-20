import feedparser
import requests
import re
from datetime import datetime
from config import THEMES
from db.database import save_article
from analyzer.mock import generate_hint
from collectors.summarizer import build_summary, translate_to_ja
from analyzer.scorer import score_article


def _strip_html(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _matches_keywords(text: str, keywords: list[str]) -> bool:
    text_lower = text.lower()
    return any(kw.lower() in text_lower for kw in keywords)


def _parse_date(entry) -> str:
    for attr in ("published", "updated"):
        val = getattr(entry, attr, None)
        if val:
            return val[:10] if len(val) >= 10 else val
    return datetime.now().strftime("%Y-%m-%d")


def collect_rss():
    saved = 0
    for theme, cfg in THEMES.items():
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

    print(f"RSS収集完了: {saved}件保存")
    return saved
