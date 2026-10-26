#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""laws-query —— query the ee-gcc 3.2 handbook by symptom, pass or id.

The handbook is written for the moment when a matching diff is wrong and the question is "which
decision produced this?". This tool is the entry point for a person or an agent: give it a symptom,
a pass, or a law id, and it prints the law, its anchors, its receipt and its levers.

It reads `docs/knowledge-base/compiler/laws.json` and never touches the game or the compiler.

Usage
-----
```sh
python3 tools/compiler/laws-query.py list
python3 tools/compiler/laws-query.py find frame            # symptom / lever / title / pass
python3 tools/compiler/laws-query.py law L-EE-001
python3 tools/compiler/laws-query.py pass 23.greg
python3 tools/compiler/laws-query.py symptoms
python3 tools/compiler/laws-query.py guide frame        # levers in FIELD-GUIDE.md
python3 tools/compiler/laws-query.py --json find allocation
```

Exit codes: 0 = at least one hit, 1 = no hit, 2 = usage / data error.

用法（中文摘要）：按「症状 / pass / 条目号」查询手册。匹配范围是标题、症状、杠杆与 pass 名。
输出含分级（T1/T2/T3）、源码锚点、二进制锚点、receipt 与 scope。不读游戏内容，不调用编译器。
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LAWS_JSON = ROOT / "docs" / "knowledge-base" / "compiler" / "laws.json"


def load() -> dict:
    if not LAWS_JSON.is_file():
        print(f"error: {LAWS_JSON} not found", file=sys.stderr)
        sys.exit(2)
    try:
        return json.loads(LAWS_JSON.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"error: {LAWS_JSON} is not valid JSON: {exc}", file=sys.stderr)
        sys.exit(2)


def haystack(law: dict) -> str:
    parts = [law.get("title", ""), law.get("receipt", ""), law.get("scope", "")]
    parts += law.get("symptom", []) + law.get("lever", []) + law.get("pass", [])
    return " ".join(parts).lower()


def searchable(laws: list[dict], text: str) -> list[dict]:
    needle = text.lower()
    return [law for law in laws if needle in haystack(law)]


def render(law: dict) -> str:
    out = [f"{law['id']}  [{law.get('tier', '?')}]  {law.get('title', '')}"]
    src = law.get("source_anchor") or {}
    bin_ = law.get("binary_anchor") or {}
    if src.get("file"):
        note = f"  ({src.get('note')})" if src.get("note") else ""
        out.append(f"  source anchor : {src['file']}:{src.get('line', 0)}{note}")
    if bin_.get("symbol"):
        out.append(f"  binary anchor : {bin_['symbol']} @ {bin_.get('addr', '?')}")
    for const in bin_.get("constants", []) or []:
        out.append(f"                  {const.get('kind')} {const.get('value')} @ {const.get('at')}"
                   f"  -- {const.get('means', '')}")
    struct = bin_.get("struct") or {}
    if struct.get("name"):
        out.append(f"                  struct {struct['name']} byte_size={struct.get('byte_size')}")
    if law.get("pass"):
        out.append(f"  pass          : {', '.join(law['pass'])}")
    for key in ("symptom", "lever"):
        for item in law.get(key, []) or []:
            out.append(f"  {key:<13} : {item}")
    if law.get("receipt"):
        out.append(f"  receipt       : {law['receipt']}")
    if law.get("falsifies"):
        out.append(f"  falsifies     : {law['falsifies']}")
    if law.get("scope"):
        out.append(f"  scope         : {law['scope']}")
    return "\n".join(out)


def load_guide_sections() -> list[tuple[str, str]]:
    """Split FIELD-GUIDE.md into `(heading, section text)` pairs."""
    path = ROOT / "docs" / "knowledge-base" / "compiler" / "FIELD-GUIDE.md"
    if not path.is_file():
        return []
    sections: list[tuple[str, str]] = []
    heading, body = "", []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            if heading:
                sections.append((heading, "\n".join(body).strip()))
            heading, body = line[3:].strip(), []
        elif heading:
            body.append(line)
    if heading:
        sections.append((heading, "\n".join(body).strip()))
    return sections


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="laws-query",
        description="Query the ee-gcc 3.2 compiler handbook (docs/knowledge-base/compiler/laws.json).",
    )
    ap.add_argument("--json", action="store_true", help="print JSON instead of prose")
    ap.add_argument("command", choices=["list", "find", "law", "pass", "symptoms", "levers", "guide"])
    ap.add_argument("query", nargs="*", help="for `find` / `guide`: one or more search terms")
    args = ap.parse_args(argv)

    if args.command == "guide":
        if not args.query:
            ap.error("guide needs at least one term, for example: guide frame")
        sections = load_guide_sections()
        hits = [(h, b) for h, b in sections
                if any(term.lower() in (h + "\n" + b).lower() for term in args.query)]
        if args.json:
            print(json.dumps([{"heading": h, "body": b} for h, b in hits], ensure_ascii=False, indent=1))
            return 0 if hits else 1
        if not hits:
            print("no field-guide section matches. Run `list` for the laws, or read FIELD-GUIDE.md.")
            return 1
        for heading, body in hits:
            print(f"## {heading}\n{body}\n")
        return 0

    data = load()
    laws = data.get("laws") or []

    if args.command == "list":
        if args.json:
            print(json.dumps([{"id": law["id"], "tier": law.get("tier"), "title": law.get("title")}
                              for law in laws], ensure_ascii=False, indent=1))
            return 0 if laws else 1
        for law in laws:
            print(f"{law['id']}  [{law.get('tier', '?')}]  {law.get('title', '')}")
        return 0 if laws else 1

    if args.command == "symptoms":
        seen: list[str] = []
        for law in laws:
            for item in law.get("symptom", []) or []:
                if item not in seen:
                    seen.append(item)
        if args.json:
            print(json.dumps(seen, ensure_ascii=False, indent=1))
            return 0 if seen else 1
        for item in seen:
            print(f"- {item}")
        return 0 if seen else 1

    if args.command == "levers":
        rows = [{"id": law["id"], "lever": item}
                for law in laws for item in (law.get("lever", []) or [])]
        if args.json:
            print(json.dumps(rows, ensure_ascii=False, indent=1))
            return 0
        for row in rows:
            print(f"{row['id']}  {row['lever']}")
        return 0

    if args.command == "law":
        if not args.query:
            ap.error("law needs an id, for example: law L-EE-001")
        wanted = args.query[0].upper()
        hits = [law for law in laws if law.get("id", "").upper() == wanted]
        if not hits:
            hits = [law for law in laws if wanted in law.get("id", "").upper()]
    elif args.command == "pass":
        if not args.query:
            ap.error("pass needs a dump name, for example: pass 23.greg")
        needle = args.query[0].lower()
        hits = [law for law in laws if any(needle in p.lower() for p in law.get("pass", []) or [])]
    else:  # find
        if not args.query:
            ap.error("find needs at least one term")
        hits = laws
        for term in args.query:
            hits = searchable(hits, term)

    if args.json:
        print(json.dumps(hits, ensure_ascii=False, indent=1))
        return 0 if hits else 1

    if not hits:
        print("no law matches. Try `symptoms` to see the recorded symptoms, or `list`.")
        return 1
    print("\n\n".join(render(law) for law in hits))
    if len(hits) > 1:
        print(f"\n({len(hits)} laws matched)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
