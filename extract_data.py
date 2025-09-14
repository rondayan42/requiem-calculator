#!/usr/bin/env python3
import argparse
import json
import os
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional


GROUP_FROM_BG = {
    # background-image: url(/template/images/clas/<key>.png)
    "Defender": "Turian",
    "Templar": "Turian",
    "Warrior": "Bartuk",
    "Shaman": "Bartuk",
    "Rogue": "Kruxena",
    "SoulHunter": "Kruxena",
    "Hunter": "Xenoa",
    "BattleMagician": "Xenoa",
}


def _space_from_camel(name: str) -> str:
    return re.sub(r"(?<!^)([A-Z])", r" \1", name).strip()


def _clean_skill_filename(filename: str) -> str:
    # Examples: 'Fire Ball_G.png', 'DNA_FireBall_G.png', 'Loa Summon_G.png'
    base = filename.rsplit("/", 1)[-1]
    base = base.rsplit(".", 1)[0]
    base = base.replace("_G", "")
    # Drop leading DNA_
    if base.startswith("DNA_"):
        base = base[4:]
    # Replace underscores with spaces
    base = base.replace("_", " ")
    return base.strip()


def find_latest_calculator_index(snapshots_root: Path) -> Optional[Path]:
    candidates = list(snapshots_root.glob("requiem.isnet.ru/**/calculator.html"))
    if not candidates:
        return None
    # Sort by timestamp folder numerically if present
    def ts_key(p: Path) -> Tuple[int, str]:
        try:
            return (int(p.parent.name), str(p))
        except Exception:
            return (0, str(p))

    candidates.sort(key=ts_key, reverse=True)
    return candidates[0]


def parse_groups_and_subclasses(index_html: str) -> Tuple[Dict[str, str], Dict[str, List[Dict[str, object]]]]:
    """
    Returns tuple:
    - groups: group_id -> group_name (race)
    - jobs_by_group: group_id -> list of first-job dicts:
        { "id": <first_job_id>, "name": <first_job_name>, "specs": [ {"id": <spec_id>, "name": <spec_name>} ] }
    """
    groups: Dict[str, str] = {}
    jobs_by_group: Dict[str, List[Dict[str, object]]] = {}

    group_re = re.compile(
        r"<div class='calculator_select_job'[^>]*?background-image:\s*url\(/template/images/clas/([^/)]+)\.png\);'\s+clas='(\d+)'\s*>",
        re.IGNORECASE,
    )

    subclass_re = re.compile(
        r"<a[^>]+href='[^']*/calculator/(\d+)\.html'[^>]*>\s*<img[^>]+src='/template/images/clas/[^/]+_([A-Za-z]+)\.png'",
        re.IGNORECASE,
    )

    pos = 0
    while True:
        m = group_re.search(index_html, pos)
        if not m:
            break
        bg_key = m.group(1)
        first_job_id = m.group(2)
        race_name = GROUP_FROM_BG.get(bg_key, _space_from_camel(bg_key))
        race_id = race_name.lower().replace(" ", "-")
        first_job_name = _space_from_camel(bg_key)
        groups[race_id] = race_name

        # find block end
        start = m.end()
        next_m = group_re.search(index_html, start)
        end = next_m.start() if next_m else index_html.find("</div></div></div>", start)
        if end == -1:
            end = len(index_html)
        block = index_html[start:end]

        specs: List[Dict[str, object]] = []
        for sm in subclass_re.finditer(block):
            spec_id = sm.group(1)
            raw_name = sm.group(2)
            spec_name = _space_from_camel(raw_name)
            specs.append({"id": spec_id, "name": spec_name})

        jobs_by_group.setdefault(race_id, []).append({
            "id": first_job_id,
            "name": first_job_name,
            "specs": specs,
        })
        pos = end

    return groups, jobs_by_group


def find_latest_subclass_page(snapshots_root: Path, subclass_id: str) -> Optional[Path]:
    candidates = list(snapshots_root.glob(f"requiem.isnet.ru/**/calculator/{subclass_id}.html"))
    if not candidates:
        return None
    def ts_key(p: Path) -> Tuple[int, str]:
        try:
            return (int(p.parents[1].name), str(p))
        except Exception:
            return (0, str(p))
    candidates.sort(key=ts_key, reverse=True)
    return candidates[0]


def parse_skills_and_dna_from_subclass(html: str) -> Tuple[List[Dict[str, object]], List[Dict[str, object]]]:
    skills: List[Dict[str, object]] = []
    dna: List[Dict[str, object]] = []
    # <img class='skill' type='0' id='25100' src='/template/images/skills/Fire Ball_G.png' ... />
    img_re = re.compile(r"<img[^>]+class='skill'[^>]+type='(\d+)'[^>]+id='(\d+)'[^>]+src='([^']+)'", re.IGNORECASE)
    seen_skill = set()
    seen_dna = set()
    for m in img_re.finditer(html):
        type_code = m.group(1)
        sid = m.group(2)
        src = m.group(3)
        name = _clean_skill_filename(src)
        if type_code == '0':
            if sid in seen_skill:
                continue
            seen_skill.add(sid)
            skills.append({"id": sid, "name": name, "maxLevel": 10})
        elif type_code == '1':
            if sid in seen_dna:
                continue
            seen_dna.add(sid)
            dna.append({"id": sid, "name": name, "maxLevel": 10})
    return skills, dna


def build_data(snapshots_root: Path) -> Dict[str, object]:
    index_path = find_latest_calculator_index(snapshots_root)
    if not index_path:
        raise SystemExit("calculator.html not found in snapshots")
    index_html = index_path.read_text(encoding='utf-8', errors='ignore')
    groups, jobs_by_group = parse_groups_and_subclasses(index_html)

    skills_map: Dict[str, List[Dict[str, object]]] = {}
    dna_map: Dict[str, List[Dict[str, object]]] = {}
    for race_id, jobs in jobs_by_group.items():
        for job in jobs:
            for spec in job.get("specs", []):
                subclass_id = str(spec["id"])  # ensure string
                page_path = find_latest_subclass_page(snapshots_root, subclass_id)
                if not page_path:
                    continue
                html = page_path.read_text(encoding='utf-8', errors='ignore')
                skills, dna = parse_skills_and_dna_from_subclass(html)
                skills_map[subclass_id] = skills
                dna_map[subclass_id] = dna

    out = {
        "groups": [{"id": gid, "name": gname} for gid, gname in groups.items()],
        "jobs": jobs_by_group,
        "skills": skills_map,
        "dna": dna_map,
    }
    return out


def main():
    ap = argparse.ArgumentParser(description="Extract Requiem calculator data from snapshots into english-calculator/data.json")
    ap.add_argument("snapshots_root", help="Path to waybackup_snapshots directory")
    ap.add_argument("output_json", help="Path to write data.json")
    args = ap.parse_args()

    snapshots_root = Path(args.snapshots_root).resolve()
    out_path = Path(args.output_json).resolve()

    data = build_data(snapshots_root)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()


