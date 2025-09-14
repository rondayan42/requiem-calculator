#!/usr/bin/env python3
import json
import time
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen


TS_LIST = [
    "20170504110444",
    "20170429184609",
    "20170429185928",
    "20161221164956",
    "20161119113620",
    "20160924030950",
    "20160831035703",
]


def fetch_one(sub_id: str, out_dir: Path) -> None:
    print(f"spec {sub_id}: starting")
    for ts in TS_LIST:
        url = f"https://web.archive.org/web/{ts}id_/http://requiem.isnet.ru/ajax/calculator/load?{urlencode({'c': sub_id})}"
        dest = out_dir / f"load-{sub_id}-{ts}.txt"
        if dest.exists():
            print(f"  {ts}: cached -> {dest.name}")
            return
        try:
            print(f"  {ts}: GET …", end="")
            req = Request(url, headers={"User-Agent": "Mozilla/5.0 (Wayback fetch)"})
            with urlopen(req, timeout=20) as r, dest.open("wb") as w:
                w.write(r.read())
            print(" ok")
            time.sleep(0.2)  # be nice to Wayback
            return
        except Exception as e:
            print(f" fail ({e.__class__.__name__})")
            continue
    print(f"  all timestamps failed for spec {sub_id}")


def main():
    root = Path(__file__).resolve().parent
    data_path = root / "data.json"
    out_dir = root / "ajax"
    out_dir.mkdir(parents=True, exist_ok=True)

    data = json.loads(data_path.read_text(encoding="utf-8"))
    sub_ids = set()
    for jobs in data.get("jobs", {}).values():
        for job in jobs:
            for spec in job.get("specs", []):
                sub_ids.add(str(spec["id"]))

    print(f"Total specs: {len(sub_ids)}")
    for sub_id in sorted(sub_ids):
        fetch_one(sub_id, out_dir)

    print("Done. Fetched AJAX payloads to:", out_dir)


if __name__ == "__main__":
    main()


