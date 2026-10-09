# -*- coding: utf-8 -*-
"""
《高性价比出海指南》质检脚本 — 对标 HowToLiveBetter 的 tools/ 核查机制。

运行：python3 tools/check.py
退出码：0 = 全部通过；1 = 发现问题（并逐项打印）。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import gen_出海指南 as g  # noqa: E402

PRE = {"cost": "成本：", "plain": "说人话：", "gain": "收益：", "src": "来源：", "note": "备注："}


def main():
    problems = []
    chapters = g.chapters
    total = sum(len(c["entries"]) for c in chapters)

    # 1) 缺 URL
    miss = [(c["no"], e["n"]) for c in chapters for e in c["entries"] if "http" not in e["src"]]
    if miss:
        problems.append("缺官方 URL 的条目：%s" % miss)

    # 2) 重复前缀（字段被写两遍）
    for c in chapters:
        for e in c["entries"]:
            for f, p in PRE.items():
                if (e[f] or "").count(p) > 1:
                    problems.append("条 %s 字段 %s 出现重复前缀：%r" % (e["n"], f, e[f][:40]))

    # 3) 章号连续性 0..N
    nos = sorted(c["no"] for c in chapters)
    if nos != list(range(nos[0], nos[0] + len(nos))):
        problems.append("章号不连续：%s" % nos)

    # 4) 重复标题
    seen = {}
    for c in chapters:
        for e in c["entries"]:
            if e["title"] in seen:
                problems.append("重复标题：%s（%s 与 %s）" % (e["title"], seen[e["title"]], e["n"]))
            else:
                seen[e["title"]] = e["n"]

    # 5) 字段完整性
    for c in chapters:
        for e in c["entries"]:
            for f in ("cost", "plain", "gain", "ev", "src"):
                if not (e[f] or "").strip():
                    problems.append("条 %s 字段 %s 为空" % (e["n"], f))
            if not e["ev"].replace("证据等级：", "").strip() in ("A", "B", "C"):
                problems.append("条 %s 证据等级非法：%r" % (e["n"], e["ev"]))

    # 6) 空标签
    for c in chapters:
        for e in c["entries"]:
            if not (e["tags"] or "").strip():
                problems.append("条 %s 缺少标签" % e["n"])

    if problems:
        print("❌ 质检未通过，共 %d 项问题：" % len(problems))
        for p in problems:
            print("  - " + p)
        sys.exit(1)
    else:
        a = sum(1 for c in chapters for e in c["entries"] if e["ev"].endswith("A"))
        b = sum(1 for c in chapters for e in c["entries"] if e["ev"].endswith("B"))
        c = sum(1 for c in chapters for e in c["entries"] if e["ev"].endswith("C"))
        print("✅ 质检通过：%d 章 %d 条（A=%d B=%d C=%d），URL 覆盖率 100%%，无重复/无空字段。"
              % (len(chapters), total, a, b, c))
        sys.exit(0)


if __name__ == "__main__":
    main()
