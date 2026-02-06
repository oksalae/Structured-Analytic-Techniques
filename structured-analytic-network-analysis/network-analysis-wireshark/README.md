# Network Mapper

Web UI tool that **passively** maps hosts on the same network by capturing traffic (PCAP), extracting source and destination IP addresses, and displaying them as an interactive graph.

## Features

- **Start PCAP capture** — Click the button, choose how long to listen (1–60 minutes), optionally pick a network interface.
- **Live timer** — Countdown while the capture runs.
- **Graph view** — After capture, IPs are shown as nodes; connections between them as lines (edges).
- **Search** — Text search to find and highlight IP addresses on the graph; matching nodes are emphasized and the view can focus on them.

## Requirements for listening (PCAP capture)

1. **Wireshark (with tshark and Npcap)**  
   - Install [Wireshark](https://www.wireshark.org/download.html).  
   - During setup, ensure **Npcap** is selected (default). Npcap is the driver that allows capturing raw packets.  
   - This gives you:
     - **tshark** — command-line capture (used by this app to create the PCAP file).
     - **Npcap** — required for capturing on the network interface.

2. **Administrator rights**  
   - Capturing raw traffic usually requires running the capture process (and thus this app) **as Administrator** on Windows.  
   - Otherwise capture may fail or be empty.

3. **Python**  
   - Python 3.10+ recommended.  
   - Install dependencies: `pip install -r requirements.txt`

## Which app is used for raw data?

- **tshark** (from Wireshark) is used to create the PCAP file.  
- It’s the right choice because:
  - It uses Npcap for raw packet capture.
  - It can limit capture by **duration** (`-a duration:N`).
  - It writes standard PCAP/PCAPNG that we then parse with **Scapy** to get only source and destination IPs.

## Run the app

1. Install Wireshark (with Npcap) and Python dependencies as above.
2. From the project folder, run (preferably in an elevated “Run as administrator” terminal):

   ```bash
   python app.py
   ```

3. Open a browser at: **http://localhost:5000**

4. Click **Start PCAP capture**, set the listen time, then **Start listening**. When the timer finishes, the graph updates with IPs and connections. Use the search box to find IPs on the graph.

## Project layout

- `app.py` — Flask server: capture start/status/result APIs, tshark invocation, PCAP parsing with Scapy.
- `static/index.html` — Web UI: capture button, time modal, timer, graph container, search.
- `static/app.js` — Logic: modal, countdown, polling, vis-network graph, search/highlight.
- `static/style.css` — Styling.
- `requirements.txt` — Python dependencies (Flask, Scapy).

## License

Use as you like; ensure your use of passive capture complies with your network’s policy and local laws.
