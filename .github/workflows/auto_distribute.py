#!/usr/bin/env python3
"""
GitHub Actions 自动分发脚本
触发条件: 新文章 push 到 source/_posts/
功能:
  1. 检测最新文章
  2. 解析 frontmatter 的 platforms 字段
  3. 生成各平台专用格式
  4. 输出到 dist/ 目录
"""
import os
import sys
import re
from pathlib import Path
from datetime import datetime

# ============ 路径 ============
REPO_ROOT = Path(os.environ.get("GITHUB_WORKSPACE", "."))
POSTS_DIR = REPO_ROOT / "hexo-blog/source/_posts"
DIST_DIR = REPO_ROOT / "dist"
BLOG_URL = os.environ.get("BLOG_URL", "https://zoebischuribe-cloud.github.io/Sunny-research")

DIST_DIR.mkdir(exist_ok=True)


def parse_frontmatter(content: str) -> dict:
    """解析 markdown frontmatter"""
    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return {}
    fm = {}
    current_key = None
    current_list = []
    for line in match.group(1).split("\n"):
        if re.match(r"^[a-z_]+:", line):
            if current_key and current_list:
                fm[current_key] = current_list
                current_list = []
            key, _, val = line.partition(":")
            current_key = key.strip()
            val = val.strip()
            if val.startswith("[") or val.startswith("-"):
                continue
            fm[key.strip()] = val
        elif line.strip().startswith("- ") and current_key:
            current_list.append(line.strip()[2:])
    if current_key and current_list:
        fm[current_key] = current_list
    return fm


def find_latest_post():
    """找最新推送的文章"""
    posts = sorted(POSTS_DIR.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)
    return posts[0] if posts else None


def md_to_wechat_html(post_path: Path, fm: dict, body: str) -> str:
    """转公众号 HTML"""
    # ... 复用 sunny-publish 里的转换逻辑
    body_html = body
    body_html = re.sub(r"```(\w*)\n(.*?)\n```",
                       lambda m: f'<pre><code class="language-{m.group(1) or ""}">{m.group(2)}</code></pre>',
                       body_html, flags=re.DOTALL)
    body_html = re.sub(r"`([^`]+)`", r"<code>\1</code>", body_html)
    body_html = re.sub(r"^#### (.*?)$", r"<h4>\1</h4>", body_html, flags=re.MULTILINE)
    body_html = re.sub(r"^### (.*?)$", r"<h3>\1</h3>", body_html, flags=re.MULTILINE)
    body_html = re.sub(r"^## (.*?)$", r"<h2>\1</h2>", body_html, flags=re.MULTILINE)
    body_html = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", body_html)
    body_html = re.sub(r"\*(.*?)\*", r"<em>\1</em>", body_html)
    body_html = re.sub(r"^> (.*?)$", r"<blockquote>\1</blockquote>", body_html, flags=re.MULTILINE)

    title = fm.get("title", post_path.stem)
    desc = fm.get("description", "")
    tags = ", ".join(fm.get("tags", [])) if isinstance(fm.get("tags"), list) else fm.get("tags", "")

    return f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8">
<title>{title}</title>
<style>
body {{ font-family: -apple-system, sans-serif; max-width: 720px; margin: 40px auto; line-height: 1.8; color: #333; }}
h2 {{ border-bottom: 2px solid #4A90E2; padding-bottom: 8px; }}
blockquote {{ border-left: 4px solid #4A90E2; padding: 12px 16px; background: #f8f9fa; }}
pre {{ background: #2d2d2d; color: #f8f8f2; padding: 16px; border-radius: 8px; }}
code {{ background: #f4f4f4; padding: 2px 6px; border-radius: 3px; }}
strong {{ color: #4A90E2; }}
</style></head><body>
<h1>{title}</h1>
<div style="color:#999;font-size:0.9em">📅 {datetime.now().strftime("%Y-%m-%d")} | 🏷️ {tags}</div>
<p><strong>摘要:</strong> {desc}</p>
<hr>
{body_html}
<hr>
<p>📍 原文链接: <a href="{BLOG_URL}/{post_path.stem}/">{BLOG_URL}/{post_path.stem}/</a></p>
<p>👤 作者: Sunny (scLLM 资深工程师)</p>
</body></html>"""


def md_to_clean(post_path: Path, fm: dict, body: str) -> str:
    """转知乎/CSDN/掘金 通用 Markdown（去掉 hexo 标签）"""
    body = re.sub(r"\{%\s*post_link\s+.*?%\}", "", body)
    body = re.sub(r"<!-- more -->", "", body)
    title = fm.get("title", post_path.stem)
    desc = fm.get("description", "")

    header = f"\n> 本文首发于个人博客: {BLOG_URL}/{post_path.stem}/\n> 知乎专栏同步更新，欢迎关注。\n\n"
    return header + body


def generate_twitter_thread(fm: dict, body: str, url: str) -> str:
    """生成 Twitter thread（每条 < 280 字符）"""
    title = fm.get("title", "")
    desc = fm.get("description", "")
    tags = " ".join(f"#{t}" for t in (fm.get("tags") or []))

    tweets = []
    # Tweet 1
    t1 = f"🧬 New post: {title[:80]}\n\nKey takeaways ↓\n\n{url}"
    if len(t1) > 280:
        t1 = f"🧬 New post: {title[:60]}...\n\n{url}"
    tweets.append(t1)
    # Tweet 2
    t2 = f"💡 Why it matters:\n\n{desc[:240]}"
    tweets.append(t2)
    # Tweet 3
    t3 = f"🏷️ Topics: {tags[:200]}\n\nFull read: {url}"
    tweets.append(t3)

    return "\n\n---\n\n".join(tweets)


def generate_linkedin_post(fm: dict, body: str, url: str) -> str:
    """生成 LinkedIn 英文摘要"""
    title = fm.get("title", "")
    desc = fm.get("description", "")
    return f"""📝 New article published: {title}

{desc}

In this post, I share practical insights for single-cell researchers looking to leverage foundation models in their work.

🔗 Read: {url}

#Bioinformatics #MachineLearning #scRNAseq #FoundationModels"""


def main():
    # 决定要处理哪篇文章
    post_file_env = os.environ.get("POST_FILE", "")
    if post_file_env and not post_file_env.startswith("AUTO:"):
        post_path = POSTS_DIR / post_file_env
        if not post_path.exists():
            print(f"❌ 文件不存在: {post_path}", file=sys.stderr)
            sys.exit(1)
    else:
        post_path = find_latest_post()
        if not post_path:
            print("❌ 没有找到文章", file=sys.stderr)
            sys.exit(1)

    print(f"📝 处理: {post_path.name}")

    # 读文件
    content = post_path.read_text(encoding="utf-8")
    fm = parse_frontmatter(content)
    body_match = re.search(r"^---\n.*?\n---\n(.*)", content, re.DOTALL)
    body = body_match.group(1) if body_match else content

    # 决定发布哪些平台（从 frontmatter 的 platforms 字段读）
    platforms = fm.get("platforms", "wechat,zhihu,csdn,juejin,twitter,linkedin")
    if isinstance(platforms, str):
        platforms = [p.strip() for p in platforms.split(",")]

    print(f"🚀 平台: {platforms}")

    # 输出目录
    out_dir = DIST_DIR / post_path.stem
    out_dir.mkdir(parents=True, exist_ok=True)

    if "wechat" in platforms:
        html = md_to_wechat_html(post_path, fm, body)
        (out_dir / "wechat.html").write_text(html, encoding="utf-8")
        print(f"  ✅ wechat.html")

    if "zhihu" in platforms or "csdn" in platforms or "juejin" in platforms:
        md = md_to_clean(post_path, fm, body)
        if "zhihu" in platforms:
            (out_dir / "zhihu.md").write_text(md, encoding="utf-8")
            print(f"  ✅ zhihu.md")
        if "csdn" in platforms:
            (out_dir / "csdn.md").write_text(md, encoding="utf-8")
            print(f"  ✅ csdn.md")
        if "juejin" in platforms:
            (out_dir / "juejin.md").write_text(md, encoding="utf-8")
            print(f"  ✅ juejin.md")

    if "twitter" in platforms:
        url = f"{BLOG_URL}/{post_path.stem}/"
        thread = generate_twitter_thread(fm, body, url)
        (out_dir / "twitter.txt").write_text(thread, encoding="utf-8")
        print(f"  ✅ twitter.txt")

    if "linkedin" in platforms:
        url = f"{BLOG_URL}/{post_path.stem}/"
        post = generate_linkedin_post(fm, body, url)
        (out_dir / "linkedin.txt").write_text(post, encoding="utf-8")
        print(f"  ✅ linkedin.txt")

    # 摘要报告
    summary = {
        "post": post_path.name,
        "title": fm.get("title", ""),
        "platforms": platforms,
        "outputs": [f.name for f in out_dir.iterdir()],
        "generated_at": datetime.now().isoformat(),
    }
    (out_dir / "manifest.json").write_text(
        __import__("json").dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    print(f"\n✅ 完成: {out_dir}")


if __name__ == "__main__":
    main()