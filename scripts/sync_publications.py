#!/usr/bin/env python3
"""
논문 목록을 만들고, OpenAlex에 새로 잡힌 것이 있으면 보고만 합니다.

중요 — 이 스크립트는 화면에 나오는 목록에 논문을 자동으로 추가하지 않습니다.

  OpenAlex는 저자를 자동으로 식별하기 때문에 동명이인의 논문이 섞여 들어옵니다.
  실제로 그런 일이 있었습니다. 그래서 다음과 같이 동작합니다.

    _data/publications_manual.yml  →  직접 관리하는 목록. 화면에 나오는 유일한 근거.
    _data/publications.yml         →  위 파일을 그대로 옮긴 것. 화면이 읽는 파일.

  OpenAlex에서 받아온 것 중 수기 목록에 없는 논문은 보고만 합니다.
  Actions 실행 요약에 표로 뜨고, 확인한 뒤 본인 논문이 맞으면
  publications_manual.yml 에 직접 넣으면 됩니다.

로컬 확인:  python3 scripts/sync_publications.py
"""

import json
import os
import re
import time
import urllib.parse
import urllib.request

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANUAL = os.path.join(ROOT, "_data", "publications_manual.yml")
OUTPUT = os.path.join(ROOT, "_data", "publications.yml")
CONFIG = os.path.join(ROOT, "_config.yml")

KEEP_TYPES = {"article", "review"}
API = "https://api.openalex.org/works"


def fetch_works(orcid, mailto):
    works, cursor = [], "*"
    while cursor:
        q = urllib.parse.urlencode({
            "filter": f"author.orcid:{orcid}",
            "per-page": "200",
            "cursor": cursor,
            "mailto": mailto,
        })
        req = urllib.request.Request(
            f"{API}?{q}", headers={"User-Agent": f"personal-site-check ({mailto})"})
        with urllib.request.urlopen(req, timeout=60) as r:
            payload = json.load(r)
        works.extend(payload.get("results", []))
        cursor = payload.get("meta", {}).get("next_cursor")
        if cursor:
            time.sleep(0.4)
    return works


def clean(text):
    if not text:
        return ""
    t = re.sub(r"<[^>]+>", "", str(text))
    for a, b in [("&amp;", "&"), ("&lt;", "<"), ("&gt;", ">"),
                 ("&quot;", '"'), ("&#39;", "'"), ("&apos;", "'")]:
        t = t.replace(a, b)
    return re.sub(r"\s+", " ", t).strip()


def norm_doi(doi):
    if not doi:
        return ""
    return re.sub(r"^https?://(dx\.)?doi\.org/", "", str(doi).strip().lower())


def norm_title(title):
    return re.sub(r"[^a-z0-9]+", "", clean(title).lower())


def summarize(work):
    src = ((work.get("primary_location") or {}).get("source")) or {}
    authors = [((a.get("author") or {}).get("display_name") or "")
               for a in (work.get("authorships") or [])]
    return {
        "year": work.get("publication_year"),
        "title": clean(work.get("title") or work.get("display_name")),
        "venue": clean(src.get("display_name") or ""),
        "doi": norm_doi(work.get("doi")),
        "authors": ", ".join(a for a in authors if a)[:120],
    }


def main():
    cfg = yaml.safe_load(open(CONFIG, encoding="utf-8"))
    orcid = str(cfg.get("orcid", "")).strip()
    mailto = str(cfg.get("email", "")).strip()
    manual = yaml.safe_load(open(MANUAL, encoding="utf-8")) or []

    # 1. 표시용 파일 생성. 수기 목록이 전부입니다.
    def sort_key(e):
        d = str(e.get("date") or "")
        return d if len(d) == 10 else "%s-00-00" % e.get("year", 0)

    ordered = sorted(manual, key=sort_key, reverse=True)
    n = len(ordered)
    out = []
    for i, e in enumerate(ordered):
        out.append({
            "id": "J%d" % (n - i),
            "year": e.get("year"),
            "date": e.get("date", ""),
            "authors": e.get("authors", ""),
            "title": e.get("title", ""),
            "venue": e.get("venue", ""),
            "detail": e.get("detail", ""),
            "doi": e.get("doi", ""),
            "index": e.get("index", ""),
        })

    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write("# 이 파일은 scripts/sync_publications.py 가 만듭니다. 직접 고치지 마십시오.\n"
                "# 내용을 바꾸려면 _data/publications_manual.yml 을 고치십시오.\n"
                "# 총 %d편\n" % n)
        yaml.safe_dump(out, f, allow_unicode=True, sort_keys=False,
                       width=10000, default_flow_style=False)
    print("화면 표시용 목록: %d편 (수기 목록 그대로)" % n)

    # 2. OpenAlex 대조. 보고만 하고 추가하지 않습니다.
    if not orcid:
        return
    try:
        raw = fetch_works(orcid, mailto)
    except Exception as exc:
        print("OpenAlex 조회 실패 (%s). 표시용 목록에는 영향 없음." % exc)
        return

    have_doi = set(norm_doi(e.get("doi")) for e in manual if e.get("doi"))
    have_title = set(norm_title(e.get("title")) for e in manual)

    unknown = []
    for w in raw:
        if w.get("type") not in KEEP_TYPES or not w.get("title"):
            continue
        s = summarize(w)
        if (s["doi"] and s["doi"] in have_doi) or norm_title(s["title"]) in have_title:
            continue
        unknown.append(s)

    unknown.sort(key=lambda s: (s["year"] or 0), reverse=True)
    print("OpenAlex 조회: %d건, 수기 목록에 없는 항목 %d건" % (len(raw), len(unknown)))
    if not unknown:
        return

    lines = [
        "### OpenAlex에 잡혔지만 목록에 없는 논문",
        "",
        "동명이인의 논문이 섞여 있을 수 있습니다. **확인 없이 추가하지 마십시오.**",
        "본인 논문이 맞으면 `_data/publications_manual.yml` 에 직접 넣으면 됩니다.",
        "",
        "| 연도 | 제목 | 학술지 | 저자 | DOI |",
        "|---|---|---|---|---|",
    ]
    for s in unknown:
        doi = "[%s](https://doi.org/%s)" % (s["doi"], s["doi"]) if s["doi"] else ""
        lines.append("| %s | %s | %s | %s | %s |" % (
            s["year"] or "", s["title"][:90], s["venue"][:40], s["authors"][:60], doi))

    report = "\n".join(lines)
    print()
    print(report)

    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as f:
            f.write(report + "\n")


if __name__ == "__main__":
    main()
