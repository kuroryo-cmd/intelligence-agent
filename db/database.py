import os
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client

# 環境変数を読み込む
load_dotenv()

# Supabase の URL と キーを環境変数から取得
SUPABASE_URL = os.environ.get("SUPABASE_URL", "http://localhost:54321")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")

# クライアント初期化
try:
    db: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception:
    db = None


def init_db():
    """テーブル作成（Supabase では手動で作成するため、ここは空）"""
    if not db:
        return
    # Supabase の SQL Editor で手動実行：
    # CREATE TABLE articles (
    #   id BIGSERIAL PRIMARY KEY,
    #   theme TEXT NOT NULL,
    #   title TEXT NOT NULL,
    #   title_ja TEXT,
    #   url TEXT UNIQUE NOT NULL,
    #   source TEXT,
    #   published_at TEXT,
    #   summary TEXT,
    #   action_hint TEXT,
    #   content_type TEXT DEFAULT 'news',
    #   score REAL DEFAULT 0,
    #   featured INTEGER DEFAULT 0,
    #   featured_at TIMESTAMPTZ,
    #   created_at TIMESTAMPTZ DEFAULT NOW()
    # );
    pass


def save_article(theme, title, url, source, published_at, summary, action_hint, content_type="news", title_ja="", score=0.0):
    try:
        if not db:
            return False
        db.table("articles").insert({
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
        }).execute()
        return True
    except Exception as e:
        import sys
        print(f"    [save_error] {type(e).__name__}: {str(e)[:100]}", file=sys.stderr)
        return False


def get_articles(theme=None, limit=50):
    if not db:
        return []
    try:
        if theme and theme != "すべて":
            data = db.table("articles").select("*").eq("theme", theme).order("created_at", desc=True).limit(limit).execute()
        else:
            data = db.table("articles").select("*").order("created_at", desc=True).limit(limit).execute()
        return data.data if data.data else []
    except Exception:
        return []


def toggle_featured(article_id: int) -> bool:
    """⭐ フィーチャー状態をトグル"""
    if not db:
        return False
    try:
        # 現在の値を取得
        data = db.table("articles").select("featured").eq("id", article_id).execute()
        if not data.data:
            return False
        current = data.data[0]["featured"]
        new_val = 0 if current else 1
        featured_at = datetime.utcnow().isoformat() if new_val else None

        db.table("articles").update({
            "featured": new_val,
            "featured_at": featured_at
        }).eq("id", article_id).execute()
        return bool(new_val)
    except Exception:
        return False


def get_archive(theme=None, limit=5):
    """スコア上位の記事をテーマ別に返す（自動キュレーション）"""
    if not db:
        return []
    try:
        if theme and theme != "すべて":
            data = db.table("articles").select("*").eq("theme", theme).order("score", desc=True).order("created_at", desc=True).limit(limit).execute()
            return data.data if data.data else []
        else:
            # テーマごとに上位N件
            all_articles = []
            themes_data = db.table("articles").select("theme", count="exact").execute()
            themes = list(set([a["theme"] for a in themes_data.data])) if themes_data.data else []
            for t in themes:
                data = db.table("articles").select("*").eq("theme", t).order("score", desc=True).order("created_at", desc=True).limit(limit).execute()
                if data.data:
                    all_articles.extend(data.data)
            return all_articles
    except Exception:
        return []


def get_featured(theme=None):
    if not db:
        return []
    try:
        if theme and theme != "すべて":
            data = db.table("articles").select("*").eq("theme", theme).eq("featured", 1).order("featured_at", desc=True).execute()
        else:
            data = db.table("articles").select("*").eq("featured", 1).order("theme").order("featured_at", desc=True).execute()
        return data.data if data.data else []
    except Exception:
        return []


def get_stats():
    if not db:
        return {"total": 0, "by_theme": {}}
    try:
        all_data = db.table("articles").select("theme", count="exact").execute()
        if not all_data.data:
            return {"total": 0, "by_theme": {}}

        by_theme = {}
        for article in all_data.data:
            theme = article["theme"]
            by_theme[theme] = by_theme.get(theme, 0) + 1

        return {"total": len(all_data.data), "by_theme": by_theme}
    except Exception:
        return {"total": 0, "by_theme": {}}
