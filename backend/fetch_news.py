# import requests
# import feedparser
# import json
# from datetime import datetime

# FEED_URL = "https://rss.itmedia.co.jp/rss/2.0/ait.xml"  # ＠ITの公式RSS

# def fetch_atmarkit_articles():
#     headers = {
#         "User-Agent": "Mozilla/5.0 (compatible; NewsBot/1.0; +https://example.com)"
#     }
#     try:
#         resp = requests.get(FEED_URL, headers=headers, timeout=10)
#         print(f"HTTP {resp.status_code} from {FEED_URL}")
#         resp.raise_for_status()
#     except Exception as e:
#         print("❌ RSS取得に失敗:", e)
#         return

#     feed = feedparser.parse(resp.content)
#     print(f"✅ フィード取得件数: {len(feed.entries)} 件")

#     top10 = feed.entries[:10]
#     news_list = []
#     for entry in top10:
#         news_list.append({
#             "id": entry.get("id") or entry.get("link"),
#             "title": entry.get("title", ""),
#             "link": entry.get("link", ""),
#             "published": entry.get("published") or entry.get("updated") or ""
#         })

#     with open("db.json", "w", encoding="utf-8") as f:
#         json.dump({
#             "date": datetime.now().isoformat(),
#             "news": news_list
#         }, f, indent=2, ensure_ascii=False)

#     print("✅ ＠IT（ITmedia RSS）からニュースを保存しました。")

# if __name__ == "__main__":
#     fetch_atmarkit_articles()


import requests, feedparser, json, os
from datetime import datetime, timezone, timedelta

FEED_URL = "https://rss.itmedia.co.jp/rss/2.0/ait.xml"

def fetch_atmarkit_articles():
    headers = {"User-Agent": "Mozilla/5.0 (compatible; NewsBot/1.0)"}
    resp = requests.get(FEED_URL, headers=headers, timeout=10)
    resp.raise_for_status()
    feed = feedparser.parse(resp.content)

    top10 = feed.entries[:10]
    news_list = [{
        "id": e.get("id") or e.get("link"),
        "title": e.get("title", ""),
        "link": e.get("link", ""),
        "published": e.get("published") or e.get("updated") or ""
    } for e in top10]

    # 最新（今日分）→ db.json
    now = datetime.now(timezone(timedelta(hours=9)))  # JST表示に寄せたいなら
    with open("db.json", "w", encoding="utf-8") as f:
        json.dump({"date": now.isoformat(), "news": news_list}, f, indent=2, ensure_ascii=False)

    # 履歴 → history.json に追記（同じ日付は上書き）
    hist_path = "history.json"
    history = {}
    if os.path.exists(hist_path):
        with open(hist_path, "r", encoding="utf-8") as f:
            try:
                history = json.load(f)
            except Exception:
                history = {}

    date_key = now.strftime("%Y-%m-%d")  # 例: 2025-08-09
    history[date_key] = news_list  # その日の一覧を保存/更新

    # 任意: 保持日数を制限（最近60日だけ残す）
    MAX_DAYS = 60
    if len(history) > MAX_DAYS:
        for d in sorted(history.keys())[:-MAX_DAYS]:
            history.pop(d, None)

    with open(hist_path, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)

    print("✅ 最新と履歴を保存しました。")

if __name__ == "__main__":
    fetch_atmarkit_articles()
