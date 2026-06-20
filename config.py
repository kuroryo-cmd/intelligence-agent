THEMES = {
    "Agentic AI": {
        "keywords": ["agentic AI", "agentic", "AI agent", "autonomous agent", "エージェントAI", "tool-calling", "tool use", "multi-agent"],
        "color": "#4F8EF7",
        "rss_feeds": [
            ("TechCrunch AI", "https://techcrunch.com/category/artificial-intelligence/feed/"),
            ("VentureBeat AI", "https://venturebeat.com/category/ai/feed/"),
            ("MIT Tech Review", "https://www.technologyreview.com/feed/"),
            ("ITmedia AI", "https://rss.itmedia.co.jp/rss/2.0/aiplus.xml"),
        ],
        "arxiv_query": "(cat:cs.AI OR cat:cs.LG OR cat:cs.CL) AND (abs:\"agentic\" OR abs:\"AI agent\" OR abs:\"autonomous agent\" OR ti:\"agentic\" OR ti:\"AI agent\")",
    },
    "ゲーミフィケーション": {
        "keywords": ["gamification", "game mechanics", "gamified", "loyalty program", "loyalty", "light buyer", "light user", "customer engagement", "reward program", "ゲーミフィケーション", "ロイヤルティ", "ライトバイヤー"],
        "color": "#F76F4F",
        "rss_feeds": [
            ("Gamasutra", "https://www.gamedeveloper.com/rss.xml"),
            ("Yu-kai Chou", "https://yukaichou.com/feed/"),
            ("ITmedia", "https://rss.itmedia.co.jp/rss/2.0/itmedia_all.xml"),
        ],
        "arxiv_query": "(cat:cs.AI OR cat:cs.HC OR cat:cs.LG OR cat:econ.GN) AND (abs:\"gamification\" OR abs:\"gamified\" OR abs:\"loyalty program\" OR abs:\"reward program\" OR abs:\"customer engagement\" OR ti:\"gamification\" OR ti:\"loyalty\")",
    },
    "セマンティックレイヤー": {
        "keywords": ["semantic layer", "metrics layer", "headless BI", "knowledge graph", "ontology", "data modeling", "セマンティックレイヤー", "オントロジー"],
        "color": "#4FBF8E",
        "rss_feeds": [
            ("dbt Blog", "https://www.getdbt.com/blog/rss.xml"),
            ("Towards Data Science", "https://towardsdatascience.com/feed"),
            ("ZDNet Japan", "https://japan.zdnet.com/rss/index.rdf"),
        ],
        "arxiv_query": "(cat:cs.DB OR cat:cs.AI OR cat:cs.IR) AND (abs:\"semantic layer\" OR abs:\"knowledge graph\" OR abs:\"ontology\" OR abs:\"data modeling\" OR ti:\"semantic layer\" OR ti:\"knowledge graph\")",
    },
}
