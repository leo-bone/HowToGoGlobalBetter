# -*- coding: utf-8 -*-
"""
《高性价比出海指南》分册生成器 —— 对标《高性价比人生指南》的 34 分册结构。

把单一的大文件 高性价比出海指南.md 按「第 N 章」拆成 分册/ 下的独立 Markdown，
并生成 分册/README.md 索引。每个分册自包含、可精读、可打印、可定向分享。

用法（在仓库根目录执行）：
    python3 tools/build_booklets.py
依赖：仅标准库；章节顺序与标题取自 gen_出海指南（用于索引的「想搞清楚」字段）。
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

MD_PATH = os.path.join(ROOT, "高性价比出海指南.md")
OUT_DIR = os.path.join(ROOT, "分册")


def safe_name(ch_no, title):
    """生成安全的文件名片段：保留中文/数字/·/（），替换文件系统的非法字符。"""
    s = "第%02d章_%s" % (ch_no, title)
    for ch in '/\\:*"<>|?':
        s = s.replace(ch, "_")
    s = s.strip().replace(" ", "_")
    return s + ".md"


def split_chapters(text):
    """按 '## N. 标题' 切分，返回 [(no, title, body), ...]。"""
    pat = re.compile(r"^##\s+(\d+)\.\s+(.+)$", re.M)
    matches = list(pat.finditer(text))
    out = []
    for i, m in enumerate(matches):
        no = int(m.group(1))
        title = m.group(2).strip()
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[start:end].strip("\n")
        out.append((no, title, body))
    return out


def main():
    text = open(MD_PATH, encoding="utf-8").read()
    chapters = split_chapters(text)
    if not chapters:
        print("未找到任何「第 N 章」标题，退出。")
        sys.exit(1)
    os.makedirs(OUT_DIR, exist_ok=True)

    # 索引所需的「想搞清楚」字段来自生成器（若有）
    q_of = {}
    try:
        import gen_出海指南 as g  # noqa
        for c in g.chapters:
            q_of[c["no"]] = c.get("q", "")
    except Exception:
        pass

    written = []
    for no, title, body in chapters:
        # 把分册首行的 '## N. 标题' 升为 H1 '# 第 N 章 标题'
        body = re.sub(r"^##\s+\d+\.\s+.*$", "# 第 %d 章 %s\n" % (no, title),
                     body, count=1, flags=re.M)
        fname = safe_name(no, title)
        with open(os.path.join(OUT_DIR, fname), "w", encoding="utf-8") as f:
            f.write(body + "\n")
        written.append((no, title, fname, q_of.get(no, "")))

    # 写索引 README
    L = []
    L.append("# 高性价比出海指南 · 分册索引")
    L.append("")
    L.append("> 单一大文件按章拆成的独立 Markdown，适合精读、打印与定向分享。")
    total_entries = len(re.findall(r"^###\s+\d+\.\d+", text, re.M))
    L.append("> 全部 %d 章、%d 条；正文总入口见仓库根目录 `高性价比出海指南.md` 与 `入口.html`。" % (
        len(written), total_entries))
    L.append("")
    L.append("| 章 | 标题 | 想搞清楚 | 分册文件 |")
    L.append("|---|---|---|---|")
    for no, title, fname, q in written:
        L.append("| 第 %d 章 | %s | %s | [%s](%s) |" % (no, title, q, fname, fname))
    with open(os.path.join(OUT_DIR, "README.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")

    print("已生成 %d 个分册 + 索引：%s" % (len(written), OUT_DIR))


if __name__ == "__main__":
    main()
