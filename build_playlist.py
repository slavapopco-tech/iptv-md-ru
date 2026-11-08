#!/usr/bin/env python3
"""Build one M3U from the Russia and Moldova iptv-org country feeds."""
from urllib.request import Request, urlopen
import re
import sys

SOURCES = [
    ("Россия", "https://iptv-org.github.io/iptv/countries/ru.m3u"),
    ("Молдова", "https://iptv-org.github.io/iptv/countries/md.m3u"),
]

def fetch(url):
    req = Request(url, headers={"User-Agent": "iptv-md-ru playlist builder"})
    with urlopen(req, timeout=60) as response:
        return response.read().decode("utf-8-sig", errors="replace")

def set_group(extinf, group):
    attr = f'group-title="{group}"'
    if re.search(r'\bgroup-title="[^"]*"', extinf):
        return re.sub(r'\bgroup-title="[^"]*"', attr, extinf, count=1)
    comma = extinf.find(",")
    return extinf if comma < 0 else extinf[:comma] + " " + attr + extinf[comma:]

def main():
    output = ["#EXTM3U"]
    counts = {}
    for country, url in SOURCES:
        data = fetch(url)
        lines = [line.strip() for line in data.splitlines() if line.strip()]
        count = 0
        for line in lines:
            if line.startswith("#EXTM3U"):
                continue
            if line.startswith("#EXTINF:"):
                output.append(set_group(line, country))
                count += 1
            else:
                output.append(line)
        counts[country] = count

    if sum(counts.values()) == 0:
        raise RuntimeError("Both source playlists were empty")

    Path("russia-moldova.m3u").write_text(
        "\n".join(output) + "\n", encoding="utf-8"
    )
    print("Playlist generated:", counts)

if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"Playlist build failed: {exc}", file=sys.stderr)
        raise
