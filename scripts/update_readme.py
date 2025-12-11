#!/usr/bin/env python3
"""Generate README sections for projects, stats, and blog.

- Projects: use GitHub API to fetch pinned repos (requires GH_TOKEN) or fallback sample.
- Stats: emit Markdown with images pointing to self-hosted domain env or default.
- Blogs: optional RSS feed via requests.
"""

import json
import os
import re
import urllib.request
from datetime import datetime

README_PATH = os.path.join(os.path.dirname(__file__), "..", "README.md")
OWNER = os.environ.get("GITHUB_OWNER", "AAASS554")
SELF_STATS_BASE = os.environ.get("STATS_BASE_URL", "https://github-readme-stats.vercel.app")
BLOG_FEED = os.environ.get("BLOG_FEED_URL", "")
BLOG_STATIC_MESSAGE = os.environ.get(
    "BLOG_STATIC_MESSAGE",
    "正在开发「AI 模型调度平台」（本地路径 `/Users/pepsi/Desktop/jdwa-code`），聚焦统一代理多家模型 API、Key 管理与观测。",
)
MAX_PROJECTS = int(os.environ.get("MAX_PROJECTS", "3"))
MAX_BLOG = int(os.environ.get("MAX_BLOG", "5"))
TOKEN = os.environ.get("GH_TOKEN")


def fetch_pinned_repos():
    query = {
        "query": f"""
        {{
          user(login: \"{OWNER}\") {{
            pinnedItems(first: {MAX_PROJECTS}) {{
              nodes {{
                ... on Repository {{
                  name
                  description
                  primaryLanguage {{ name }}
                  url
                }}
              }}
            }}
          }}
        }}
        """
    }
    if not TOKEN:
        return []
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps(query).encode(),
        headers={"Authorization": f"Bearer {TOKEN}"},
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.load(resp)
    nodes = data["data"]["user"]["pinnedItems"]["nodes"]
    repos = []
    for node in nodes:
        if not node:
            continue
        repos.append(
            {
                "name": node["name"],
                "desc": (node["description"] or "无描述").strip(),
                "lang": node["primaryLanguage"]["name"] if node.get("primaryLanguage") else "",
                "url": node["url"],
            }
        )
    return repos


def render_projects():
    repos = []
    try:
        repos = fetch_pinned_repos()
    except Exception as err:
        print(f"Failed to fetch pinned repos: {err}")
    if not repos:
        repos = [
            {
                "name": "Virtual-Core Lab",
                "desc": "虚拟化实验环境与 memflow 自动化分析工具包",
                "lang": "Rust / Python",
                "url": "https://github.com/AAASS554",
            }
        ]
    lines = ["| 项目 | 功能概述 | 核心技术 |", "| --- | --- | --- |"]
    for repo in repos:
        line = f"| [{repo['name']}]({repo['url']}) | {repo['desc']} | {repo['lang']} |"
        lines.append(line)
    return "\n".join(lines)


def render_stats():
    visitor = f"<img src=\"https://visitor-badge.laobi.icu/badge?page_id={OWNER}.profile\" alt=\"Visitor Count\" />"
    stats = f"<img src=\"{SELF_STATS_BASE}/api?username={OWNER}&show_icons=true&theme=tokyonight\" alt=\"GitHub Stats\" />"
    langs = f"<img src=\"{SELF_STATS_BASE}/api/top-langs/?username={OWNER}&layout=compact&theme=tokyonight\" alt=\"Top Languages\" />"
    streak = f"<img src=\"https://github-readme-streak-stats.herokuapp.com/?user={OWNER}&theme=tokyonight\" alt=\"GitHub Streak\" />"
    body = [
        "<p align=\"center\">",
        visitor,
        "</p>",
        "<p align=\"center\">",
        stats,
        "</p>",
        "<p align=\"center\">",
        langs,
        "</p>",
        "<p align=\"center\">",
        streak,
        "</p>",
    ]
    return "\n".join(body)


def fetch_blog():
    if not BLOG_FEED:
        return []
    try:
        with urllib.request.urlopen(BLOG_FEED, timeout=10) as resp:
            content = resp.read().decode()
    except Exception as err:
        print(f"Failed to fetch blog feed: {err}")
        return []
    items = re.findall(r"<item>(.*?)</item>", content, re.S)
    posts = []
    for item in items[:MAX_BLOG]:
        title_match = re.search(r"<title>(.*?)</title>", item)
        link_match = re.search(r"<link>(.*?)</link>", item)
        date_match = re.search(r"<pubDate>(.*?)</pubDate>", item)
        title = title_match.group(1).strip() if title_match else "Untitled"
        link = link_match.group(1).strip() if link_match else "#"
        date = date_match.group(1).strip() if date_match else ""
        posts.append((title, link, date))
    return posts


def render_blog():
    posts = fetch_blog()
    if not posts:
        return BLOG_STATIC_MESSAGE
    lines = []
    for title, link, date in posts:
        parts = [f"- [{title}]({link})"]
        if date:
            parts[0] += f" · {date}"
        lines.append(parts[0])
    lines.append(f"\n> Last update: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
    return "\n".join(lines)


def replace_section(text, marker, new_content):
    pattern = re.compile(rf"(<!--{marker}-start-->)(.*?)(<!--{marker}-end-->)", re.S)
    return pattern.sub(rf"\1\n{new_content}\n\3", text)


def main():
    with open(README_PATH, "r", encoding="utf-8") as f:
        content = f.read()
    content = replace_section(content, "projects", render_projects())
    content = replace_section(content, "stats", render_stats())
    content = replace_section(content, "blog", render_blog())
    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(content)
    print("README updated.")


if __name__ == "__main__":
    main()
