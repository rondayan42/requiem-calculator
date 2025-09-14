#!/usr/bin/env python3
import json
import re
from pathlib import Path
from html import unescape
from bs4 import BeautifulSoup, Tag


WIKI_DIR = Path(__file__).resolve().parent / 'wiki_cache'
DATA_JSON = Path(__file__).resolve().parent / 'data.json'


def normalize_name(name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", name.lower())


def parse_prereqs_table(soup: BeautifulSoup):
    """Extracts data from the main red 'Prerequisites' table."""
    reqs = {}
    prereqs_header = soup.find(lambda tag: tag.name == 'b' and 'Prerequisites' in tag.get_text(strip=True))
    if not prereqs_header:
        return None

    table = prereqs_header.find_parent('table')
    if not table:
        return None

    rows = table.find_all('tr')
    for row in rows:
        cells = row.find_all('td')
        if len(cells) < 2:
            continue

        key = cells[0].get_text(strip=True).replace(':', '').lower()
        value_text = cells[1].get_text(strip=True)

        if 'job' in key or 'skill' in key:
            # e.g., "Warrior, Level 32, Skill Mastery 22"
            # e.g., "Holy Bolt, Level 5"
            parts = [p.strip() for p in value_text.split(',')]
            job_req = {}
            for part in parts:
                if 'level' in part.lower():
                    lvl_match = re.search(r'(\d+)', part)
                    if lvl_match:
                        job_req['level'] = int(lvl_match.group(1))
                else: # Assumed to be a name (job or skill)
                    job_req['name'] = part
            if job_req:
                reqs[key] = job_req

    return reqs if reqs else None


def parse_level_needed_row(soup: BeautifulSoup):
    """Extracts the 'Level needed' array from the main skill progression table."""
    level_needed_header = soup.find(lambda tag: tag.name in ('th', 'td') and 'Level needed' in tag.get_text(strip=True))
    if not level_needed_header:
        return None

    row = level_needed_header.find_parent('tr')
    if not row:
        return None

    cells = row.find_all('td')
    if not cells: # Header might be the first cell
        # This is a bit brittle, assumes header is first `th`
        cells = row.find_all('th')[1:] if len(row.find_all('th')) > 1 else []


    levels = []
    # Fill in sparse "Level needed" rows (like Reckless Attack)
    last_level = None
    for cell in cells:
        val = cell.get_text(strip=True)
        if val.isdigit():
            last_level = int(val)
            levels.append(last_level)
        else:
            levels.append(last_level) # repeat last known level for empty cells
            
    # Heuristic to fill out to 5 levels if sparse
    if levels and len(levels) < 5:
        last_val = levels[-1]
        while len(levels) < 5:
            levels.append(last_val)

    return levels if levels else None


def build_wiki_index():
    """Builds an index of normalized skill/job names to their file paths and parsed soup."""
    idx = {}
    for p in WIKI_DIR.glob('site_pages_*.html.html'):
        try:
            html = p.read_text(encoding='utf-8', errors='ignore')
            soup = BeautifulSoup(html, 'html.parser')
            title_tag = soup.find('h1', class_='page-title')
            title = unescape(title_tag.get_text(strip=True)) if title_tag else p.stem
            idx[normalize_name(title)] = (p, soup, title)
        except Exception as e:
            # print(f"Error processing {p.name}: {e}")
            continue
    return idx


def main():
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        print("Error: `beautifulsoup4` is not installed. Please run `pip install beautifulsoup4`")
        return

    data = json.loads(DATA_JSON.read_text(encoding='utf-8'))
    wiki_idx = build_wiki_index()
    updated_count = 0
    skills_with_reqs = 0

    name_to_id_map = {}
    for spec_id, skills in (data.get('skills') or {}).items():
        for s in skills:
            name_to_id_map[normalize_name(s.get('name', ''))] = s.get('id')

    for spec_id, skills in (data.get('skills') or {}).items():
        for s in skills:
            key = normalize_name(s.get('name', ''))
            if not key or key not in wiki_idx:
                continue

            _, soup, _ = wiki_idx[key]
            
            # Use a flag to track if we added/changed something on this skill
            skill_updated = False

            # Extract detailed prerequisites
            prereqs = parse_prereqs_table(soup)
            if prereqs:
                # Convert prerequisite names to IDs where possible
                for req_key, req_val in prereqs.items():
                    if 'name' in req_val:
                        req_name_norm = normalize_name(req_val['name'])
                        if req_name_norm in name_to_id_map:
                            req_val['id'] = name_to_id_map[req_name_norm]
                
                if s.get('requires') != prereqs:
                    s['requires'] = prereqs
                    skill_updated = True

            # Extract per-rank level requirements
            lvl_req = parse_level_needed_row(soup)
            if lvl_req:
                if s.get('lvlReq') != lvl_req:
                    s['lvlReq'] = lvl_req
                    skill_updated = True

            if skill_updated:
                updated_count += 1
            
            if s.get('requires') or s.get('lvlReq'):
                skills_with_reqs += 1


    if updated_count > 0:
        DATA_JSON.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
        print(f"Enriched/updated {updated_count} skills with detailed requirements. Total skills with any reqs: {skills_with_reqs}")
    else:
        print("No new requirements found in the wiki cache. data.json is unchanged.")


if __name__ == '__main__':
    main()
