#!/usr/bin/env python3
import re
import time
from collections import deque
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen
from pathlib import Path


BASE = "https://rondayan42.github.io/requiem-wiki/"
UA = {"User-Agent": "Mozilla/5.0 (RequiemScraper)"}


class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
    def handle_starttag(self, tag, attrs):
        if tag.lower() == "a":
            href = dict(attrs).get("href")
            if href:
                self.links.append(href)


def fetch(url: str) -> bytes:
    req = Request(url, headers=UA)
    with urlopen(req, timeout=20) as r:
        return r.read()


def crawl(out_dir: Path, max_pages: int = 1000) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    seen = set()
    q = deque([BASE])
    pages = 0
    domain = urlparse(BASE).netloc
    print(f"Crawling {BASE} (max {max_pages})")

    while q and pages < max_pages:
        url = q.popleft()
        if url in seen:
            continue
        seen.add(url)
        try:
            content = fetch(url)
        except Exception:
            continue

        # save
        rel = url[len(BASE):] if url.startswith(BASE) else url.replace("://", "_")
        rel = rel.strip("/") or "index"
        target = out_dir / (rel.replace("/", "_") + ".html")
        target.write_bytes(content)
        pages += 1
        print(f"  saved: {target.name}")

        # extract links
        try:
            parser = LinkParser()
            parser.feed(content.decode("utf-8", errors="ignore"))
            for href in parser.links:
                nxt = urljoin(url, href)
                pu = urlparse(nxt)
                if pu.netloc == domain and nxt.startswith(BASE):
                    if '#' in nxt:
                        nxt = nxt.split('#',1)[0]
                    if nxt not in seen:
                        q.append(nxt)
        except Exception:
            pass
        time.sleep(0.05)

    print(f"Done. Cached {pages} pages in {out_dir}")


if __name__ == "__main__":
    root = Path(__file__).resolve().parent / "wiki_cache"
    crawl(root, max_pages=1200)


