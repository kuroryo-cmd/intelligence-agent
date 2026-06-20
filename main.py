import sys
from db.database import init_db
from collectors.rss import collect_rss
from collectors.arxiv import collect_arxiv


def collect():
    print("=== Intelligence Agent 収集開始 ===")
    init_db()
    collect_rss()
    collect_arxiv()
    print("=== 収集完了 ===")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "collect"
    if cmd == "collect":
        collect()
    else:
        print(f"不明なコマンド: {cmd}")
        print("使い方: python main.py collect")
