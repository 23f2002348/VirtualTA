import requests
import json
import time
from datetime import datetime
from urllib.parse import urljoin
from datetime import timezone


# === CONFIG ===
BASE_URL = "https://discourse.onlinedegree.iitm.ac.in"
CATEGORY_ID = 34
COOKIE = "_fbp=fb.2.1695117688414.197948432; _ga_5HTJMW67XK=GS2.1.s1746889600$o26$g0$t1746889603$j0$l0$h0; _ga_QHXRKWW9HH=GS2.3.s1746889619$o1$g0$t1746889619$j0$l0$h0; _ga=GA1.1.1723869132.1746205494; _ga_YRLBGM14X9=GS2.1.s1746889600$o1$g1$t1746889966$j24$l0$h0; _gcl_gs=2.1.k1$i1746890299$u129582030; _gcl_aw=GCL.1746890530.Cj0KCQjw8vvABhCcARIsAOCfwwoHpWyspEGDjZdaVEx_WSBPT7rA2d4qRwrn2Kw2EIXX5I7-ubWpJxkaAkGREALw_wcB; _ga_08NPRH5L4M=GS2.1.s1749645908$o102$g1$t1749645910$j58$l0$h0; _bypass_cache=true; _t=BYXfMhDu7bYXtOakFY2i86u4rn3gMevtd%2BrGUO3Xz9lEGrlNnu2i3XVRcic5XpB8AJ391dIf%2F6%2Fe7lsZI5PTbVmMRpBvjiPwa%2F7UQJmnAR6cKyvFKbDl00sS7nOS6P2gKO2jwlvIVbIXaCGK7OAz%2BYFUx8o4qfQc6w9B1%2FWJgGm1w%2FxD0L3fV3g01%2F5ii2Wj3O1wwcWOAiU%2BxEi3T1%2FtO5FH78Lbem5Cv9m0%2BeNVwVZeOwpg41xltSNqqxFKgeWh1iM%2FwIhf4qNMPS5YouF8R%2BJYc2wZ86%2FXI2alXaaW%2BGrnIV7NzPzN%2F29t60aVe7BX--6nipB51gshfHu9gf--dJzK%2FwUBNzzrNA1s226hFg%3D%3D; _forum_session=xoNvD889%2BmSazsmvXZAPVjglXJSpJBdnzQflU3HHlOyLIYWkqEre%2B3zYt6h2N43qaafFKval5%2BXqJ%2FiU5LqZU9wollPpDBvueLV9IlQHnLHUnJquPJD%2FS0F0kLTMaPCPE3zkn6%2FmTJM4eiM1yhqzGTvscbjJaija7YXwzNBc0yB2%2F61Go81lA2golFGp9bG3D0jVRW73CeXfvkUdjs%2B5tlWP2PGl2wnlWgStUE8rxA1FOsc9kqpwjNSwRMDc77pot6gW4DXccHhUi85vA%2FQnuqhKULYq0VH6QuHNIagSZavP2pW7hEb72Ebz8CJGQWLCr7zF33TOO5qYb7ieMKqhMS%2FouZpQ1z29tUBoh7FuDvzDpg%2FICftvfT48T1iBGg%3D%3D--4Zc1Wk27Ad2R%2F3YI--Y1GGelvflibIZHPwzNpIxw%3D%3D"

START_DATE = datetime(2024, 12, 31, tzinfo=timezone.utc)
END_DATE = datetime(2025, 4, 16, tzinfo=timezone.utc)


# Set initial cookie string


# Parse cookie string into dictionary
def parse_cookie_string(cookie_str):
    return dict(item.strip().split("=", 1) for item in cookie_str.split("; ") if "=" in item)

# Setup session with initial cookies
session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json"
})
session.cookies.update(parse_cookie_string(COOKIE))

# A helper to update session cookie from response
def update_cookie_from_response(resp):
    new_cookies = resp.cookies.get_dict()
    if new_cookies:
        session.cookies.update(new_cookies)

#print(session.cookies.get_dict())
"""
HEADERS = {
    "Cookie": COOKIE,
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json"
}"""



def get_category_topics(page):
    """Fetch topics in a category page."""
    url = f"{BASE_URL}/c/courses/tds-kb/{CATEGORY_ID}.json?page={page}"
    print(f"Fetching page {page} → {url}")
    response = session.get(url)
    #print("Updated cookies:", session.cookies.get_dict())
    update_cookie_from_response(response)
    print("✅ Got JSON. Current session cookies:")
    response.raise_for_status()
    return response.json()

def get_all_posts_in_topic(topic_id,total_posts):
    """Fetch all posts in a topic via pagination."""
    c=0

    url = f"{BASE_URL}/t/{topic_id}.json"
    response = session.get(url)
    update_cookie_from_response(response)
    c+=1
    response.raise_for_status()
    topic_data = response.json()

    post_ids = topic_data.get("post_stream", {}).get("stream", [])
    print(f"📦 Total post IDs found: {len(post_ids)}")

    all_posts = []
    batch_size = 20
    for i in range(0, len(post_ids), batch_size):
        batch = post_ids[i:i + batch_size]
        params = [("post_ids[]", str(pid)) for pid in batch]
        url = f"{BASE_URL}/t/{topic_id}/posts.json"
        response = session.get(url, params=params)
        update_cookie_from_response(response)
        response.raise_for_status()
        data = response.json()
        posts = data.get("post_stream", {}).get("posts", [])
        all_posts.extend(posts)
        print(f"✅ Fetched {len(posts)} posts for batch {i // batch_size + 1}")
        time.sleep(1)
        if c==5:
            time.sleep(5)
            c+=1

    return all_posts
    """Fetch full topic thread."""

def scrape_topics_within_timeframe():
    all_topics = []
    page = 1
    keep_fetching = True

    while keep_fetching:
        data = get_category_topics(page)
        topics = data.get("topic_list", {}).get("topics", [])
        

        if page == 6:
            keep_fetching = False
        if not topics:
            break  # no more pages

        for topic in topics:
            topic_id = topic["id"]
            total_posts = topic["posts_count"]
            topic_created_at = topic.get("created_at")
            if not topic_created_at:
                continue

            try:
                created_dt = datetime.fromisoformat(topic_created_at.replace("Z", "+00:00"))
            except Exception as e:
                print(f"⚠️ Skipping topic {topic_id} due to date parsing error: {e}")
                continue

            if created_dt > END_DATE:
                continue  # future topic, skip

            print(f"📥 Fetching posts from topic {topic_id} created at {created_dt}")
            try:
                full_posts = get_all_posts_in_topic(topic_id, total_posts)
                matching_posts = [
                    p for p in full_posts
                    if "created_at" in p and START_DATE <= datetime.fromisoformat(p["created_at"].replace("Z", "+00:00")) <= END_DATE
                ]

                if matching_posts:
                    print(f"✅ {len(matching_posts)} posts matched date range in topic {topic_id}")
                    all_topics.append({
                        "topic_id": topic_id,
                        "topic_created_at": topic_created_at,
                        "posts": matching_posts
                    })
            except Exception as e:
                print(f"⚠️ Error fetching posts for topic {topic_id}: {e}")
                continue


            if created_dt < START_DATE:
                continue  # skip topic outside range

        page += 1

    return all_topics


if __name__ == "__main__":
    threads = scrape_topics_within_timeframe()
    with open("discourse_threadsV4.json", "w") as f:
        json.dump(threads, f, indent=2)
    print(f"✅ Done. Saved {len(threads)} threads.")
