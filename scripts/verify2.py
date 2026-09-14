"""多见证本校验：原文是否存在 + 篇目归属是否正确。"""
from __future__ import annotations
import json, re, sys
from pathlib import Path

SP = Path(__file__).parent
idx = json.loads((SP / "sources/index.json").read_text(encoding="utf-8"))
corpus = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
norm = lambda s: re.sub(r"[^一-鿿]", "", s)

WITNESSES = {"sunzi": ["sunzi", "sunzi_b"], "yangming": ["yangming", "yangming_b"],
             "zhuangzi": ["zhuangzi"], "mozi": ["mozi"]}
ORD = re.compile(r"(第[一二三四五六七八九十]+|篇|卷)")
key = lambda s: ORD.sub("", s)

report = {"OK": [], "SECTION": [], "MISSING": [], "SKIP": []}

for q in corpus["quotes"]:
    book, claimed = q["book"], q["source"].split("·")[-1].split(" · ")[0].strip()
    if book not in WITNESSES:
        report["SKIP"].append(q); continue
    needle = norm(q["text"])
    hits = []
    for w in WITNESSES[book]:
        hits += [(w, sec) for sec, body in idx.get(w, {}).items() if needle in body]
    if not hits:
        # 定位分歧点
        best = (0, None, None)
        for L in range(len(needle), 3, -1):
            for w in WITNESSES[book]:
                for sec, body in idx.get(w, {}).items():
                    if needle[:L] in body:
                        p = body.find(needle[:L])
                        best = (L, sec, body[p:p + len(needle) + 8]); break
                if best[1]: break
            if best[1]: break
        report["MISSING"].append((q, best)); continue
    ck = key(claimed)
    if any(ck and ck in key(sec) for _, sec in hits):
        report["OK"].append(q)
    else:
        report["SECTION"].append((q, sorted({s for _, s in hits})[:4]))

n = len(corpus["quotes"])
print(f"总计 {n} 条 | 原文+篇目确认 {len(report['OK'])} | "
      f"篇目存疑 {len(report['SECTION'])} | 原文未命中 {len(report['MISSING'])} | "
      f"无见证本 {len(report['SKIP'])}")
print("=" * 74)
print("\n── 篇目存疑 ──")
for q, hits in report["SECTION"]:
    print(f"  {q['source']:28s} → 实见于 {hits}\n     {q['text'][:40]}")
print("\n── 原文未命中 ──")
for q, (L, sec, ctx) in report["MISSING"]:
    print(f"  {q['source']:28s} 前{L}/{len(norm(q['text']))}字命中 {sec}")
    print(f"     我: {norm(q['text'])[:50]}")
    print(f"     本: {ctx[:50] if ctx else '(完全不命中)'}")
