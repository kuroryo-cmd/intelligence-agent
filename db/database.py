import os
import requests
from datetime import datetime
from dotenv import load_dotenv

# 環境変数を読み込む
load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}


def init_db():
    """テーブル作成（Supabase では手動で作成するため、ここは空）"""
    pass


def save_article(theme, title, url, source, published_at, summary, action_hint, content_type="news", title_ja="", score=0.0):
    try:
        if not SUPABASE_URL or not SUPABASE_KEY:
            return False

        payload = {
            "theme": theme,
            "title": title,
            "title_ja": title_ja,
            "url": url,
            "source": source,
            "published_at": published_at,
            "summary": summary,
            "action_hint": action_hint,
            "content_type": content_type,
            "score": score,
        }

        response = requests.post(
            f"{SUPABASE_URL}/rest/v1/articles",
            json=payload,
            headers=HEADERS,
            timeout=10
        )

        if response.status_code in (200, 201):
            return True
        else:
            print(f"    [save_error] HTTP {response.status_code}: {response.text[:100]}")
            return False
    except Exception as e:
        print(f"    [save_error] {type(e).__name__}: {str(e)[:100]}")
        return False


def get_articles(theme=None, limit=50):
    try:
        if not SUPABASE_URL or not SUPABASE_KEY:
            return []

        if theme and theme != "すべて":
            url = f"{SUPABASE_URL}/rest/v1/articles?theme=eq.{theme}&order=created_at.desc&limit={limit}"
        else:
            url = f"{SUPABASE_URL}/rest/v1/articles?order=created_at.desc&limit={limit}"

        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            return response.json()
        return []
    except Exception:
        return []


def toggle_featured(article_id: int) -> bool:
    """⭐ フィーチャー状態をトグル"""
    try:
        if not SUPABASE_URL or not SUPABASE_KEY:
            return False

        # 現在の値を取得
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/articles?id=eq.{article_id}&select=featured",
            headers=HEADERS,
            timeout=10
        )

        if response.status_code != 200 or not response.json():
            return False

        current = response.json()[0]["featured"]
        new_val = 0 if current else 1
        featured_at = datetime.utcnow().isoformat() if new_val else None

        response = requests.patch(
            f"{SUPABASE_URL}/rest/v1/articles?id=eq.{article_id}",
            json={"featured": new_val, "featured_at": featured_at},
            headers=HEADERS,
            timeout=10
        )

        return response.status_code in (200, 204)
    except Exception:
        return False


def get_archive(theme=None, limit=5):
    """スコア上位の記事をテーマ別に返す（自動キュレーション）"""
    try:
        if not SUPABASE_URL or not SUPABASE_KEY:
            return []

        if theme and theme != "すべて":
            url = f"{SUPABASE_URL}/rest/v1/articles?theme=eq.{theme}&order=score.desc,created_at.desc&limit={limit}"
            response = requests.get(url, headers=HEADERS, timeout=10)
            if response.status_code == 200:
                return response.json()
        else:
            # Get all themes first
            response = requests.get(
                f"{SUPABASE_URL}/rest/v1/articles?select=theme",
                headers=HEADERS,
                timeout=10
            )
            if response.status_code == 200:
                themes = list(set([a["theme"] for a in response.json()]))
                all_articles = []
                for t in themes:
                    url = f"{SUPABASE_URL}/rest/v1/articles?theme=eq.{t}&order=score.desc,created_at.desc&limit={limit}"
                    resp = requests.get(url, headers=HEADERS, timeout=10)
                    if resp.status_code == 200:
                        all_articles.extend(resp.json())
                return all_articles

        return []
    except Exception:
        return []


def get_featured(theme=None):
    try:
        if not SUPABASE_URL or not SUPABASE_KEY:
            return []

        if theme and theme != "すべて":
            url = f"{SUPABASE_URL}/rest/v1/articles?theme=eq.{theme}&featured=eq.1&order=featured_at.desc"
        else:
            url = f"{SUPABASE_URL}/rest/v1/articles?featured=eq.1&order=theme.asc,featured_at.desc"

        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            return response.json()
        return []
    except Exception:
        return []


def get_stats():
    try:
        if not SUPABASE_URL or not SUPABASE_KEY:
            return {"total": 0, "by_theme": {}}

        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/articles?select=theme",
            headers=HEADERS,
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            by_theme = {}
            for article in data:
                theme = article["theme"]
                by_theme[theme] = by_theme.get(theme, 0) + 1
            return {"total": len(data), "by_theme": by_theme}

        return {"total": 0, "by_theme": {}}
    except Exception:
        return {"total": 0, "by_theme": {}}
