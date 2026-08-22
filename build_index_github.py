import os
import json
import re
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

# ---------- CONFIG ----------
GITHUB_REPO = "prabhattripathi9351/Daily_leet_code"  # <-- Sahi repo name
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/contents"
# If repo is private, add token: headers = {"Authorization": "token YOUR_TOKEN"}
# ---------------------------

def get_all_files_from_github():
    """GitHub API se saari files ki list lein (recursive)"""
    files = []
    stack = [GITHUB_API_URL]
    while stack:
        url = stack.pop()
        resp = requests.get(url)
        if resp.status_code != 200:
            print(f"❌ GitHub API error: {resp.status_code}")
            break
        items = resp.json()
        for item in items:
            if item['type'] == 'file':
                # Sirf code files filter karein
                if item['name'].endswith(('.py','.cpp','.java','.js','.go','.rb','.c')):
                    files.append({
                        "name": item['name'],
                        "path": item['path'],
                        "download_url": item['download_url']
                    })
            elif item['type'] == 'dir':
                stack.append(item['url'])  # subfolder explore karein
    return files

def extract_slug(filename):
    name = os.path.splitext(filename)[0]
    name = re.sub(r'^\d+-', '', name)
    return name

def fetch_metadata(slug):
    try:
        resp = requests.post("https://leetcode.com/graphql", json={
            "query": "query q($s: String!) { question(titleSlug: $s) { difficulty topicTags { slug } } }",
            "variables": {"s": slug}
        }, timeout=10)
        q = resp.json().get('data', {}).get('question')
        if q:
            return {"difficulty": q['difficulty'].lower(), "tags": [t['slug'] for t in q['topicTags']]}
    except: pass
    return {"difficulty": "unknown", "tags": []}

def build_index():
    print("🔍 Fetching file list from GitHub API...")
    all_files = get_all_files_from_github()
    print(f"📂 Found {len(all_files)} code files.")
    
    index = []
    with ThreadPoolExecutor(max_workers=10) as ex:
        futures = {ex.submit(fetch_metadata, extract_slug(f["name"])): f for f in all_files}
        for ft in as_completed(futures):
            f = futures[ft]
            meta = ft.result()
            index.append({
                "name": f['name'],
                "slug": extract_slug(f['name']),
                "download_url": f['download_url'],
                "difficulty": meta["difficulty"],
                "tags": meta["tags"]
            })
            print(f"✅ {f['name']} -> {meta['difficulty']} / {', '.join(meta['tags'])}")
    
    with open("index.json", "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2)
    print(f"\n🎉 Done! {len(index)} problems indexed. File: index.json")

if __name__ == "__main__":
    build_index()