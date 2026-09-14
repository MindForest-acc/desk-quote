"""按底本裁决结果修正语料，并为每条写入可审计的 verified 字段。"""
from __future__ import annotations
import json, re, sys
from pathlib import Path

CP = Path.home() / "Documents/claudecode/paperweight/Resources/corpus.json"
d = json.loads(CP.read_text(encoding="utf-8"))
qs = d["quotes"]
by_text = {q["text"]: q for q in qs}

def edit(old: str, *, text: str | None = None, source: str | None = None, note: str | None = None):
    q = by_text.get(old)
    if q is None:
        print(f"  !! 找不到：{old[:20]}"); return
    if text: q["text"] = text
    if source: q["source"] = source
    if note: q["note"] = note

def drop(old: str, why: str):
    q = by_text.get(old)
    if q is None:
        print(f"  !! 找不到：{old[:20]}"); return
    qs.remove(q); print(f"  删除：{old[:24]}… （{why}）")

# —— 孙子：一律以两个见证本为准 ——
edit("十则围之，五则攻之，倍则分之，敌则能战之，少则能逃之，不若则能避之。",
     text="十则围之，五则攻之，倍则分之，敌则能战之，少则能守之，不若则能避之。")
edit("夫兵形象水，水之形避高而趋下，兵之形避实而击虚。",
     text="夫兵形象水，水之行避高而趋下，兵之胜避实而击虚。")
drop("兵无常势，水无常形，能因敌变化而取胜者，谓之神。",
     "两见证本均作「兵无成势，无恒形」，与通行写法冲突且异文读感差")
edit("无恃其不来，恃吾有以待也；无恃其不攻，恃吾有所不可攻也。",
     text="无恃其不来，恃吾有以待之；无恃其不攻，恃吾有所不可攻也。")
edit("兵非贵益多也，惟无武进，足以并力、料敌、取人而已。",
     text="兵非贵益多，无武进，足以并力、料敌、取人而已。")
edit("视卒如婴儿，故可与之赴深溪；视卒如爱子，故可与之俱死。",
     text="视卒如婴儿，故可以与之赴深溪；视卒如爱子，故可与之俱死。")
edit("进不求名，退不避罪，唯人是保，而利合于主，国之宝也。",
     text="进不求名，退不避罪，唯民是保，而利合于主，国之宝也。")

# —— 王阳明：篇目归属以《王阳明集》为准 ——
edit("知行原是两个字说一个工夫。", source="王阳明全集·答友人问")
edit("破山中贼易，破心中贼难。", source="王阳明全集·与杨仕德薛尚谦")
edit("人须在事上磨，方立得住，方能静亦定，动亦定。", source="传习录·上")
edit("悔悟是去病之药，然以改之为贵。若留滞于中，则又因药发病。", source="传习录·上")
edit("攻吾之短者是吾师。", source="传习录·中")
edit("无善无恶心之体，有善有恶意之动，知善知恶是良知，为善去恶是格物。",
     text="无善无恶是心之体，有善有恶是意之动，知善知恶是良知，为善去恶是格物。")

# —— 庄子 ——
edit("且夫水之积也不厚，则其负大舟也无力。", text="且夫水之积也不厚，则负大舟也无力。")
edit("举世誉之而不加劝，举世非之而不加沮。",
     text="且举世而誉之而不加劝，举世而非之而不加沮。")
edit("堕肢体，黜聪明，离形去知，同于大通，此谓坐忘。",
     text="离形去知，同于大通，此谓坐忘。")

# —— 墨子 ——
edit("原浊者流不清，行不信者名必秏。", text="源浊者流不清，行不信者名必秏。")
edit("天下之所以乱者，其说将何哉？则是天下之人异义。",
     text="一人则一义，二人则二义，十人则十义，其人兹众，其所谓义者亦兹众。",
     note="每个人都揣着一套自己的是非，人越多分歧越多——墨子对失序的诊断。")
edit("何谓三表？有本之者，有原之者，有用之者。",
     text="有本之者，有原之者，有用之者。",
     note="判断一句话真假的三把尺：有没有依据、有没有事实、有没有效果。")
edit("执无命者之言，是覆天下之义。", text="执有命者之言，是覆天下之义。",
     note="把一切归给命，等于取消了所有努力的意义。墨家「非命」的锋刃所在。")
drop("俭节则昌，淫佚则亡。", "《辞过》正文未获见证本，无法校验")

# —— 重新校验并写入 verified ——
idx = json.loads((Path(sys.argv[1]) / "sources/index.json").read_text(encoding="utf-8"))
VARIANT = str.maketrans({"彊": "强", "愼": "慎", "虖": "乎", "谿": "溪", "遊": "游"})
def norm(s: str) -> str:
    return re.sub(r"[^一-鿿]", "", s).translate(VARIANT)
IDXN = {b: {s: norm(t) for s, t in secs.items()} for b, secs in idx.items()}
WIT = {"sunzi": ["sunzi", "sunzi_b"], "yangming": ["yangming", "yangming_b"],
       "zhuangzi": ["zhuangzi"], "mozi": ["mozi"]}
LABEL = {"sunzi": "维基文库《孫子兵法》", "sunzi_b": "维基文库《孫子略解》(曹操注)",
         "yangming": "维基文库《傳習錄》", "yangming_b": "维基文库《王陽明集》",
         "zhuangzi": "维基文库《莊子》", "mozi": "维基文库《墨子》"}

stat = {"verified": 0, "unverified": 0}
for q in qs:
    hits = [(w, sec) for w in WIT.get(q["book"], [])
            for sec, body in IDXN[w].items() if norm(q["text"]) in body]
    if hits:
        w, sec = hits[0]
        q["verified"] = {"witness": LABEL[w], "section": sec}
        stat["verified"] += 1
    else:
        q["verified"] = None
        stat["unverified"] += 1

d["provenance"] = {
    "checked": "2026-09-14",
    "method": "逐条与维基文库公有领域底本做去标点全文比对；篇目归属以底本为准",
    "witnesses": sorted(set(LABEL.values())),
    "unverified_note": "verified 为 null 的条目未获公有领域见证本（《毛泽东选集》非公有领域；王阳明《年谱》维基文库无可检索正文），文本与出处来自模型知识，未经原书校验。",
}
CP.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"\n合计 {len(qs)} 条 | 已校验 {stat['verified']} | 未获见证本 {stat['unverified']}")
for q in qs:
    if q["verified"] is None and q["book"] != "maoxuan":
        print(f"  [未校验·非毛选] {q['source']} — {q['text'][:24]}")
