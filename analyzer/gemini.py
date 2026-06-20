import os
import re
import google.generativeai as genai

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
genai.configure(api_key=GEMINI_API_KEY)

THEME_CONTEXT = {
    "Agentic AI": "You are an expert in AI agent technology and business strategy. Generate a specific, actionable suggestion for how to use this article in a business proposal or newsletter.",
    "ゲーミフィケーション": "You are an expert in gamification and customer engagement. Generate a specific, actionable suggestion for how to use this article in a business proposal or newsletter.",
    "セマンティックレイヤー": "You are an expert in data management and semantic layers. Generate a specific, actionable suggestion for how to use this article in a business proposal or newsletter.",
}


def generate_hint(theme: str, title: str = "", summary: str = "") -> str:
    """Gemini API を使用して、記事から具体的な示唆を生成"""
    if not GEMINI_API_KEY:
        return f"「{title[:50]}」を提案資料のトレンド根拠として活用できます。"

    context = THEME_CONTEXT.get(theme, "Generate a business-focused suggestion for using this article.")

    prompt = f"""You are a business consultant helping a marketing strategist use the latest trends.

Theme: {theme}
Article Title: {title}
Article Summary: {summary[:500]}

{context}

Please provide ONE concise, specific suggestion (Japanese) for how to use this article in a business proposal or company newsletter.
Focus on: WHAT to include (specific slide, section, or talking point) and WHY it will resonate with the audience.
Keep it under 100 words. Start directly with the suggestion, no preamble.
"""

    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt, stream=False)
        hint = response.text.strip()

        # 結果が空の場合はフォールバック
        if not hint or len(hint) < 10:
            return f"「{title[:50]}」を提案資料/メルマガのトレンド根拠として活用できます。"

        return hint
    except Exception as e:
        # API エラー時はフォールバック
        return f"「{title[:50]}」を提案資料のトレンド根拠として活用できます。"
