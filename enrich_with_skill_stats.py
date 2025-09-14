#!/usr/bin/env python3
import json
import re
from pathlib import Path
from html import unescape
from bs4 import BeautifulSoup

WIKI_DIR = Path(__file__).resolve().parent / 'wiki_cache'
DATA_JSON = Path(__file__).resolve().parent / 'data.json'

def normalize_name(name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", name.lower())

def parse_skill_info_table(soup: BeautifulSoup):
    """Extracts basic info from the top skill info table."""
    info = {}
    info_table = soup.find('table', class_='skill info')
    if not info_table:
        return None

    rows = info_table.find_all('tr')
    for row in rows:
        cells = row.find_all('td')
        if len(cells) < 2:
            continue

        key = cells[0].get_text(strip=True).replace(':', '').replace('<b>', '').replace('</b>', '').strip().lower()
        value = cells[1].get_text(strip=True).strip()

        if key == 'type':
            info['type'] = value
        elif key == 'levels':
            info['levels'] = int(value) if value.isdigit() else None
        elif key == 'casting time':
            info['cast_time'] = value
        elif key == 'skill downtime':
            info['cooldown'] = value
        elif key == 'compatible weapon':
            info['weapons'] = [w.strip() for w in value.split(',')]
        elif key == 'range':
            info['range'] = value
        elif key == 'target':
            info['target'] = value
        # Skip prerequisites as we have a separate parser

    return info if info else None

def parse_progression_table(soup: BeautifulSoup):
    """Extracts per-level stats from the main progression table."""
    prog_table = soup.find('table', class_='wikitable')
    if not prog_table:
        return None

    headers = [th.get_text(strip=True).lower() for th in prog_table.find_all('th')]
    rows = prog_table.find_all('tr')[1:]  # Skip header

    # Assume first column is "Level", then stats
    if not headers or headers[0] != 'level':
        return None

    stats = {h: [] for h in headers[1:]}
    for row in rows:
        cells = row.find_all('td')
        if len(cells) != len(headers):
            continue
        for i, h in enumerate(headers[1:], 1):
            val = cells[i].get_text(strip=True).strip()
            if val.replace('+', '').isdigit():
                stats[h].append(int(val.replace('+', '')))
            else:
                stats[h].append(val)

    return stats

def build_wiki_index():
    idx = {}
    for p in WIKI_DIR.glob('site_pages_*.html.html'):
        try:
            html = p.read_text(encoding='utf-8', errors='ignore')
            soup = BeautifulSoup(html, 'html.parser')
            title_tag = soup.find('h1', class_='page-title')
            title = unescape(title_tag.get_text(strip=True)) if title_tag else p.stem
            idx[normalize_name(title)] = (p, soup, title)
        except Exception:
            continue
    return idx

def main():
    data = json.loads(DATA_JSON.read_text(encoding='utf-8'))
    wiki_idx = build_wiki_index()
    updated_count = 0

    for spec_id, skills in (data.get('skills') or {}).items():
        for s in skills:
            key = normalize_name(s.get('name', ''))
            if not key or key not in wiki_idx:
                continue

            _, soup, _ = wiki_idx[key]
            
            skill_updated = False

            # Parse basic info
            info = parse_skill_info_table(soup)
            if info and s.get('info') != info:
                s['info'] = info
                skill_updated = True

            # Parse progression stats
            prog = parse_progression_table(soup)
            if prog and s.get('progression') != prog:
                s['progression'] = prog
                skill_updated = True

            if skill_updated:
                updated_count += 1

    if updated_count > 0:
        DATA_JSON.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
        print(f"Enriched {updated_count} skills with detailed stats from wiki.")
    else:
        print("No new stats found. data.json unchanged.")

if __name__ == '__main__':
    main()
