#!/usr/bin/env python3
import csv
import os
from pathlib import Path
from urllib.request import urlopen


WAYBACK = "https://web.archive.org/web/{ts}id_/http://requiem.isnet.ru/template/js/{name}"
NAMES = [
    "tooltip.js",
    "calculator.js",
    "functions.js",
    "character.js",
    "buns.js",
]


def iter_timestamps(csv_path: Path):
    seen = set()
    with csv_path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            ts = (row.get("timestamp") or "").strip()
            if ts and ts.isdigit() and ts not in seen:
                seen.add(ts)
                yield ts


def fetch_all(csv_path: Path, out_dir: Path, max_ts: int = 50):
    out_dir.mkdir(parents=True, exist_ok=True)
    count = 0
    for ts in iter_timestamps(csv_path):
        for name in NAMES:
            url = WAYBACK.format(ts=ts, name=name)
            out = out_dir / f"{name.replace('.js','')}-{ts}.js"
            if out.exists():
                continue
            try:
                with urlopen(url, timeout=20) as r, out.open("wb") as w:
                    w.write(r.read())
            except Exception:
                # ignore failures; try other timestamps
                pass
        count += 1
        if count >= max_ts:
            break


def main():
    root = Path(__file__).resolve().parent.parent / "waybackup_snapshots"
    csv_path = root / "waybackup_http.requiem.isnet.ru.csv"
    out_dir = Path(__file__).resolve().parent / "sources"
    fetch_all(csv_path, out_dir)
    print("Fetched sources into:", out_dir)


if __name__ == "__main__":
    main()


