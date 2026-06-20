import re

# ───────────────────────────────────────────────
# テーマ別：パターン × 示唆テンプレート
# {topic} = タイトルから抽出したキーフレーズ
# ───────────────────────────────────────────────

HINTS = {
    "Agentic AI": [
        # ビジネス活用・導入事例
        (r"enterprise|business|deploy|implement|production|real.world|compan",
         "「{topic}」は企業導入事例として使える。提案資料の「なぜ今AIエージェントを入れるのか」スライドに、"
         "競合他社がすでに動いているという根拠として引用すると意思決定層の背中を押せる。"),
        # 安全・ガバナンス
        (r"safety|risk|govern|trust|audit|security|attack|defense|misdirect",
         "「{topic}」はAIエージェント導入の懸念を先回りする材料になる。"
         "提案資料に「リスク管理とガバナンス」のスライドを1枚追加し、"
         "「人間がどこで判断を持つか」という黒田さん独自の視点で差別化できる。"),
        # マルチエージェント・協調
        (r"multi.agent|collaborat|coordinat|network|contagion|propagat",
         "「{topic}」はマルチエージェント時代の到来を示す論拠になる。"
         "メルマガで「AIが複数連携して動く世界」を平易に解説すると、"
         "技術に疎い読者ほど「自社はどう備えるか」という危機感を持ちやすい。"),
        # コーディング・自動化
        (r"cod|automat|compil|software|develop|repositor",
         "「{topic}」はソフトウェア開発の自動化事例として使える。"
         "DX推進担当者向け提案資料の「AIが変える開発現場」スライドに引用すると、"
         "エンジニア不足の解決策として具体性が出る。"),
        # 評価・ベンチマーク
        (r"evaluat|benchmark|verif|assess|score|measur",
         "「{topic}」は「AIエージェントの品質をどう測るか」という問いへの答えになる。"
         "提案資料に評価指標のスライドを入れると、"
         "ROI重視のクライアントに対して投資対効果の説明がしやすくなる。"),
        # デフォルト
        ("",
         "「{topic}」は最新のエージェントAIトレンドとして提案資料の冒頭に引用できる。"
         "「AIが自律的に動く時代」という文脈を設けると、"
         "その後の提案内容への読者の受容度が上がる。"),
    ],

    "ゲーミフィケーション": [
        # ロイヤルティ・顧客維持
        (r"loyal|retain|churn|light.buyer|light.user|reward.program|point|badge",
         "「{topic}」はロイヤルティプログラムの設計根拠になる。"
         "メルマガで「ライトバイヤーをヘビーバイヤーに育てる3つのゲーム設計」として紹介すると、"
         "マーケターに直接刺さる実践コンテンツになる。"),
        # 医療・ヘルスケア
        (r"health|medic|clinic|patient|catheter|ultrasound",
         "「{topic}」はヘルスケア領域でのゲーミフィケーション導入事例として使える。"
         "提案資料の「業界別活用例」スライドに入れると、"
         "医療・製薬クライアントへの提案に説得力が加わる。"),
        # 学習・研修・エンゲージメント
        (r"learn|train|student|educat|engag|motivat|serious.game",
         "「{topic}」は社員研修・人材育成への応用として使える。"
         "HR担当者向けの提案資料に「研修定着率をゲームで上げる」事例として組み込むと、"
         "コスト削減と効果向上の両面から訴求できる。"),
        # AI×ゲーミフィケーション
        (r"ai|llm|language model|generat|reward design|incentive",
         "「{topic}」はAI×ゲーミフィケーションの融合事例として希少性が高い。"
         "メルマガで「AIがゲームの報酬設計を最適化する時代」として先取りして発信すると、"
         "業界の一歩先を行く書き手としてのポジションが固まる。"),
        # デジタル疲れ・行動変容
        (r"digital|exhaust|burnout|wellbeing|connect|behavior",
         "「{topic}」は「ゲーミフィケーションの副作用とその克服」という切り口になる。"
         "提案資料に批判的視点を1枚入れると、"
         "一方的な推進論より信頼感が増し、意思決定者の懸念を先回りできる。"),
        # デフォルト
        ("",
         "「{topic}」をメルマガのネタとして取り上げると、"
         "ゲーミフィケーションに関心を持つビジネスパーソンへのリーチが広がる。"
         "冒頭に「なぜ人は飽きるのか」という問いを置くと開封率が上がりやすい。"),
    ],

    "セマンティックレイヤー": [
        # AI×データ
        (r"llm|language model|ai|generat|agent|mcp",
         "「{topic}」は「AIがデータを正しく読むためにセマンティックレイヤーが必要」という論拠になる。"
         "提案資料に「AIにデータを渡す前にやるべきこと」スライドを追加すると、"
         "DX担当者の「AIを入れたのに使えない」という悩みに直撃する。"),
        # BI・アナリティクス
        (r"bi|analyt|dashboard|report|metric|kpi|forecast",
         "「{topic}」は「BIツール導入前にセマンティックレイヤーを整備すべき理由」の根拠になる。"
         "メルマガで「ダッシュボードが信頼されない本当の理由」という切り口で書くと、"
         "データ活用に悩む意思決定層に刺さる。"),
        # ナレッジグラフ・オントロジー
        (r"knowledge.graph|ontolog|graph|schema|model",
         "「{topic}」はデータの「意味」を統一するアプローチとして提案資料に使える。"
         "「部門ごとにデータの定義がバラバラ」という課題を持つクライアントへの"
         "解決策スライドに組み込むと具体性が増す。"),
        # エンタープライズ・組織
        (r"enterprise|organiz|team|collaborat|govern|trust|traceab",
         "「{topic}」は組織横断でデータを統一するガバナンスの文脈で使える。"
         "提案資料の「なぜデータ活用が組織で止まるのか」スライドに引用すると、"
         "経営層への説明資料として機能する。"),
        # 精度・コンプライアンス
        (r"accurac|compliance|logical|predict|bias|fair",
         "「{topic}」はデータ品質・コンプライアンスの根拠として使える。"
         "「AIの出力が信頼できない」という懸念への回答として"
         "提案資料に「セマンティックレイヤーで精度を担保する」スライドを入れると効果的。"),
        # デフォルト
        ("",
         "「{topic}」の知見を提案資料の「データ活用の課題と解決策」スライドに組み込むことを検討。"
         "技術的な話に入る前に「御社のデータは今、誰が信頼していますか？」という問いを置くと、"
         "クライアントの当事者意識を引き出せる。"),
    ],
}


def _extract_topic(title: str) -> str:
    title = re.sub(r"^\[論文\]\s*", "", title).strip()
    # コロンで分割して短い方（≒タイトルのキーフレーズ）を使う
    if ":" in title:
        parts = title.split(":", 1)
        return parts[0].strip() if len(parts[0]) <= 35 else parts[1].strip()[:40]
    return title[:45]


def generate_hint(theme: str, title: str = "", summary: str = "") -> str:
    patterns = HINTS.get(theme)
    if not patterns:
        return f"「{_extract_topic(title)}」を提案資料のトレンド根拠として活用できます。"

    topic = _extract_topic(title)
    combined = (title + " " + summary).lower()

    for pattern, template in patterns:
        if not pattern or re.search(pattern, combined):
            return template.format(topic=topic)

    return f"「{topic}」を提案資料・メルマガのトレンド根拠として活用できます。"
