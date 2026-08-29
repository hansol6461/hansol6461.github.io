#!/usr/bin/env python3
"""
_data/publications.yml 를 자동으로 갱신합니다.

동작 방식
  1. OpenAlex에 ORCID로 질의해 색인된 논문을 전부 받아옵니다.
     (OpenAlex는 Crossref를 실시간으로 받아오므로 논문이 출판되면 대개 며칠 안에 잡힙니다)
  2. _data/publications_manual.yml 의 수기 목록과 합칩니다.
  3. 수기 목록의 값이 항상 우선합니다. 서지 표기를 직접 다듬어 두었거나
     OpenAlex에 없는 KCI 논문도 그대로 남습니다.
  4. 결과를 _data/publications.yml 로 씁니다.

GitHub Actions가 매주 돌리므로 직접 실행할 일은 없습니다.
로컬에서 확인하려면:  python3 scripts/sync_publications.py
"""

import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANUAL = os.path.join(ROOT, "_data", "publications_manual.yml")
OUTPUT = os.path.join(ROOT, "_data", "publications.yml")
CONFIG = os.path.join(ROOT, "_config.yml")

# 논문으로 볼 유형. preprint 나 book-chapter 를 넣고 싶으면 여기에 추가하십시오.
KEEP_TYPES = {"article", "review"}

API = "https://api.openalex.org/works"


# ── OpenAlex ────────────────────────────────────────────────────────────────

def fetch_works(orcid, mailto):
    """ORCID로 걸린 논문을 커서 방식으로 전부 받아옵니다."""
    works, cursor = [], "*"
    while cursor:
        q = urllib.parse.urlencode({
            "filter": f"author.orcid:{orcid}",
            "per-page": "200",
            "cursor": cursor,
            "mailto": mailto,          # 예의상 붙이면 요청 한도가 넉넉해집니다
        })
        req = urllib.request.Request(
            f"{API}?{q}",
            headers={"User-Agent": f"personal-site-sync ({mailto})"},
        )
        with urllib.request.urlopen(req, timeout=60) as r:
            payload = json.load(r)

        works.extend(payload.get("results", []))
        cursor = payload.get("meta", {}).get("next_cursor")
        if cursor:
            time.sleep(0.4)
    return works


# ── 서지 정보 정리 ───────────────────────────────────────────────────────────

def surname_initials(display_name):
    """'Hansol Lee' -> 'Lee, H.' 형태로 바꿉니다."""
    parts = [p for p in re.split(r"\s+", (display_name or "").strip()) if p]
    if not parts:
        return ""
    if len(parts) == 1:
        return parts[0]
    surname = parts[-1]
    initials = " ".join(p[0].upper() + "." for p in parts[:-1] if p[0].isalpha())
    return f"{surname}, {initials}".strip().rstrip(",")


def format_authors(authorships, my_orcid):
    """저자 목록을 APA 비슷하게 만들고 본인 이름을 굵게 처리합니다."""
    names = []
    for a in authorships:
        author = a.get("author") or {}
        name = surname_initials(author.get("display_name"))
        if not name:
            continue
        oid = (author.get("orcid") or "").rstrip("/").split("/")[-1]
        names.append(f"<strong>{name}</strong>" if oid == my_orcid else name)

    if not names:
        return ""
    if len(names) == 1:
        return names[0]
    return ", ".join(names[:-1]) + ", & " + names[-1]


def format_detail(biblio):
    """'30(1), 1-19' 형태의 권호쪽수 문자열을 만듭니다."""
    b = biblio or {}
    vol, issue = b.get("volume"), b.get("issue")
    first, last = b.get("first_page"), b.get("last_page")

    out = ""
    if vol:
        out += str(vol)
    if issue:
        out += f"({issue})"
    if first:
        out += (", " if out else "") + str(first)
        if last and str(last) != str(first):
            out += f"\u2013{last}"
    return out


def clean(text):
    """OpenAlex 제목에 남아 있는 태그와 엔티티를 정리합니다."""
    if not text:
        return ""
    t = re.sub(r"<[^>]+>", "", text)
    for a, b in [("&amp;", "&"), ("&lt;", "<"), ("&gt;", ">"),
                 ("&quot;", '"'), ("&#39;", "'"), ("&apos;", "'")]:
        t = t.replace(a, b)
    return re.sub(r"\s+", " ", t).strip()


def norm_doi(doi):
    if not doi:
        return ""
    return re.sub(r"^https?://(dx\.)?doi\.org/", "", doi.strip().lower())


def norm_title(title):
    return re.sub(r"[^a-z0-9]+", "", clean(title).lower())


def to_entry(work, my_orcid):
    src = ((work.get("primary_location") or {}).get("source")) or {}
    doi = work.get("doi") or ""
    return {
        "year": work.get("publication_year"),
        "date": work.get("publication_date") or "",
        "authors": format_authors(work.get("authorships") or [], my_orcid),
        "title": clean(work.get("title") or work.get("display_name")),
        "venue": clean(src.get("display_name") or ""),
        "detail": format_detail(work.get("biblio")),
        "doi": f"https://doi.org/{norm_doi(doi)}" if doi else "",
        "index": "",
    }


# ── 병합 ────────────────────────────────────────────────────────────────────

def merge(manual, fetched):
    """수기 항목이 우선. 수기에 없는 논문만 OpenAlex 쪽에서 새로 추가합니다."""
    by_doi = {norm_doi(m.get("doi")): m for m in manual if m.get("doi")}
    by_title = {norm_title(m.get("title")): m for m in manual}

    merged = [dict(m) for m in manual]
    added = []

    for f in fetched:
        key_doi = norm_doi(f["doi"])
        key_title = norm_title(f["title"])

        hit = by_doi.get(key_doi) if key_doi else None
        if hit is None:
            hit = by_title.get(key_title)

        if hit is not None:
            # 이미 있는 논문 — 수기 쪽에 비어 있는 칸만 채웁니다.
            for k in ("detail", "venue", "doi", "authors"):
                if not str(hit.get(k, "")).strip() and f.get(k):
                    hit[k] = f[k]
            if not hit.get("date") and f.get("date"):
                hit["date"] = f["date"]
            continue

        added.append(f)
        merged.append(f)

    # 날짜 내림차순. 날짜가 없으면 연도만으로 정렬합니다.
    def sort_key(e):
        d = str(e.get("date") or "")
        if len(d) == 10:
            return d
        return f"{e.get('year', 0)}-00-00"

    merged.sort(key=sort_key, reverse=True)

    # J 번호는 오래된 것부터 1번. 새 논문이 붙어도 기존 번호가 흔들리지 않습니다.
    total = len(merged)
    for i, e in enumerate(merged):
        e["id"] = f"J{total - i}"

    ordered = []
    for e in merged:
        ordered.append({
            "id": e["id"],
            "year": e.get("year"),
            "date": e.get("date", ""),
            "authors": e.get("authors", ""),
            "title": e.get("title", ""),
            "venue": e.get("venue", ""),
            "detail": e.get("detail", ""),
            "doi": e.get("doi", ""),
            "index": e.get("index", ""),
        })
    return ordered, added


# ── 실행 ────────────────────────────────────────────────────────────────────

def main():
    cfg = yaml.safe_load(open(CONFIG, encoding="utf-8"))
    orcid = str(cfg.get("orcid", "")).strip()
    mailto = str(cfg.get("email", "")).strip()

    if not orcid:
        sys.exit("_config.yml 에 orcid 가 없습니다.")

    manual = yaml.safe_load(open(MANUAL, encoding="utf-8")) or []
    print(f"수기 목록: {len(manual)}편")

    try:
        raw = fetch_works(orcid, mailto)
    except Exception as exc:                      # 네트워크가 막혀도 사이트는 살아 있어야 합니다
        print(f"OpenAlex 조회 실패 ({exc}). 수기 목록을 그대로 씁니다.")
        raw = []

    fetched = [to_entry(w, orcid) for w in raw
               if (w.get("type") in KEEP_TYPES) and w.get("title")]
    print(f"OpenAlex: {len(raw)}건 중 논문 {len(fetched)}편")

    merged, added = merge(manual, fetched)

    header = (
        "# 이 파일은 scripts/sync_publications.py 가 만듭니다. 직접 고치지 마십시오.\n"
        "# 내용을 바꾸려면 _data/publications_manual.yml 을 고치십시오.\n"
        f"# 총 {len(merged)}편\n"
    )
    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write(header)
        yaml.safe_dump(merged, f, allow_unicode=True, sort_keys=False,
                       width=10000, default_flow_style=False)

    print(f"결과: {len(merged)}편 -> _data/publications.yml")
    if added:
        print(f"새로 추가된 논문 {len(added)}편:")
        for a in added:
            print(f"  · {a['year']} {a['title'][:70]}")
    else:
        print("새로 추가된 논문 없음")


if __name__ == "__main__":
    main()
