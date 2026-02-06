"""
Network Mapper - Passive PCAP-based host discovery with Web UI.
Uses tshark for capture and scapy for parsing. Requires Wireshark/Npcap (tshark) installed.
"""
import os
import re
import subprocess
import tempfile
import threading
import time
import uuid
from pathlib import Path

from flask import Flask, send_from_directory, request, jsonify

# Optional: scapy for parsing; tshark is used for capture
try:
    from scapy.all import PcapReader
    from scapy.layers.inet import IP
    SCAPY_AVAILABLE = True
except ImportError:
    SCAPY_AVAILABLE = False

app = Flask(__name__, static_folder="static", static_url_path="")

# In-memory job store: job_id -> { status, result?, error?, pcap_path? }
jobs = {}
jobs_lock = threading.Lock()

# Default tshark paths (Windows)
TSHARK_PATHS = [
    r"C:\Program Files\Wireshark\tshark.exe",
    r"C:\Program Files (x86)\Wireshark\tshark.exe",
]


def find_tshark():
    """Locate tshark executable."""
    for path in TSHARK_PATHS:
        if os.path.isfile(path):
            return path
    # Try PATH
    import shutil
    return shutil.which("tshark")


def get_interfaces():
    """List capture interfaces via tshark -D. Returns list of { number, label }."""
    tshark = find_tshark()
    if not tshark:
        return []
    try:
        out = subprocess.run(
            [tshark, "-D"],
            capture_output=True,
            text=True,
            timeout=10,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )
        if out.returncode != 0:
            return []
        # Parse lines like "1. \Device\NPF_{...} (Description)"
        interfaces = []
        for line in out.stdout.strip().splitlines():
            m = re.match(r"^(\d+)\.\s+(.+)$", line)
            if m:
                num, label = m.group(1), m.group(2).strip()
                interfaces.append({"number": num, "label": label})
        return interfaces
    except Exception:
        return []


def run_capture(job_id: str, duration_seconds: int, interface: str | None, pcap_path: str):
    """Run tshark capture in background and then parse pcap."""
    tshark = find_tshark()
    with jobs_lock:
        jobs[job_id]["status"] = "running"

    if not tshark:
        with jobs_lock:
            jobs[job_id]["status"] = "error"
            jobs[job_id]["error"] = "tshark not found. Install Wireshark (includes Npcap and tshark)."
        return

    cmd = [
        tshark,
        "-q",  # quiet
        "-w", pcap_path,
        "-a", f"duration:{int(duration_seconds)}",
    ]
    if interface:
        # interface is the interface number string from tshark -D (e.g. "1", "2")
        cmd.extend(["-i", str(interface)])
    else:
        cmd.extend(["-i", "1"])

    try:
        subprocess.run(
            cmd,
            capture_output=True,
            timeout=duration_seconds + 30,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )
    except subprocess.TimeoutExpired:
        with jobs_lock:
            jobs[job_id]["status"] = "error"
            jobs[job_id]["error"] = "Capture timed out."
        return
    except Exception as e:
        with jobs_lock:
            jobs[job_id]["status"] = "error"
            jobs[job_id]["error"] = str(e)
        return

    result = parse_pcap_file(pcap_path)
    if result is None:
        with jobs_lock:
            jobs[job_id]["status"] = "error"
            jobs[job_id]["error"] = "Parsing failed (missing Scapy or invalid PCAP)."
        return
    if "error" in result:
        with jobs_lock:
            jobs[job_id]["status"] = "error"
            jobs[job_id]["error"] = result["error"]
        return

    with jobs_lock:
        jobs[job_id]["status"] = "completed"
        jobs[job_id]["result"] = result

    try:
        os.remove(pcap_path)
    except OSError:
        pass


def parse_pcap_file(pcap_path: str) -> dict | None:
    """
    Parse a PCAP file and return { nodes, edges, parsed, host_count, connection_count }
    or { "error": "..." } on parse error, or None if Scapy unavailable / file missing.
    """
    if not SCAPY_AVAILABLE or not os.path.isfile(pcap_path):
        return None
    nodes = set()
    edges = set()  # (src, dst) - directed
    try:
        with PcapReader(pcap_path) as reader:
            for pkt in reader:
                if IP in pkt:
                    src = pkt[IP].src
                    dst = pkt[IP].dst
                    nodes.add(src)
                    nodes.add(dst)
                    edges.add((src, dst))
    except Exception as e:
        return {"error": f"Parse error: {e}"}
    node_list = [{"id": ip, "label": ip} for ip in sorted(nodes)]
    edge_list = [
        {"from": a, "to": b, "title": f"SRC {a} → DST {b}"}
        for a, b in sorted(edges)
    ]
    return {
        "nodes": node_list,
        "edges": edge_list,
        "parsed": True,
        "host_count": len(node_list),
        "connection_count": len(edge_list),
    }


@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.route("/api/interfaces")
def api_interfaces():
    return jsonify(get_interfaces())


@app.route("/api/capture/start", methods=["POST"])
def api_capture_start():
    data = request.get_json() or {}
    duration = int(data.get("duration_seconds", 60))
    duration = max(1, min(3600, duration))  # 1s–1h
    interface = data.get("interface") or None
    if interface == "":
        interface = None

    job_id = str(uuid.uuid4())
    fd, pcap_path = tempfile.mkstemp(suffix=".pcap")
    os.close(fd)

    with jobs_lock:
        jobs[job_id] = {
            "status": "pending",
            "result": None,
            "error": None,
            "duration_seconds": duration,
        }

    thread = threading.Thread(
        target=run_capture,
        args=(job_id, duration, interface, pcap_path),
        daemon=True,
    )
    thread.start()

    return jsonify({"job_id": job_id, "duration_seconds": duration})


@app.route("/api/capture/status/<job_id>")
def api_capture_status(job_id):
    with jobs_lock:
        job = jobs.get(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404
    return jsonify({"status": job["status"], "error": job.get("error")})


@app.route("/api/capture/result/<job_id>")
def api_capture_result(job_id):
    with jobs_lock:
        job = jobs.get(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404
    if job["status"] != "completed":
        return jsonify({"error": "Job not completed", "status": job["status"]}), 400
    return jsonify(job["result"])


@app.route("/api/import-pcap", methods=["POST"])
def api_import_pcap():
    """Parse an uploaded PCAP file (no capture). Same result as capture + parse."""
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    f = request.files["file"]
    if not f or not f.filename:
        return jsonify({"error": "No file selected"}), 400
    if not (f.filename.lower().endswith(".pcap") or f.filename.lower().endswith(".pcapng")):
        return jsonify({"error": "File must be .pcap or .pcapng"}), 400
    fd, pcap_path = tempfile.mkstemp(suffix=".pcap")
    try:
        f.save(pcap_path)
        result = parse_pcap_file(pcap_path)
    finally:
        try:
            os.remove(pcap_path)
        except OSError:
            pass
    if result is None:
        return jsonify({"error": "Scapy not available or invalid PCAP"}), 500
    if "error" in result:
        return jsonify({"error": result["error"]}), 400
    return jsonify(result)


if __name__ == "__main__":
    print("TShark found:", find_tshark())
    print("Scapy available:", SCAPY_AVAILABLE)
    app.run(host="0.0.0.0", port=5000, debug=False)
