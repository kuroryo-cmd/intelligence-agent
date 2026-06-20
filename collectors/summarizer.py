import requests
import re
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; IntelligenceAgent/1.0)"}


def _strip_html(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def fetch_body(url: str, max_chars: int = 800) -> str:
    """記事URLから本文テキストを取得する"""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.encoding = resp.apparent_encoding
        soup = BeautifulSoup(resp.text, "html.parser")

        # <script> <style> <nav> <footer> などノイズを除去
        for tag in soup(["script", "style", "nav", "footer", "header", "aside", "form"]):
            tag.decompose()

        # <article> > <main> > <body> の順で本文を探す
        body = soup.find("article") or soup.find("main") or soup.find("body")
        if not body:
            return ""

        paragraphs = [p.get_text(separator=" ", strip=True) for p in body.find_all("p")]
        text = " ".join(p for p in paragraphs if len(p) > 40)
        return text[:max_chars]
    except Exception:
        return ""


def translate_to_ja(text: str) -> str:
    """英語テキストを日本語に翻訳する（500文字以内で分割）"""
    if not text:
        return ""
    try:
        # GoogleTranslatorは1回5000文字まで
        translated = GoogleTranslator(source="auto", target="ja").translate(text[:1000])
        return translated or text
    except Exception:
        return text


def build_summary(rss_summary: str, url: str) -> str:
    """
    RSS要旨を使う（記事本文取得はスキップして高速化）
    """
    clean = _strip_html(rss_summary)

    # 要旨がない場合のみフォールバック
    if len(clean) < 50:
        body = fetch_body(url)
        source_text = body if body else "記事を取得できませんでした"
    else:
        source_text = clean[:800]

    if not source_text:
        return "（要旨を取得できませんでした）"

    return translate_to_ja(source_text)
