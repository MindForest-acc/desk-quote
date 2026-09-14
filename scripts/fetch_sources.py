"""从 zh.wikisource 拉取公有领域原文，转简体，切分到篇，落盘为可检索索引。"""
from __future__ import annotations
import json, re, sys, time, urllib.parse, urllib.request
from pathlib import Path
from zhconv import convert

API = "https://zh.wikisource.org/w/api.php"
UA = "DeskQuote-corpus-verify/1.0 (personal desktop widget; contact: local)"
OUT = Path(__file__).parent / "sources"
OUT.mkdir(exist_ok=True)


def api(**params: str) -> dict:
    params.setdefault("format", "json")
    params.setdefault("formatversion", "2")
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read().decode())
        except Exception as exc:  # noqa: BLE001 - 网络重试
            if attempt == 3:
                raise
            print(f"  retry {attempt+1}: {exc}", file=sys.stderr)
            time.sleep(2 * (attempt + 1))
    raise RuntimeError("unreachable")


def subpages(prefix: str) -> list[str]:
    d = api(action="query", list="allpages", apprefix=prefix + "/", aplimit="500")
    return [p["title"] for p in d["query"]["allpages"]]


def wikitext(titles: list[str]) -> dict[str, str]:
    out: dict[str, str] = {}
    for i in range(0, len(titles), 40):
        chunk = titles[i : i + 40]
        d = api(action="query", prop="revisions", rvprop="content",
                rvslots="main", titles="|".join(chunk))
        for page in d["query"]["pages"]:
            if "revisions" not in page:
                continue
            out[page["title"]] = page["revisions"][0]["slots"]["main"]["content"]
        time.sleep(0.4)
    return out


TEMPLATE = re.compile(r"\{\{[^{}]*\}\}")
NOISE = re.compile(
    r"<ref[^>]*>.*?</ref>|<ref[^>]*/>|<!--.*?-->|<[^>]+>", re.S)


def strip_markup(w: str) -> str:
    w = NOISE.sub("", w)
    for _ in range(6):                       # 模板可嵌套
        w2 = TEMPLATE.sub("", w)
        if w2 == w:
            break
        w = w2
    w = re.sub(r"\[\[([^\]|]*\|)?([^\]]*)\]\]", r"\2", w)   # 内链取显示文本
    w = re.sub(r"'{2,}", "", w)
    return w


HEADING = re.compile(r"^\s*={2,}\s*(.+?)\s*={2,}\s*$", re.M)
PUNCT = re.compile(r"[^一-鿿]")


def norm(s: str) -> str:
    """归一化：转简体 + 剥掉所有非汉字。标点差异不应该影响原文比对。"""
    return PUNCT.sub("", convert(s, "zh-cn"))


def split_sections(raw: str) -> dict[str, str]:
    """按 == 标题 == 切篇。无标题则整篇归到 __all__。"""
    body = strip_markup(raw)
    marks = list(HEADING.finditer(body))
    if not marks:
        return {"__all__": body}
    out: dict[str, str] = {}
    for i, m in enumerate(marks):
        end = marks[i + 1].start() if i + 1 < len(marks) else len(body)
        out[convert(m.group(1), "zh-cn")] = body[m.end():end]
    return out


PLAN = {
    "sunzi":    {"root": "孫子兵法", "mode": "single"},
    "zhuangzi": {"root": "莊子",     "mode": "subpages"},
    "mozi":     {"root": "墨子",     "mode": "subpages"},
    "yangming": {"root": "傳習錄",   "mode": "subpages"},
}

index: dict[str, dict[str, str]] = {}
for book, spec in PLAN.items():
    print(f"[{book}] {spec['root']} …")
    sections: dict[str, str] = {}
    if spec["mode"] == "single":
        raw = wikitext([spec["root"]])[spec["root"]]
        sections = split_sections(raw)
    else:
        titles = subpages(spec["root"])
        print(f"  子页 {len(titles)} 个")
        for title, raw in wikitext(titles).items():
            leaf = convert(title.split("/", 1)[1], "zh-cn")
            sub = split_sections(raw)
            if set(sub) == {"__all__"}:
                sections[leaf] = sub["__all__"]
            else:
                for k, v in sub.items():
                    sections[f"{leaf}/{k}"] = v
    index[book] = {k: norm(v) for k, v in sections.items() if norm(v)}
    total = sum(len(v) for v in index[book].values())
    print(f"  篇目 {len(index[book])} 个，正文 {total} 字")

(OUT / "index.json").write_text(json.dumps(index, ensure_ascii=False), encoding="utf-8")
print(f"\n写入 {OUT/'index.json'}")
