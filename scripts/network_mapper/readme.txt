# PCAP → Obsidian IP Map Tools

Two small utilities to turn a packet capture into an IP-to-IP “entity map” in **Obsidian Graph**.

## What’s included

### 1) `pcap-to-edges.ps1`
Parses a `.pcap` / `.pcapng` using **tshark** (Wireshark CLI) and outputs CSVs:
- `pairs.csv` — raw `src_ip,dst_ip` rows
- `edges.csv` — aggregated **directed** edges: `count,src_ip,dst_ip`
- `edges_undirected.csv` — aggregated **undirected** edges (A↔B merged): `count,ip_a,ip_b`

> Uses `-n` (no name resolution) by default.

### 2) `csv_to_obsidian_ip_notes.py`
Reads `edges.csv` and generates one Markdown note per IP address with `[[links]]` to peers.  
This makes Obsidian’s Graph view render the network as a map.

It also tolerates malformed CSV rows with extra columns by extracting the last two IPv4 addresses on the row.

---

## Requirements

- Windows PowerShell 5+ (or PowerShell 7)
- Wireshark installed (needs `tshark.exe`; `capinfos.exe` recommended for % progress)
- Python 3.9+ for the Markdown generator
- An Obsidian vault (any folder)

---

## Usage

### Step 1: PCAP → edges CSV
1. Put `pcap-to-edges.ps1` in a working folder.
2. Open PowerShell in that folder.
3. If scripts are blocked, allow running for this session only:
   ```powershell
   Set-ExecutionPolicy -Scope Process Bypass
