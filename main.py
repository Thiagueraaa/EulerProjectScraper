import os
import re
from time import sleep

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://projecteuler.net/"
LIST_URL = "https://projecteuler.net/archives"
OUTPUT_DIR = "./Problems"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def slugify(text):
    text = text.lower()
    text = re.sub(r"[^a-z0-9 ]", "", text)
    text = text.replace(" ", "-")
    return text[:80]


def save_file(problem_id, title, content):
    fname = f"{problem_id:04d}-{slugify(title)}.mdx"
    path = os.path.join(OUTPUT_DIR, fname)

    if os.path.exists(path):
        print(f"🟡 Already exists, skipping: {fname}")
        return False

    with open(path, "w", encoding="utf-8") as f:
        f.write(f"# Problem {problem_id}: {title}\n\n")
        f.write(content)
        print(f"🟢 Saved: {path}")
        return True


def scrape_problem(problem_id):
    url = f"{BASE_URL}problem={problem_id}"
    print(f"\nDownloading {url}...")

    r = requests.get(url)
    if r.status_code != 200:
        print(f"❌ Problem {problem_id} does not exist! (status {r.status_code}).")
        return False

    soup = BeautifulSoup(r.text, "html.parser")

    # Title
    title_tag = soup.select_one("h2")
    if not title_tag:
        print(f"❌ Title from problem {problem_id} does not exist!")
        return False
    title = title_tag.text.strip()

    # Content
    content_div = soup.select_one(".problem_content")
    if not content_div:
        print(f"❌ Content from problem {problem_id} does not exist!")
        return False
    content = content_div.get_text("\n", strip=True)

    return save_file(problem_id, title, content)


def get_total_problems():
    # Read page from archives to find how many problems exists
    r = requests.get(LIST_URL)
    soup = BeautifulSoup(r.text, "html.parser")

    # lins of 'Problem=XXX'
    links = soup.select("a[href^='problem=']")
    ids = []

    for a in links:
        href = a.get("href")
        num = int(href.replace("problem=", ""))
        ids.append(num)

    return max(ids)


print("🔍 Getting total number of problems...")
total = get_total_problems()
print(f"📌 There are currently {total} problems in Project Euler..\n")

for pid in range(1, total + 1):
    scrape_problem(pid)
    sleep(0.5)

print("\n🎉 Finished! Only new problems were downloaded.")
