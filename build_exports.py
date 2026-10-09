# -*- coding: utf-8 -*-
"""离线导出：PDF / EPUB / Anki（.apkg）。
函数均接收 chapters（gen_出海指南.chapters 的同构列表），便于主生成器直接调用；
本文件 __main__ 可独立运行：python3 build_exports.py
"""
import os
import io
import zipfile
import datetime

# ----------------------------------------------------------------------------
# 公共：把条目渲染为 HTML 片段
# ----------------------------------------------------------------------------
def _esc(s):
    if s is None:
        return ""
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))

def entry_html(e):
    parts = ['<div class="entry">']
    parts.append('<h3>%s %s</h3>' % (_esc(e["n"]), _esc(e["title"])))
    if e.get("tags"):
        parts.append('<p class="tags">%s</p>' % _esc(e["tags"]))
    for label, key in (("成本", "cost"), ("说人话", "plain"), ("收益", "gain"),
                       ("证据等级", "ev"), ("来源", "src")):
        v = e.get(key) or ""
        # 字段值多已带「标签：」前缀，避免重复；没有则补上
        if v and not v.lstrip().startswith(label):
            v = label + "：" + v
        parts.append('<p><b>%s</b> %s</p>' % (label, _esc(v)))
    if e.get("note"):
        parts.append('<p class="note"><b>备注</b> %s</p>' % _esc(e["note"]))
    parts.append('</div>')
    return "\n".join(parts)

def chapter_html(c):
    out = ['<section class="chapter">',
           '<h2>第%s章 %s</h2>' % (_esc(c["no"]), _esc(c["title"]))]
    if c.get("q"):
        out.append('<p class="q">%s</p>' % _esc(c["q"]))
    if c.get("intro"):
        out.append('<p class="intro">%s</p>' % _esc(c["intro"]))
    for e in c["entries"]:
        out.append(entry_html(e))
    out.append('</section>')
    return "\n".join(out)

# ----------------------------------------------------------------------------
# PDF（reportlab + 中文）
# ----------------------------------------------------------------------------
def build_pdf(chapters, path="高性价比出海指南.pdf"):
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_LEFT
    from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                    PageBreak, HRFlowable)
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.cidfonts import UnicodeCIDFont

    # 注册中文字体：优先 Adobe 内置 CID（无文件依赖），失败回退 PingFang TTC
    FONT = "Helvetica"
    try:
        pdfmetrics.registerFont(UnicodeCIDFont("STSong-Light"))
        FONT = "STSong-Light"
    except Exception:
        try:
            from reportlab.pdfbase.ttfonts import TTFont
            pdfmetrics.registerFont(TTFont("PingFang",
                "/System/Library/Fonts/PingFang.ttc", subfontIndex=0))
            FONT = "PingFang"
        except Exception:
            FONT = "Helvetica"

    total = sum(len(c["entries"]) for c in chapters)
    styles = getSampleStyleSheet()
    h1 = ParagraphStyle("h1", parent=styles["Heading1"], fontName=FONT,
                        fontSize=20, spaceAfter=10, textColor="#1a3c5e")
    h2 = ParagraphStyle("h2", parent=styles["Heading2"], fontName=FONT,
                        fontSize=14, spaceBefore=12, spaceAfter=6,
                        textColor="#1a3c5e")
    h3 = ParagraphStyle("h3", parent=styles["Heading3"], fontName=FONT,
                        fontSize=11.5, spaceBefore=8, spaceAfter=2,
                        textColor="#b35900")
    body = ParagraphStyle("body", parent=styles["BodyText"], fontName=FONT,
                         fontSize=9.5, leading=14, alignment=TA_LEFT)
    small = ParagraphStyle("small", parent=body, fontSize=8.5,
                          textColor="#555555")
    tagp = ParagraphStyle("tagp", parent=small, textColor="#2e7d32")

    doc = SimpleDocTemplate(path, pagesize=A4, leftMargin=18*mm,
                           rightMargin=18*mm, topMargin=18*mm,
                           bottomMargin=16*mm,
                           title="高性价比出海指南", author="leo-bone")
    E = []

    # 封面
    E.append(Spacer(1, 40*mm))
    E.append(Paragraph("高性价比出海指南", h1))
    E.append(Paragraph("给中国人的循证出海实操手册 · 离线 PDF 版", body))
    E.append(Spacer(1, 6*mm))
    E.append(Paragraph("共 %d 章 · %d 条 · 每条附证据等级与官方出处" %
                       (len(chapters), total), body))
    E.append(Spacer(1, 4*mm))
    E.append(Paragraph("生成日期：%s" % datetime.date.today().isoformat(), small))
    E.append(Paragraph("内容以 CC BY 4.0 发布；重大决策请咨询持牌专业人士。",
                       small))
    E.append(PageBreak())

    # 目录
    E.append(Paragraph("目录", h2))
    for c in chapters:
        E.append(Paragraph("第%s章 %s（%d 条）" %
                           (c["no"], c["title"], len(c["entries"])), small))
    E.append(PageBreak())

    # 正文
    for c in chapters:
        E.append(Paragraph("第%s章 %s" % (c["no"], c["title"]), h2))
        if c.get("q"):
            E.append(Paragraph(_esc(c["q"]), small))
        if c.get("intro"):
            E.append(Paragraph(_esc(c["intro"]), body))
        E.append(HRFlowable(width="100%", thickness=0.4, color="#cccccc",
                           spaceBefore=4, spaceAfter=6))
        for e in c["entries"]:
            E.append(Paragraph("%s %s" % (_esc(e["n"]), _esc(e["title"])), h3))
            if e.get("tags"):
                E.append(Paragraph(_esc(e["tags"]), tagp))
            for label, key in (("成本", "cost"), ("说人话", "plain"),
                               ("收益", "gain"), ("证据等级", "ev"),
                               ("来源", "src")):
                v = e.get(key) or ""
                if v and not v.lstrip().startswith(label):
                    v = label + "：" + v
                E.append(Paragraph("<b>%s</b> %s" % (label, _esc(v)), body))
            if e.get("note"):
                E.append(Paragraph("<b>备注</b> %s" % _esc(e["note"]), small))
            E.append(Spacer(1, 4))
    doc.build(E)
    return path

# ----------------------------------------------------------------------------
# EPUB（标准 zip 结构，EPUB3）
# ----------------------------------------------------------------------------
def build_epub(chapters, path="高性价比出海指南.epub"):
    total = sum(len(c["entries"]) for c in chapters)
    css = ("body{font-family:'Songti SC','Noto Serif CJK SC',serif;"
           "line-height:1.7;margin:1.2em;color:#222}"
           "h1,h2{color:#1a3c5e}h3{color:#b35900;font-size:1.05em}"
           ".tags{color:#2e7d32;font-size:.85em}.note{color:#666;font-size:.85em}"
           ".q,.intro{color:#444;font-style:italic}.entry{border-bottom:"
           "1px solid #eee;padding-bottom:.6em;margin-bottom:.6em}")
    # 一个 content 文件容纳全部内容（轻量且兼容）
    body_parts = []
    for c in chapters:
        body_parts.append(chapter_html(c))
    content_xhtml = (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<!DOCTYPE html><html xmlns="http://www.w3.org/1999/xhtml"'
        ' xml:lang="zh" lang="zh"><head><meta charset="utf-8"/>'
        '<title>高性价比出海指南</title><style>%s</style></head><body>' % css
        + '<h1>高性价比出海指南</h1><p>共 %d 章 %d 条</p>' % (len(chapters), total)
        + "\n".join(body_parts)
        + '</body></html>')

    # nav
    nav_items = "".join('<li><a href="content.xhtml#ch%s">第%s章 %s</a></li>'
                        % (c["no"], c["no"], _esc(c["title"])) for c in chapters)
    nav_xhtml = (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<!DOCTYPE html><html xmlns="http://www.w3.org/1999/xhtml"'
        ' xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="zh" lang="zh">'
        '<head><meta charset="utf-8"/><title>目录</title></head><body>'
        '<nav epub:type="toc" id="toc"><h1>目录</h1><ol>' + nav_items
        + '</ol></nav></body></html>')

    # content.opf
    item_meta = ('<item id="content" href="content.xhtml"'
                 ' media-type="application/xhtml+xml"/>'
                 '<item id="nav" href="nav.xhtml"'
                 ' media-type="application/xhtml+xml"'
                 ' properties="nav"/>'
                 '<item id="css" href="style.css" media-type="text/css"/>')
    opf = (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<package xmlns="http://www.idpf.org/2007/opf" version="3.0"'
        ' unique-identifier="bookid"><metadata '
        'xmlns:dc="http://purl.org/dc/elements/1.1/">'
        '<dc:identifier id="bookid">urn:uuid:howtogo-global-better</dc:identifier>'
        '<dc:title>高性价比出海指南</dc:title>'
        '<dc:language>zh</dc:language>'
        '<dc:creator>leo-bone</dc:creator>'
        '<meta property="dcterms:modified">%sT00:00:00Z</meta>'
        '</metadata><manifest>%s'
        '<item id="ncx" href="nav.xhtml" media-type="application/xhtml+xml"/>'
        '</manifest><spine><itemref idref="nav"/>'
        '<itemref idref="content"/></spine></package>'
        % (datetime.date.today().isoformat(), item_meta))

    container = (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<container version="1.0" '
        'xmlns="urn:oasis:names:tc:opendocument:xmlns:container">'
        '<rootfiles><rootfile full-path="OEBPS/content.opf" '
        'media-type="application/oebps-package+xml"/></rootfiles>'
        '</container>')

    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("mimetype", "application/epub+zip")  # 不压缩，按规范必须首条且不压缩
        # 重新以 STORE 写 mimetype
        z.writestr("META-INF/container.xml", container)
        z.writestr("OEBPS/content.opf", opf)
        z.writestr("OEBPS/nav.xhtml", nav_xhtml)
        z.writestr("OEBPS/content.xhtml", content_xhtml)
        z.writestr("OEBPS/style.css", css)
    # mimetype 需为未压缩且位于首位
    _fix_mimetype(path)
    return path

def _fix_mimetype(path):
    """把 mimetype 重新以 STORE 方式写入到 zip 开头。"""
    data = io.BytesIO()
    with zipfile.ZipFile(path, "r") as z:
        names = z.namelist()
        infos = {i.filename: i for i in z.infolist()}
        content = {n: z.read(n) for n in names}
    with zipfile.ZipFile(data, "w") as z:
        # 先写 mimetype（STORE）
        z.writestr(zipfile.ZipInfo("mimetype",
                    date_time=(1980,1,1,0,0,0)),
                   content["mimetype"],
                   compress_type=zipfile.ZIP_STORED)
        for n in names:
            if n == "mimetype":
                continue
            zi = infos[n]
            z.writestr(zi, content[n])
    with open(path, "wb") as f:
        f.write(data.getvalue())

# ----------------------------------------------------------------------------
# Anki（genanki → .apkg）
# ----------------------------------------------------------------------------
def build_anki(chapters, path="高性价比出海指南.apkg"):
    import genanki
    DECK_ID = 2061031101
    MODEL_ID = 2061031102
    model = genanki.Model(
        MODEL_ID, "高性价比出海指南",
        fields=[{"name": "Front"}, {"name": "Back"}],
        templates=[{"name": "卡片", "qfmt": "{{Front}}",
                    "afmt": "{{Front}}<hr id=\"answer\"/>{{Back}}"}])
    deck = genanki.Deck(DECK_ID, "高性价比出海指南")
    for c in chapters:
        for e in c["entries"]:
            front = "<h3>%s %s</h3>" % (_esc(e["n"]), _esc(e["title"]))
            if e.get("tags"):
                front += '<p style="color:#2e7d32;font-size:.85em">%s</p>' % _esc(e["tags"])
            front += "<p>%s</p>" % _esc(e.get("plain") or "")
            back = ""
            for label, key in (("成本", "cost"), ("收益", "gain"),
                               ("证据等级", "ev"), ("来源", "src")):
                v = e.get(key) or ""
                if v and not v.lstrip().startswith(label):
                    v = label + "：" + v
                back += "<p><b>%s</b> %s</p>" % (label, _esc(v))
            if e.get("note"):
                back += '<p style="color:#666">%s</p>' % _esc(e["note"])
            deck.add_note(genanki.Note(model=model, fields=[front, back]))
    genanki.Package(deck).write_to_file(path)
    return path

# ----------------------------------------------------------------------------
if __name__ == "__main__":
    import gen_出海指南 as g
    print("PDF  ->", build_pdf(g.chapters))
    print("EPUB ->", build_epub(g.chapters))
    print("Anki ->", build_anki(g.chapters))
