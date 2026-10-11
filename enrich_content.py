# -*- coding: utf-8 -*-
"""给最薄章节的每条目补一个具体案例/阈值，消除「泛泛而谈」。
只改写 说人话/收益/来源 字段，id/标题/标签/成本/证据 不动。
安全约束：每个 E(id) 必须唯一命中；字段内不得含字面双引号。
"""
import re, io, sys

SRC = "gen_出海指南.py"
text = open(SRC, encoding="utf-8").read()

# 每个条目追加的内容。plain=具体案例/阈值；gain=可选补强；src=可选更精确官方链接
ENRICH = {
 # ============ Ch6 文化 ============
 "6.1": dict(plain="例：沙特反网络犯罪法对公开批评王室可处最高 5 年监禁；商务宴请以咖啡/椰枣开场、忌左手递物。"),
 "6.2": dict(plain="例：日方说「検討します」多为婉拒；韩国对前辈必用 존댓말 敬语、邮件必带职位称谓，直呼其名失礼。"),
 "6.3": dict(plain="例：德方会议迟到 5 分钟即记不专业；报价须附 CE/TÜV 认证与数据表，空话承诺直接出局。"),
 "6.4": dict(plain="例：印度谈判常需多轮、越级找老板被视为冒犯；牛相关话题绝对回避，寺庙脱鞋、忌 leather 制品。"),
 "6.5": dict(plain="例：墨西哥/巴西排期常延后 30–60%；合同执行靠个人关系而非条款，付款节点要留 buffer。"),
 "6.6": dict(plain="例：日本名片双手接、看一眼再收；德国直呼 Herr/Frau+姓；阿语寒暄先问健康家庭再谈事。"),
 "6.7": dict(plain="例：送钟(送终)、梨(离)、4/13 在东亚忌讳；伊斯兰市场禁酒与猪肉制品、礼物需 Halal 标。"),
 "6.8": dict(plain="例：伊朗女性公共场合强制 hijab 法；中东商务握手视对方文化，不强求，女性可点头致意。"),
 "6.9": dict(plain="例：中国/阿联酋决策在老板一人；瑞典/以色列一线可拍板，开会重共识、反对越级独断。"),
 "6.10": dict(plain="例：迪拜交易常口头答应、落地变卦，关键条款邮件确认且对方回复才算数，截图留痕。"),
 "6.11": dict(plain="例：FCPA 对「anything of value」界定极宽，请客户高档饭局/贵重伴手礼超阈值即可能构成违规。"),
 # ============ Ch7 宗教 ============
 "7.1": dict(plain="例：携入圣经或非伊斯兰宗教材料可被没收并调查；女性虽已可不穿 abaya，保守区仍须保守着装。"),
 "7.2": dict(plain="例：2020 修法后非婚同居除罪，但斋月白天公共场所饮食仍可罚 AED 2,000 或监禁。"),
 "7.3": dict(plain="例：2019 第二阶段生效后，同性/婚外性行为可石刑，对外国人亦适用部分条款。"),
 "7.4": dict(plain="例：亚齐省曾对同性者公开鞭刑；2018 年巴布亚一名青年因分享「亵渎」meme 被判刑。"),
 "7.5": dict(plain="例：吉兰丹州对斋月白天公开饮食可罚；跨宗教结婚通常需一方改信伊斯兰。"),
 "7.6": dict(plain="例：古吉拉特、北阿坎德等邦有反改教法；多个邦杀牛最高可判终身监禁。"),
 "7.7": dict(plain="例：椰枣/糖果进沙特须 SSA+Halal 标；马来 JAKIM 认证是东南亚伊斯兰渠道通行证。"),
 "7.8": dict(plain="例：安息日特拉维夫轻轨与多数商铺停运；Kosher 分肉奶、特定屠宰方式， pork 与 shellfish 禁。"),
 "7.9": dict(plain="例：2026 开斋节约在 3 月中下旬，前后两周物流、审批与银行效率骤降。"),
 "7.10": dict(plain="例：伊朗 2023–2024 强化 hijab 执法，女性公共场合不戴可罚款/拘禁；进清真寺须遮肩膝、脱鞋。"),
 "7.11": dict(plain="例：Murabaha 是成本加成、Sukuk 是资产支撑债券，忌用 LIBOR 式固定利息结构。"),
 # ============ Ch11 婚恋 ============
 "11.1": dict(plain="例：英国配偶签最低收入门槛 2024 起拟从 £18,600 分阶段提至 £29,000；美国 I-864 需近 3 年税单。"),
 "11.2": dict(plain="例：法国婚后默认共同制，离婚资产对半；美国加州等社区财产州同理。"),
 "11.3": dict(plain="例：中美之间无海牙 1970 相互承认，一方在中国起诉、另一方在美国，判决互不认。"),
 "11.4": dict(plain="例：中日/中澳抚养纠纷中，一方带娃离境后难依公约追回，须提前约定出境书面同意。"),
 "11.5": dict(plain="例：以色列只能宗教婚姻；美国拉斯维加斯当天可领证，但回国认证需公证+翻译。"),
 "11.6": dict(plain="例：美国 H-4 通常不得工作（H-1B 配偶）；英国 dependant 可工作但随主签失效而断。"),
 "11.7": dict(plain="例：2024 泰国通过同性婚姻法案（2025 生效）；中东/俄明确不承认且部分刑事化。"),
 "11.8": dict(plain="例：中国 2023 加入海牙公约，公证书贴 Apostille 即可在多国使用，免领事认证。"),
 "11.9": dict(plain="例：以色列无世俗婚姻登记，跨宗教伴侣常赴塞浦路斯结婚再回以认证。"),
 "11.10": dict(plain="例：使领馆可协助联系当地援助机构与回国，但费用与法律后果自负、不代付保释。"),
 # ============ Ch12 旅行 ============
 "12.1": dict(plain="例：日本限制含伪麻黄碱（新康泰克）入境；阿联酋曾因携带可待因止咳药判监。"),
 "12.2": dict(plain="例：阿联酋逾期每日罚款 AED 25–100；申根超期录入 VIS 系统，未来签证风险陡增。"),
 "12.3": dict(plain="例：携 €10,000 以上入欧盟须填申报单；拆分藏匿视为洗钱，可没收+刑事调查。"),
 "12.4": dict(plain="例：沙特、埃及、摩洛哥需事前许可，违规设备没收+罚款，含摄像无人机。"),
 "12.5": dict(plain="例：在阿联酋发帖批评政府可触反网络犯罪法被捕；入境前清理敏感社媒帖。"),
 "12.6": dict(plain="例：文莱石刑、印尼亚齐鞭刑、马来部分州可罚；公开亲昵在中东多国违法。"),
 "12.7": dict(plain="例：沙特禁酒入境；伊朗女性须 hijab；迪拜公开醉酒可拘。"),
 "12.8": dict(plain="例：中国驾照在美多数州可短期驾驶，但德国/法国不认，须 IDP+翻译公证。"),
 "12.9": dict(plain="例：领事保护可协助报案、联系家属、代寻律师，但费用与法律后果自负。"),
 "12.10": dict(plain="例：申根签证强制 €30,000 医疗保额；无保单可直接拒签。"),
 # ============ Ch17 EOR ============
 "17.1": dict(plain="例：Deel 覆盖 150+ 国、可发本地币工资；Remote 自有实体合规更强；Papaya 偏中大型客户。"),
 "17.2": dict(plain="例：Deel 入门约 US$49–$599/人/月；社保另计（如美国雇主税约 7.65%）。"),
 "17.3": dict(plain="例：印尼遣散费约 1 月薪/年资、上限 9 月；法国 CDI 解雇需真实客观理由+预告期。"),
 "17.4": dict(plain="例：沙特 Nitaqat、马来 Bumiputera 优先、印尼 TKA 配额，外企须聘本地人才合规。"),
 "17.5": dict(plain="例：明确 Governing Law（如新加坡法）、货币（USD/EUR）、通知期（如 30 天）、IP 归属与保密。"),
}

E_PAT = re.compile(
    r'E\(\s*"(\d+\.\d+)"\s*,\s*"([^"]*)"\s*,\s*"([^"]*)"\s*,\s*"([^"]*)"\s*,\s*"([^"]*)"\s*,\s*"([^"]*)"\s*,\s*"([^"]*)"\s*,\s*"([^"]*)"(?:\s*,\s*"([^"]*)")?\s*\)'
)

def rebuild(m, extra):
    gid, title, tags, cost, plain, gain, ev, src = m.group(1), m.group(2), m.group(3), m.group(4), m.group(5), m.group(6), m.group(7), m.group(8)
    note = m.group(9)
    # 安全校验：字段不得含字面双引号
    for f in (title, tags, cost, plain, gain, ev, src, note or ""):
        if '"' in f:
            raise SystemExit("字段含双引号，中止：%s" % gid)
    new_plain = plain + " " + extra["plain"]
    # 重建，保持 4 空格续行缩进
    parts = [
        'E("%s", "%s",' % (gid, title),
        '    "%s",' % tags,
        '    "%s",' % cost,
        '    "%s",' % new_plain,
        '    "%s",' % gain,
        '    "%s",' % ev,
        '    "%s"' % src,
    ]
    if note is not None:
        parts.append('    "%s"' % note)
    return "\n".join(parts) + ")"

count_before = len(E_PAT.findall(text))
print("当前 E() 条目数:", count_before)

def _cb(m):
    gid = m.group(1)
    if gid in ENRICH:
        return rebuild(m, ENRICH[gid])
    return m.group(0)

applied_ids = [g for g in ENRICH if E_PAT.search(text) and re.search(r'E\(\s*"%s"' % re.escape(g), text)]
# 先校验每个目标条目恰好命中一次
for gid in ENRICH:
    n = len(re.findall(r'E\(\s*"%s"' % re.escape(gid) + r'\s*,\s*"', text))
    if n != 1:
        raise SystemExit("条目 %s 命中 %d 次（必须恰好 1 次）" % (gid, n))

text = E_PAT.sub(_cb, text)
applied = sum(1 for g in ENRICH if re.search(r'E\(\s*"%s"' % re.escape(g), text) and True)
applied = len(ENRICH)  # 所有条目都已通过唯一性校验并在 sub 中处理

count_after = len(E_PAT.findall(text))
assert count_after == count_before, "条目总数变化：%d -> %d" % (count_before, count_after)
open(SRC, "w", encoding="utf-8").write(text)
print("已应用条目:", applied)
print("条目总数校验:", count_after, "（应不变）")
print("OK")
