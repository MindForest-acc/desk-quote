"""补充见证本：孙子第二底本（曹操注《孫子略解》）+ 王阳明非《传习录》诸篇。"""
from __future__ import annotations
import json
from pathlib import Path
import importlib.util, sys
spec = importlib.util.spec_from_file_location("fs", Path(__file__).parent / "fetch_sources.py")

# 复用 fetch_sources 的工具函数，但不重跑它的抓取流程
src = (Path(__file__).parent / "fetch_sources.py").read_text(encoding="utf-8")
ns: dict = {"__file__": str(Path(__file__).resolve())}
exec(src.split("PLAN = {")[0], ns)          # 只执行工具函数定义部分
api, subpages, wikitext = ns["api"], ns["subpages"], ns["wikitext"]
split_sections, norm = ns["split_sections"], ns["norm"]
from zhconv import convert

OUT = Path(__file__).parent / "sources"
index = json.loads((OUT / "index.json").read_text(encoding="utf-8"))

# --- 见证本 B：曹操注《孫子略解》---
raw = wikitext(["孫子略解"])["孫子略解"]
secs = split_sections(raw)
index["sunzi_b"] = {k: norm(v) for k, v in secs.items() if norm(v)}
print(f"sunzi_b 篇目 {len(index['sunzi_b'])}，{sum(len(v) for v in index['sunzi_b'].values())} 字")

# --- 王阳明集（含教条示龙场诸生、泛海、咏良知、年谱等）---
titles = subpages("王陽明集") + ["教條示龍場諸生", "泛海"]
print(f"王陽明集 子页 {len(titles)} 个")
ym: dict[str, str] = {}
for title, raw in wikitext(titles).items():
    leaf = convert(title.split("/", 1)[1] if "/" in title else title, "zh-cn")
    for k, v in split_sections(raw).items():
        key = leaf if k == "__all__" else f"{leaf}/{k}"
        if norm(v):
            ym[key] = norm(v)
index["yangming_b"] = ym
print(f"yangming_b 篇目 {len(ym)}，{sum(len(v) for v in ym.values())} 字")

(OUT / "index.json").write_text(json.dumps(index, ensure_ascii=False), encoding="utf-8")
print("已并入 index.json；现有 book:", list(index))
