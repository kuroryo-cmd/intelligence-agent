# ─── テーマごとの RSS フィード定義 ─────────────────────────────
# テーマ名は Supabase の themes.name と一致させること
THEMES_RSS = {
    "Agentic AI": [
        ("Hugging Face Blog", "https://huggingface.co/blog/feed.xml"),
        ("Langchain", "https://blog.langchain.dev/feed.xml"),
        ("TechCrunch AI", "https://techcrunch.com/category/artificial-intelligence/feed/"),
        ("VentureBeat AI", "https://venturebeat.com/category/ai/feed/"),
        ("MIT Tech Review", "https://www.technologyreview.com/feed/"),
    ],
    "ゲーミフィケーション": [
        ("Gamesbrief", "https://www.gamesbrief.com/feed/"),
        ("GDC Vault", "https://www.gdcvault.com/rss.xml"),
        ("Gamasutra", "https://www.gamedeveloper.com/rss.xml"),
        ("Yu-kai Chou", "https://yukaichou.com/feed/"),
        ("Interaction Design Foundation", "https://www.interaction-design.org/feed"),
        ("Nielsen Norman", "https://www.nngroup.com/feed/rss/all/"),
        ("Medium - Gamification", "https://medium.com/tag/gamification/feed"),
        ("ITmedia", "https://rss.itmedia.co.jp/rss/2.0/itmedia_all.xml"),
    ],
    "セマンティックレイヤー": [
        ("dbt Blog", "https://www.getdbt.com/blog/rss.xml"),
        ("Databricks Blog", "https://databricks.com/blog/feed"),
        ("Looker Blog", "https://www.looker.com/blog/feed"),
        ("Mode Analytics", "https://mode.com/blog/feed/"),
        ("ThoughtWorks Technology Radar", "https://www.thoughtworks.com/radar/feed"),
        ("Towards Data Science", "https://towardsdatascience.com/feed"),
        ("Medium - Data Engineering", "https://medium.com/tag/data-engineering/feed"),
        ("ZDNet Japan", "https://japan.zdnet.com/rss/index.rdf"),
    ],
}

# ─── テーマごとの arXiv クエリ定義 ──────────────────────────────
THEMES_ARXIV = {
    "Agentic AI": '(cat:cs.AI OR cat:cs.LG OR cat:cs.CL) AND (abs:"agentic" OR abs:"AI agent" OR abs:"autonomous agent" OR abs:"agent framework" OR ti:"agentic" OR ti:"agent")',
    "ゲーミフィケーション": '(cat:cs.AI OR cat:cs.HC OR cat:cs.LG OR cat:econ.GN) AND (abs:"gamification" OR abs:"gamified" OR abs:"loyalty program" OR abs:"reward program" OR abs:"customer engagement" OR abs:"behavioral" OR ti:"gamification" OR ti:"loyalty")',
    "セマンティックレイヤー": '(cat:cs.DB OR cat:cs.AI OR cat:cs.IR OR cat:cs.DC) AND (abs:"semantic layer" OR abs:"knowledge graph" OR abs:"ontology" OR abs:"data warehouse" OR abs:"data mesh" OR abs:"data catalog" OR ti:"semantic" OR ti:"knowledge graph")',
}

# ─── テーマごとのキーワード定義（フォールバック用） ─────────────
# Supabase の keywords テーブルにキーワードがない場合のデフォルト
THEMES_KEYWORDS_DEFAULT = {
    "Agentic AI": [
        "agentic AI", "agentic", "AI agent", "autonomous agent", "エージェントAI",
        "tool-calling", "tool use", "multi-agent", "agent framework", "LLM agent",
    ],
    "ゲーミフィケーション": [
        "gamification", "game mechanics", "gamified", "loyalty program", "loyalty",
        "light buyer", "light user", "customer engagement", "reward program",
        "ゲーミフィケーション", "ロイヤルティ", "ライトバイヤー",
        "behavioral economics", "user retention",
    ],
    "セマンティックレイヤー": [
        "semantic layer", "metrics layer", "headless BI", "knowledge graph",
        "ontology", "data modeling", "data warehouse", "data lakehouse",
        "セマンティックレイヤー", "オントロジー", "data mesh", "data catalog",
    ],
}


def get_theme_rss(theme_name: str) -> list:
    """テーマ名に対応する RSS フィード一覧を返す"""
    return THEMES_RSS.get(theme_name, [])


def get_theme_arxiv(theme_name: str) -> str:
    """テーマ名に対応する arXiv クエリを返す"""
    return THEMES_ARXIV.get(theme_name, "")


def get_theme_keywords_default(theme_name: str) -> list:
    """テーマ名に対応するデフォルトキーワード一覧を返す"""
    return THEMES_KEYWORDS_DEFAULT.get(theme_name, [])


# ─── 後方互換用（既存コードが THEMES を参照している箇所向け） ──
# collectors が Supabase から読み込む前のフォールバックとして使用
THEMES = {
    name: {
        "keywords": THEMES_KEYWORDS_DEFAULT.get(name, []),
        "color": color,
        "rss_feeds": THEMES_RSS.get(name, []),
        "arxiv_query": THEMES_ARXIV.get(name, ""),
    }
    for name, color in [
        ("Agentic AI", "#4F8EF7"),
        ("ゲーミフィケーション", "#F76F4F"),
        ("セマンティックレイヤー", "#4FBF8E"),
    ]
}
