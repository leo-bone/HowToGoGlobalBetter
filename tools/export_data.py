# -*- coding: utf-8 -*-
"""把全量条目导出为结构化数据（JSON / CSV），对标标杆的「开源复用」姿态。
直接 import 生成器，复用其已构建好的 chapters 结构，无需重新解析 Markdown。
"""
import csv
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import gen_出海指南 as g

URL_RE = re.compile(r"https?://[^\s｜|）)。，,]+")


def main():
    rows = []
    for c in g.chapters:
        for e in c["entries"]:
            src = e.get("src", "") or ""
            urls = URL_RE.findall(src)
            rows.append({
                "chapter_no": c["no"],
                "chapter_title": c["title"],
                "entry_no": e["n"],
                "title": e["title"],
                "tags": e.get("tags", "") or "",
                "cost": e.get("cost", "") or "",
                "plain": e.get("plain", "") or "",
                "gain": e.get("gain", "") or "",
                "evidence": e.get("ev", "") or "",
                "source": src,
                "official_urls": " ; ".join(urls),
                "note": e.get("note", "") or "",
            })

    assert len(rows) == 634, "条目数异常：%d（预期 634）" % len(rows)
    ev = {}
    for r in rows:
        ev[r["evidence"]] = ev.get(r["evidence"], 0) + 1
    print("条目总数：%d" % len(rows))
    print("证据分级：", ev)
    print("章节数：%d" % len(g.chapters))

    with open("出海指南数据.json", "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=1)

    with open("出海指南数据.csv", "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    print("已写出：出海指南数据.json / 出海指南数据.csv")


if __name__ == "__main__":
    main()
