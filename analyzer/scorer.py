from config import THEMES

# 信頼性の高いソースは加点
SOURCE_SCORES = {
    "TechCrunch AI": 3.0,
    "VentureBeat AI": 3.0,
    "MIT Tech Review": 4.0,
    "dbt Blog": 4.0,
    "Towards Data Science": 2.5,
    "arXiv": 2.0,
    "ITmedia AI": 2.0,
    "ZDnet Japan": 2.0,
    "Gamasutra": 3.0,
    "Yu-kai Chou": 4.0,
    "Atlan Blog": 3.5,
}

# タイトルに含まれると加点されるビジネス寄りのキーワード
BUSINESS_KEYWORDS = [
    "how to", "why", "guide", "case study", "enterprise", "business",
    "strategy", "roi", "revenue", "customer", "market", "trend",
    "practical", "real-world", "example", "framework", "best practice",
    "活用", "事例", "戦略", "収益", "顧客", "市場", "実践", "ガイド",
    "loyalty", "reward", "engagement", "light buyer", "gamif",
]

# タイトルに含まれると減点される純技術ワード
TECH_PENALTY_WORDS = [
    "theorem", "proof", "equation", "gradient", "convergence",
    "latency", "benchmark", "ablation", "embedding", "token",
    "probabilistic", "stochastic", "entropy", "homotopy",
]


def score_article(theme: str, title: str, summary: str, source: str) -> float:
    score = 1.0
    keywords = THEMES.get(theme, {}).get("keywords", [])
    combined = (title + " " + summary).lower()
    title_lower = title.lower()

    # キーワード密度（タイトルに含まれると2点、要旨のみは0.5点）
    for kw in keywords:
        kw_l = kw.lower()
        if kw_l in title_lower:
            score += 2.0
        elif kw_l in combined:
            score += 0.5

    # ソース信頼度
    score += SOURCE_SCORES.get(source, 1.0)

    # ビジネスキーワード加点
    for bw in BUSINESS_KEYWORDS:
        if bw in combined:
            score += 0.8

    # 技術用語減点
    for tw in TECH_PENALTY_WORDS:
        if tw in title_lower:
            score -= 1.5

    # 要旨が充実していると加点
    if len(summary) > 200:
        score += 1.0

    return round(max(score, 0.0), 2)
