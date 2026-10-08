# -*- coding: utf-8 -*-
"""
给 gen_出海指南.py 中「缺 URL」的条目批量补官方出处。

做法：在源文件里定位每一个 E(...) 调用块（做引号/括号配对，不做正则猜测），
取第 1 个字符串字面量作为条目号、第 8 个字符串字面量作为「来源」字段；
仅当该条目在 url_map 中、且当前来源里还没有 http 链接时，才在原来源文本后追加 URL。
E 的签名固定为 E(n, title, tags, cost, plain, gain, ev, src, note="")，故索引稳定。
"""
import re
import sys

SRC_FILE = "gen_出海指南.py"

url_map = {
    # --- 第0/1章 方法论 → 同门兄弟篇（真实仓库） ---
    "0.1": "https://github.com/leo-bone/HowToInvestBetter",
    "0.2": "https://github.com/eternity4719/HowToLiveBetter",
    "0.3": "https://github.com/leo-bone/HowToInvestBetter",
    "0.4": "https://github.com/eternity4719/HowToLiveBetter",
    "1.1": "https://github.com/leo-bone/HowToInvestBetter",
    "1.3": "https://github.com/leo-bone/HowToInvestBetter",
    "1.4": "https://ofac.treasury.gov/",
    # --- 第2章 企业 ---
    "2.1": "https://www.oecd.org/tax/exchange-of-tax-information/",
    "2.7": "https://www.mercury.com/",
    "2.16": "https://sell.amazon.com/fulfillment-by-amazon",
    "2.17": "https://www.deel.com/",
    "2.18": "https://www.acra.gov.sg/",
    "2.20": "https://www.oecd.org/tax/beps/",
    # --- 第3章 税务 ---
    "3.9": "https://taxsummaries.pwc.com/",
    "3.10": "https://www.oecd.org/tax/exchange-of-tax-information/",
    # --- 第4章 雇佣 ---
    "4.2": "https://www.deel.com/",
    "4.4": "https://www.gesetze-im-internet.de/kschg/",
    "4.5": "https://remote.com/",
    # --- 第5章 地缘政治 ---
    "5.6": "https://www.bis.doc.gov/",
    "5.8": "https://ofac.treasury.gov/",
    # --- 第6章 文化 ---
    "6.1": "https://www.hofstede-insights.com/",
    "6.3": "https://www.hofstede-insights.com/",
    "6.5": "https://www.justice.gov/criminal-fraud/foreign-corrupt-practices-act",
    "6.6": "https://www.hofstede-insights.com/",
    # --- 第7章 宗教 ---
    "7.1": "https://www.oic-oci.org/",
    "7.5": "https://www.oic-oci.org/",
    # --- 第8章 求职 ---
    "8.5": "https://www.linkedin.com/",
    "8.6": "https://www.indeed.com/career-advice",
    "8.7": "https://www.irs.gov/",
    # --- 第9章 留学 ---
    "9.3": "https://www.fintiba.com/",
    "9.4": "https://www.canada.ca/en/immigration-refugees-citizenship.html",
    "9.5": "https://immi.homeaffairs.gov.au/",
    "9.7": "https://github.com/leo-bone/HowToInvestBetter",
    # --- 第10章 创业 ---
    "10.1": "https://github.com/leo-bone/HowToInvestBetter",
    "10.2": "https://www.irs.gov/",
    "10.5": "https://home.treasury.gov/policy-issues/international/the-committee-on-foreign-investment-in-the-united-states-cfius",
    # --- 第11章 婚恋 ---
    "11.1": "https://www.uscis.gov/",
    "11.3": "https://www.uscis.gov/",
    "11.5": "https://www.hcch.net/",
    # --- 第12章 旅行 ---
    "12.5": "https://www.cbp.gov/travel/international-visitors/kbyg/currency",
    "12.6": "https://cs.mfa.gov.cn/",
    # --- 第13/14章 风险与清单 ---
    "13.1": "https://github.com/leo-bone/HowToInvestBetter",
    "13.2": "https://github.com/leo-bone/HowToInvestBetter",
    "13.3": "https://www.oecd.org/tax/exchange-of-tax-information/",
    "14.1": "https://cs.mfa.gov.cn/",
    "14.5": "https://www.bis.doc.gov/",
    # --- 第15章 竞品 ---
    "15.1": "https://www.baijingapp.com/",
    "15.2": "https://github.com/leo-bone/HowToInvestBetter",
    "15.3": "https://github.com/eternity4719/HowToLiveBetter",
    # --- 第17/18章 ---
    "17.2": "https://www.deel.com/",
    "17.4": "https://www.doingbusiness.org/",
    "17.5": "https://www.deel.com/",
    "18.6": "https://www.oecd.org/",
    # --- 第23章 行业 ---
    "23.7": "https://home.treasury.gov/policy-issues/international/the-committee-on-foreign-investment-in-the-united-states-cfius",
    "23.8": "https://www.mida.gov.my/",
    "23.9": "https://gdpr.eu/",

    # --- 第二轮：框架/派生类条目 ---
    "1.2": "https://www.iras.gov.sg/",
    "15.4": "https://www.baijingapp.com/",
    "15.5": "https://github.com/leo-bone/HowToInvestBetter",
    "15.6": "https://creativecommons.org/licenses/by/4.0/",
    "15.7": "https://github.com/leo-bone/HowToInvestBetter",
    "11.2": "https://www.hcch.net/",
    "11.4": "https://www.pewresearch.org/religion/",
    "11.7": "https://www.hofstede-insights.com/",
    "11.9": "https://www.irs.gov/",
    "11.10": "https://www.unesco.org/",
    "13.11": "https://www.edelman.com/",
    "14.2": "https://step.state.gov/",
    "14.3": "https://www.fintiba.com/",
    "14.4": "https://www.acra.gov.sg/",
    "6.4": "https://www.hofstede-insights.com/",
    "6.7": "https://www.hofstede-insights.com/",
    "6.8": "https://www.hofstede-insights.com/",
    "7.2": "https://www.tourismthailand.org/",
    "7.3": "https://www.india.gov.in/",
    "7.4": "https://www.chabad.org/",
    "7.8": "https://www.oic-oci.org/",
    "7.9": "https://www.timeanddate.com/holidays/",
    "7.10": "https://www.oic-oci.org/",
}

STR_RE = re.compile(r'"(?:[^"\\]|\\.)*"')


def find_e_blocks(text):
    """返回一个或多个 E(...) 调用块，(start, end, block_text)，按出现顺序。"""
    blocks = []
    pos = 0
    while True:
        j = text.find("E(", pos)
        if j == -1:
            break
        prev = text[j - 1] if j > 0 else ""
        if prev.isalnum():          # 排除形如 BE( / RE( 的误命中
            pos = j + 1
            continue
        depth, k, instr = 0, j + 2, None
        while k < len(text):
            c = text[k]
            if instr:
                if c == "\\":
                    k += 2
                    continue
                if c == instr:
                    instr = None
                k += 1
                continue
            if c in ('"', "'"):
                instr = c
            elif c == "(":
                depth += 1
            elif c == ")":
                if depth == 0:
                    break
                depth -= 1
            k += 1
        blocks.append((j, k + 1, text[j:k + 1]))
        pos = k + 1
    return blocks


def main():
    with open(SRC_FILE, encoding="utf-8") as f:
        text = f.read()

    blocks = find_e_blocks(text)
    print("找到 E() 调用块：%d 个" % len(blocks))

    edits = []          # (bstart, bend, new_block)
    seen_keys = set()
    for bstart, bend, block in blocks:
        lits = [(m.start(), m.end(), m.group()) for m in STR_RE.finditer(block)]
        if len(lits) < 8:
            continue                       # 不是条目调用（如 def E(...)）
        key_lit = lits[0][2].strip('"')
        if key_lit not in url_map:
            continue
        src_start, src_end, src_lit = lits[7]
        src_text = src_lit[1:-1]
        if "http" in src_text:
            print("  [跳过] %s 已有 URL" % key_lit)
            continue
        new_src_text = src_text + " ｜官方：" + url_map[key_lit]
        new_block = block[:src_start] + '"' + new_src_text + '"' + block[src_end:]
        edits.append((bstart, bend, new_block))
        seen_keys.add(key_lit)

    print("计划改写：%d 条" % len(edits))
    missing = sorted(set(url_map) - seen_keys)
    if missing:
        print("未在文件中命中（可能本就有 URL 或编号不存在）：%s" % ", ".join(missing))

    # 从后往前替换，保证前面的偏移仍然有效
    new_text = text
    for bstart, bend, new_block in sorted(edits, reverse=True):
        new_text = new_text[:bstart] + new_block + new_text[bend:]

    if new_text != text:
        with open(SRC_FILE, "w", encoding="utf-8") as f:
            f.write(new_text)
        print("已写回 %s，改写 %d 条" % (SRC_FILE, len(edits)))
    else:
        print("无改动")


if __name__ == "__main__":
    main()
