import csv
import os
import re
from collections import defaultdict
from pathlib import Path

IPV4_RE = re.compile(r"^\d{1,3}(\.\d{1,3}){3}$")


def is_ipv4(s: str) -> bool:
    if not IPV4_RE.match(s):
        return False
    parts = s.split(".")
    # Basic numeric validity 0-255
    try:
        return all(0 <= int(p) <= 255 for p in parts)
    except ValueError:
        return False


def safe_filename(ip: str) -> str:
    # For IPv4, it's already safe. This is here for future-proofing.
    return ip


def parse_edges_csv(csv_path: Path):
    """
    Reads a CSV with at least: count,src_ip,dst_ip
    Also tolerates "bad" rows where extra columns exist; we take the LAST two IPv4s on the row as src/dst.
    Returns:
      edges_dir[(src,dst)] = count_sum
      edges_und[(a,b)] = count_sum (a<b)
      peers_out[src][dst] = count_sum
      peers_in[dst][src] = count_sum
      all_ips = set()
      stats about skipped lines
    """
    edges_dir = defaultdict(int)
    peers_out = defaultdict(lambda: defaultdict(int))
    peers_in = defaultdict(lambda: defaultdict(int))
    all_ips = set()
    skipped = 0
    fixed = 0

    with csv_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        if not header:
            raise ValueError("Empty CSV")

        for row in reader:
            if not row:
                continue

            # Trim whitespace
            row = [c.strip() for c in row if c is not None]

            # Must have a count in first column
            try:
                count = int(row[0])
            except Exception:
                skipped += 1
                continue

            # Collect all IPv4s in row (some rows have extra fields)
            ips = [c for c in row[1:] if is_ipv4(c)]

            if len(ips) < 2:
                skipped += 1
                continue

            # Heuristic: take last two IPv4s on the row as src/dst
            # This fixes rows like: count, A, B, B, C  -> uses B,C
            src, dst = ips[-2], ips[-1]
            if len(row) > 3:
                fixed += 1

            if src == dst:
                # ignore self-loops
                continue

            edges_dir[(src, dst)] += count
            peers_out[src][dst] += count
            peers_in[dst][src] += count
            all_ips.add(src)
            all_ips.add(dst)

    # Build undirected aggregation too (optional use)
    edges_und = defaultdict(int)
    for (src, dst), c in edges_dir.items():
        a, b = sorted([src, dst])
        edges_und[(a, b)] += c

    return edges_dir, edges_und, peers_out, peers_in, all_ips, skipped, fixed


def write_ip_note(
    out_dir: Path,
    ip: str,
    capture_name: str,
    peers_out: dict,
    peers_in: dict,
    top_n: int = 200,
):
    """
    Creates/overwrites IP markdown note.
    Includes outbound and inbound peers with links.
    """
    out_path = out_dir / f"{safe_filename(ip)}.md"

    # Sort peers by count desc
    out_items = sorted(peers_out.get(ip, {}).items(), key=lambda kv: kv[1], reverse=True)[:top_n]
    in_items = sorted(peers_in.get(ip, {}).items(), key=lambda kv: kv[1], reverse=True)[:top_n]

    lines = []
    lines.append("---")
    lines.append("type: ip")
    lines.append(f"ip: {ip}")
    lines.append("tags: [pcap, entity, ip]")
    lines.append("---")
    lines.append("")
    lines.append(f"# {ip}")
    lines.append("")
    lines.append("## Peers (outbound)")
    if out_items:
        for peer, c in out_items:
            lines.append(f"- [[{peer}]] — {c} packets")
    else:
        lines.append("- (none)")
    lines.append("")
    lines.append("## Peers (inbound)")
    if in_items:
        for peer, c in in_items:
            lines.append(f"- [[{peer}]] — {c} packets")
    else:
        lines.append("- (none)")
    lines.append("")
    lines.append("## Captures")
    lines.append(f"### {capture_name}")
    lines.append("")
    lines.append("> Generated from edges.csv. Counts represent aggregated packet observations per direction.")
    lines.append("")

    out_path.write_text("\n".join(lines), encoding="utf-8")


def write_capture_summary(
    out_dir: Path,
    capture_name: str,
    edges_dir: dict,
    edges_und: dict,
    all_ips: set,
    top_n: int = 30,
):
    """
    Creates a single capture summary note with top edges.
    """
    cap_dir = out_dir.parent / "Captures"
    cap_dir.mkdir(parents=True, exist_ok=True)
    cap_path = cap_dir / f"{capture_name}.md"

    # Top directed edges
    top_dir = sorted(edges_dir.items(), key=lambda kv: kv[1], reverse=True)[:top_n]
    top_und = sorted(edges_und.items(), key=lambda kv: kv[1], reverse=True)[:top_n]

    lines = []
    lines.append("---")
    lines.append("type: pcap_capture")
    lines.append(f"capture: {capture_name}")
    lines.append(f"unique_ips: {len(all_ips)}")
    lines.append(f"directed_edges: {len(edges_dir)}")
    lines.append(f"undirected_edges: {len(edges_und)}")
    lines.append("---")
    lines.append("")
    lines.append(f"# {capture_name}")
    lines.append("")
    lines.append(f"- Unique IPs: **{len(all_ips)}**")
    lines.append(f"- Directed edges: **{len(edges_dir)}**")
    lines.append(f"- Undirected edges: **{len(edges_und)}**")
    lines.append("")
    lines.append("## Top directed connections")
    for (src, dst), c in top_dir:
        lines.append(f"- {c} — [[{src}]] → [[{dst}]]")
    lines.append("")
    lines.append("## Top undirected connections (A↔B merged)")
    for (a, b), c in top_und:
        lines.append(f"- {c} — [[{a}]] ↔ [[{b}]]")
    lines.append("")

    cap_path.write_text("\n".join(lines), encoding="utf-8")


def main():
    print("=== edges.csv -> Obsidian IP entity notes ===\n")

    csv_path = Path(input("Path to edges.csv: ").strip().strip('"'))
    if not csv_path.exists():
        raise SystemExit(f"CSV not found: {csv_path}")

    vault_out = Path(input("Output folder INSIDE your vault (e.g. C:\\Vault\\PCAP Entities\\IPs): ").strip().strip('"'))
    vault_out.mkdir(parents=True, exist_ok=True)

    capture_name = input("Capture name (default: edges): ").strip()
    if not capture_name:
        capture_name = "edges"

    top_n = input("Max peers per section (default 200): ").strip()
    top_n = int(top_n) if top_n else 200

    print("\nParsing CSV (and repairing malformed rows)...")
    edges_dir, edges_und, peers_out, peers_in, all_ips, skipped, fixed = parse_edges_csv(csv_path)

    print(f"  Unique IPs: {len(all_ips)}")
    print(f"  Directed edges: {len(edges_dir)}")
    print(f"  Undirected edges: {len(edges_und)}")
    print(f"  Malformed rows fixed (extra columns): {fixed}")
    print(f"  Rows skipped: {skipped}")

    print("\nWriting IP notes...")
    all_ips_sorted = sorted(all_ips, key=lambda x: tuple(int(p) for p in x.split(".")))
    for i, ip in enumerate(all_ips_sorted, 1):
        write_ip_note(vault_out, ip, capture_name, peers_out, peers_in, top_n=top_n)
        if i % 50 == 0 or i == len(all_ips_sorted):
            print(f"  {i}/{len(all_ips_sorted)} notes written")

    print("\nWriting capture summary...")
    write_capture_summary(vault_out, capture_name, edges_dir, edges_und, all_ips)

    print("\nDone ✅")
    print(f"IP notes folder: {vault_out}")
    print(f"Capture summary: {vault_out.parent / 'Captures' / (capture_name + '.md')}")
    print("\nOpen your vault in Obsidian and check Graph view. Each IP note links to its peers.")


if __name__ == "__main__":
    main()
