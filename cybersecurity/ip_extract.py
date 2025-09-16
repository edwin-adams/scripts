#!/usr/bin/env python3
import re
import sys
import ipaddress
from typing import List, Tuple

IP_CIDR_RE = re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}(?:/\d{1,2})?\b')

def parse_ranges(text: str, merge: bool = False) -> List[Tuple[int, int]]:
    """
    Extract IPv4 addresses and CIDR blocks from text and return sorted (start_int, end_int) ranges.
    """
    matches = IP_CIDR_RE.findall(text)
    ranges = set()

    for m in matches:
        try:
            if '/' in m:
                net = ipaddress.ip_network(m, strict=False)
                start = int(net.network_address)
                end = int(net.broadcast_address)
            else:
                ip = ipaddress.ip_address(m)
                start = end = int(ip)
            ranges.add((start, end))
        except ValueError:
            # Skip invalids like 999.999.999.999 or bad prefixes
            continue

    # Sort
    sorted_ranges = sorted(ranges, key=lambda t: (t[0], t[1]))
    return merge_ranges(sorted_ranges) if merge else sorted_ranges

def merge_ranges(ranges: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
    """
    Merge overlapping or contiguous ranges.
    """
    if not ranges:
        return []
    merged = [ranges[0]]
    for start, end in ranges[1:]:
        last_start, last_end = merged[-1]
        if start <= last_end + 1:
            merged[-1] = (last_start, max(last_end, end))
        else:
            merged.append((start, end))
    return merged

def format_range(start: int, end: int) -> str:
    return f"{ipaddress.ip_address(start)}-{ipaddress.ip_address(end)}"

def main():
    if len(sys.argv) < 2:
        print("Usage: python ip_extract.py <input.txt> [--merge] [--out output.txt]")
        sys.exit(1)

    in_path = None
    out_path = None
    merge = False

    # Simple arg parsing
    args = sys.argv[1:]
    if args and not args[0].startswith('-'):
        in_path = args.pop(0)

    i = 0
    while i < len(args):
        if args[i] == '--merge':
            merge = True
            i += 1
        elif args[i] == '--out' and i + 1 < len(args):
            out_path = args[i + 1]
            i += 2
        else:
            i += 1

    with open(in_path, 'r', encoding='utf-8', errors='ignore') as f:
        text = f.read()

    ranges = parse_ranges(text, merge=merge)
    lines = [format_range(s, e) for (s, e) in ranges]
    output = "\n".join(lines)

    if out_path:
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(output + "\n")
        print(f"Wrote {len(lines)} ranges to {out_path}")
    else:
        print(output)

if __name__ == "__main__":
    main()
