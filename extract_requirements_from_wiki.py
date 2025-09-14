#!/usr/bin/env python3
import json
import re
from pathlib import Path
from html import unescape


WIKI_DIR = Path(__file__).resolve().parent / 'wiki_cache'
DATA_JSON = Path(__file__).resolve().parent / 'data.json'


def normalize_name(name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", name.lower())


def extract_prereq_levels(html: str):
    # Try to capture the row titled "Prerequisite Level" and collect its numeric cells
    m = re.search(r"<th[^>]*>\s*Prerequisite Level\s*</th>\s*<td[^>]*>(.*?)</td>(.*?)</tr>", html, re.I | re.S)
    if not m:
        return None
    row = m.group(0)
    vals = re.findall(r">\s*(\d+)\s*<", row)
    if not vals:
        return None
    return [int(v) for v in vals]


def build_wiki_index():
    idx = {}
    for p in WIKI_DIR.glob('site_pages_*.html.html'):
        try:
            html = p.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            continue
        # Extract the page title inside <h1 class="page-title">Name</h1>
        t = re.search(r"<h1[^>]*class=\"page-title\"[^>]*>\s*([^<]+)\s*</h1>", html)
        title = unescape(t.group(1).strip()) if t else p.stem
        idx[normalize_name(title)] = (p, html, title)
    return idx


def main():
    data = json.loads(DATA_JSON.read_text(encoding='utf-8'))
    wiki_idx = build_wiki_index()
    updated = 0

    # Work only on skills; DNA typically doesn't have level prereq arrays in 2009 pages
    for spec_id, skills in (data.get('skills') or {}).items():
        for s in skills:
            key = normalize_name(s.get('name', ''))
            if not key:
                continue
            page = wiki_idx.get(key)
            if not page:
                continue
            _, html, _ = page
            lvl_req = extract_prereq_levels(html)
            if lvl_req:
                if s.get('lvlReq') != lvl_req:
                    s['lvlReq'] = lvl_req
                    updated += 1

    if updated:
        DATA_JSON.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
        print(f"Updated lvlReq for {updated} skills in data.json")
    else:
        print("No lvlReq rows found or matched. No changes.")


if __name__ == '__main__':
    main()


