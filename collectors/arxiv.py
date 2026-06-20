import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from config import THEMES
from db.database import save_article
from analyzer.gemini import generate_hint
from collectors.summarizer import translate_to_ja
from analyzer.scorer import score_article

ARXIV_API = "https://export.arxiv.org/api/query"
NS = {"atom": "http://www.w3.org/2005/Atom"}


def collect_arxiv():
    saved = 0
    for theme, cfg in THEMES.items():
        query = cfg["arxiv_query"]
        params = {
            "search_query": f"all:{query}",
            "start": 0,
            "max_results": 20,
            "sortBy": "submittedDate",
            "sortOrder": "descending",
        }
        try:
            resp = requests.get(ARXIV_API, params=params, timeout=15)
            root = ET.fromstring(resp.text)
        except Exception as e:
            print(f"  [arxiv skip] {theme}: {e}")
            continue

        keywords = cfg["keywords"]

        for entry in root.findall("atom:entry", NS):
            title = entry.findtext("atom:title", "", NS).strip().replace("\n", " ")
            raw_summary = entry.findtext("atom:summary", "", NS).strip().replace("\n", " ")

            # 数式・物理・数学系の純粋技術論文を除外
            TECH_NOISE = [
                "quantum", "photon", "proton", "boson", "fermion", "lattice gauge",
                "homotopy", "topology", "cohomology", "manifold", "stochastic differential",
                "polymer", "cosmolog", "magnetiz", "lensing", "neutrino", "gravitational",
                "semi-definite", "semidefinite", "convex optim",
            ]
            title_lower = title.lower()
            if any(noise in title_lower for noise in TECH_NOISE):
                print(f"  [skip] 技術ノイズ: {title[:60]}")
                continue

            # キーワードマッチング（ハイフンとスペースを統一）
            def normalize(s): return s.lower().replace("-", " ")
            title_norm = normalize(title)
            summ_norm = normalize(raw_summary)
            kws_norm = [normalize(kw) for kw in keywords]

            title_hit = any(kw in title_norm for kw in kws_norm)
            summ_hit  = any(kw in summ_norm  for kw in kws_norm)

            # タイトルか要旨どちらかに一致が必要。要旨のみ一致は2語以上のキーワードに限定
            long_kws = [kw for kw in kws_norm if len(kw.split()) >= 2]
            summ_strict = any(kw in summ_norm for kw in long_kws)

            if not title_hit and not summ_strict:
                print(f"  [skip] キーワード不一致: {title[:60]}")
                continue

            title_ja = translate_to_ja(title)
            summary = translate_to_ja(raw_summary[:800])
            link_el = entry.find("atom:id", NS)
            link = link_el.text.strip() if link_el is not None else ""
            pub = entry.findtext("atom:published", "", NS)[:10]

            if not link:
                continue

            action_hint = generate_hint(theme, title=title, summary=raw_summary)
            sc = score_article(theme, title, raw_summary, "arXiv")
            ok = save_article(
                theme=theme,
                title=f"[論文] {title}",
                title_ja=title_ja,
                url=link,
                score=sc,
                source="arXiv",
                published_at=pub,
                summary=summary,
                action_hint=action_hint,
                content_type="paper",
            )
            if ok:
                saved += 1
                print(f"  [saved] [{theme}] 論文: {title[:60]}")

    print(f"arXiv収集完了: {saved}件保存")
    return saved
