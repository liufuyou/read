#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从上游书单里筛出小说书源，清洗、校验后输出可直接导入「阅读」的 JSON。

用法:
    python scripts/build_sources.py            抓取、清洗、校验、生成导入页
    python scripts/build_sources.py --check    只校验已有文件，不联网
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "sources"
PAGE_DIR = ROOT / "import"

# 文件名 → (上游书单地址, 展示名)
SOURCES = [
    (
        "yck-novel.json",
        "https://www.yck2026.fun/yuedu/shuyuans/json/id/1067.json",
        "YCK 书单 1067（墨辰整理系列 7.1）",
    ),
    (
        "yiove-novel.json",
        "https://shuyuan-api.yiove.com/import/book-source-collection/"
        "f3f55c6e-723b-4055-b254-124c9d88c5cb",
        "Yiove 星辰整理书源合集",
    ),
]



# ---------- 抓取 ----------

def fetch(url: str) -> list:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


# ---------- 筛选 ----------

def is_novel(source: dict) -> bool:
    # bookSourceType 0 是文本，1 听书、2 图片、3 文件、4 视频都不算小说
    if source.get("bookSourceType") != 0:
        return False
    return "小说" in str(source.get("bookSourceGroup") or "")


# ---------- 清洗 ----------

# 地址里只允许 ASCII 可见字符
URL_OK = re.compile(r"^[!-~]+$")


def normalize_url(value: str) -> str:
    """去掉地址尾部的作者标记，如 `##@遇知`、`#妍希`、`已整理`。

    只动尾巴，不动域名和路径。中间出现非 ASCII 的一律留着，交给校验去判。
    """
    url = str(value or "").replace("＃", "#").strip()
    head, sep, tail = url.partition("#")
    if sep and tail and not tail.isascii():
        url = head
    # 尾部还有中文备注或全角标点，一并削掉
    url = re.sub(r"[^\x21-\x7e]+$", "", url).strip()
    return url.rstrip("/")


def normalize(source: dict) -> dict:
    """地址做规范化，其余字段原样保留。"""
    fixed = dict(source)
    fixed["bookSourceUrl"] = normalize_url(source.get("bookSourceUrl"))
    fixed["bookSourceName"] = str(source.get("bookSourceName") or "").strip()
    return fixed


def clean_reason(source: dict) -> str | None:
    """传入已规范化的条目，返回丢弃原因；None 表示留着。"""
    name = str(source.get("bookSourceName") or "")
    url = str(source.get("bookSourceUrl") or "")

    if not name:
        return "没有书名"
    if not url.startswith(("http://", "https://")):
        return "地址不是网址"
    if not URL_OK.match(url):
        return "地址含无法识别的字符"

    parsed = urllib.parse.urlparse(url)
    if "." not in parsed.netloc:
        return "地址没有域名"

    if not str(source.get("searchUrl") or "").strip() and not str(
        source.get("exploreUrl") or ""
    ).strip():
        return "搜索和发现都为空"

    if not source.get("ruleSearch") and not source.get("ruleExplore"):
        return "没有搜索或发现规则"

    return None


def pick(sources: list) -> tuple[list, dict]:
    novel = [s for s in sources if is_novel(s)]
    kept: list = []
    dropped: dict[str, int] = {}
    seen: set = set()

    for source in novel:
        item = normalize(source)
        reason = clean_reason(item)
        if reason:
            dropped[reason] = dropped.get(reason, 0) + 1
            continue
        key = (item["bookSourceUrl"], item["bookSourceName"])
        if key in seen:
            dropped["整条重复"] = dropped.get("整条重复", 0) + 1
            continue
        seen.add(key)
        kept.append(item)

    stats = {
        "upstream": len(sources),
        "novel": len(novel),
        "kept": len(kept),
        "dropped": dropped,
    }
    return kept, stats


# ---------- 校验 ----------

def validate(items: list, filename: str) -> list[str]:
    problems: list[str] = []
    if not items:
        return [f"{filename}: 没有条目"]

    seen = set()
    for i, s in enumerate(items):
        tag = f"{filename}[{i}] {s.get('bookSourceName', '?')}"
        if s.get("bookSourceType") != 0:
            problems.append(f"{tag}: bookSourceType 不是 0")
        if "小说" not in str(s.get("bookSourceGroup") or ""):
            problems.append(f"{tag}: 分组不含「小说」")
        url = str(s.get("bookSourceUrl") or "")
        if not url.startswith(("http://", "https://")):
            problems.append(f"{tag}: 地址不是 http(s)")
        if not str(s.get("searchUrl") or "").strip() and not str(
            s.get("exploreUrl") or ""
        ).strip():
            problems.append(f"{tag}: 搜索和发现都为空")
        key = (url, str(s.get("bookSourceName") or ""))
        if key in seen:
            problems.append(f"{tag}: 条目重复")
        seen.add(key)

    return problems


def json_text(items: list) -> str:
    return json.dumps(items, ensure_ascii=False, separators=(",", ":")) + "\n"


# ---------- 导入页 ----------

PAGE_CSS = """
:root{color-scheme:light dark;--bd:#d8dee4;--fg:#1f2328;--dim:#59636e;--bg:#fff;--card:#f6f8fa;--acc:#1f6feb}
@media(prefers-color-scheme:dark){:root{--bd:#30363d;--fg:#e6edf3;--dim:#9198a1;--bg:#0d1117;--card:#161b22;--acc:#4493f8}}
*{box-sizing:border-box}
body{margin:0 auto;padding:24px 18px 60px;max-width:680px;background:var(--bg);color:var(--fg);
font:16px/1.7 -apple-system,"PingFang SC","Microsoft YaHei",sans-serif}
h1{font-size:22px;margin:0 0 6px}
p.lead{color:var(--dim);margin:0 0 22px;font-size:14px}
.card{border:1px solid var(--bd);border-radius:12px;padding:18px;margin-bottom:16px;background:var(--card)}
.card h2{font-size:17px;margin:0 0 4px}
.meta{color:var(--dim);font-size:13px;margin:0 0 14px}
a.go{display:block;text-align:center;padding:13px;border-radius:9px;background:var(--acc);color:#fff;
text-decoration:none;font-weight:600}
a.go:active{opacity:.8}
.fallback{margin-top:12px;font-size:13px;color:var(--dim)}
code{display:block;margin-top:6px;padding:9px 10px;border:1px solid var(--bd);border-radius:7px;
background:var(--bg);font-size:12px;word-break:break-all;color:var(--fg)}
.note{margin-top:24px;font-size:13px;color:var(--dim)}
.note b{color:var(--fg)}
"""


def page_html(cards: list[dict], title: str, lead: str) -> str:
    blocks = []
    for c in cards:
        blocks.append(
            f'<div class="card">\n'
            f'  <h2>{c["title"]}</h2>\n'
            f'  <p class="meta">{c["count"]} 条 · {c["size"]} · 仅小说</p>\n'
            f'  <a class="go" href="#" data-src="{c["rel"]}">一键导入「阅读」</a>\n'
            f'  <p class="fallback">按钮没反应就复制下面这条，去 App 里网络导入：'
            f'<code data-src="{c["rel"]}">—</code></p>\n'
            f'</div>'
        )
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<style>{PAGE_CSS}</style>
</head>
<body>
<h1>{title}</h1>
<p class="lead">{lead}</p>
{"".join(blocks)}
<p class="note"><b>按钮是灰色或点了没反应？</b>微信、QQ 等内置浏览器会拦截 App 唤起链接，
请点右上角「在浏览器打开」再试。没有装「阅读」的话，先去
<a href="https://github.com/liufuyou/read#第三方版本">版本对照</a>里挑一个装。</p>
<script>
// 深链 src 必须写完整地址，按当前页面位置实时算，页面部署到哪都能用
(function () {{
  var q = location.search;
  document.querySelectorAll('[data-src]').forEach(function (el) {{
    var abs = new URL(el.dataset.src, document.baseURI);
    if (q && !abs.search) abs.search = q;
    var href = abs.href;
    if (el.tagName === 'A') {{
      el.href = 'legado://import/bookSource?src=' + encodeURIComponent(href);
    }} else {{
      el.textContent = href;
    }}
  }});
}})();
</script>
</body>
</html>
"""


def build_pages(manifest: dict) -> None:
    PAGE_DIR.mkdir(exist_ok=True)
    cards = []
    for item in manifest["files"]:
        cards.append(
            {
                "title": item["title"],
                "count": item["count"],
                "size": item["size"],
                # 相对页面本身的路径：import/xxx.html 与 sources/ 同级，发布时也保持同一结构
                "rel": f"../sources/{item['name']}",
            }
        )

    # 总入口：两份都列出来
    (PAGE_DIR / "index.html").write_text(
        page_html(cards, "阅读（Legado）小说书源", "两份书源各自独立，想全要就点两次。"),
        encoding="utf-8",
        newline="\n",
    )

    # 每份再单独一个页面，互不共用
    for card, item in zip(cards, manifest["files"]):
        name = item["name"].replace(".json", "")
        (PAGE_DIR / f"{name}.html").write_text(
            page_html([card], card["title"], "这一页只有这一份书源。"),
            encoding="utf-8",
            newline="\n",
        )
    print(f"已生成 import/ 下 {len(cards) + 1} 个页面")


# ---------- 主流程 ----------

def main(argv: list[str]) -> int:
    check_only = "--check" in argv
    OUT_DIR.mkdir(exist_ok=True)

    manifest_path = OUT_DIR / "manifest.json"
    if check_only:
        if not manifest_path.exists():
            print("找不到 sources/manifest.json，先跑一次不带 --check 的生成。")
            return 1
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        problems: list[str] = []
        for item in manifest["files"]:
            path = OUT_DIR / item["name"]
            if not path.exists():
                problems.append(f"{item['name']}: 文件不存在")
                continue
            items = json.loads(path.read_text(encoding="utf-8"))
            problems += validate(items, item["name"])
        if problems:
            print("校验失败：")
            for p in problems[:20]:
                print(f"  - {p}")
            return 1
        print(f"校验通过：{len(manifest['files'])} 份文件")
        return 0

    manifest = {"generated": date.today().isoformat(), "files": []}
    for filename, url, title in SOURCES:
        try:
            raw = fetch(url)
        except Exception as exc:
            print(f"{filename}: 拉取失败 — {exc}")
            return 1

        kept, stats = pick(raw)
        problems = validate(kept, filename)
        if problems:
            print(f"{filename}: 校验失败，{len(problems)} 处问题")
            for p in problems[:10]:
                print(f"  - {p}")
            return 1

        text = json_text(kept)
        target = OUT_DIR / filename
        target.write_text(text, encoding="utf-8", newline="\n")

        size = target.stat().st_size
        manifest["files"].append(
            {
                "name": filename,
                "title": title,
                "upstream": url,
                "count": len(kept),
                "bytes": size,
                "size": f"{size / 1048576:.1f} MB",
                "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                "upstream_count": stats["upstream"],
                "novel_count": stats["novel"],
            }
        )

        dropped = "、".join(f"{k} {v}" for k, v in stats["dropped"].items()) or "无"
        print(
            f"{filename}: 上游 {stats['upstream']} → 小说 {stats['novel']} "
            f"→ 清洗后 {stats['kept']}（丢弃：{dropped}）"
        )

    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    build_pages(manifest)
    print("已生成 sources/manifest.json")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
