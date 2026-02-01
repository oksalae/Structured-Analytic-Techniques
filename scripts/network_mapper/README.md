--- a/README.md
+++ b/README.md
@@ -1,200 +1,200 @@
 # network_mapper
 
 `network_mapper` turns packet captures into a graph you can explore in **Obsidian**: first it extracts **IPv4 directed edges** from a PCAP (`count,src_ip,dst_ip`), then it generates **one note per IP** with inbound/outbound peers and a capture summary—so you can pivot through traffic like an entity network.
 
 ---
 
 ## What it does
 
 1. **PCAP → `edges.csv`**  
    Converts a PCAP/PCAPNG into a directional edge list where each row is a connection **src → dst** with an aggregated packet count.
 
 2. **`edges.csv` → Obsidian notes**  
    Generates:
    - `IPs/<ip>.md` for every IP, listing top outbound and inbound peers
    - `Captures/<capture>.md` summarizing the capture and top connections
 
 With everything inside your vault, Obsidian’s **Graph view** becomes an interactive network map:
 
-![Obsidian graph view showing IP nodes and connections](docs/screenshots/screenshot_3.png)
+![Obsidian graph view showing IP nodes and connections](assets/img/screenshot_3.png)
 
 ---
 
 ## Quick Start
 
 **Install**
 - **Wireshark** (for `tshark.exe`; `capinfos.exe` is optional but nice for progress)
 - **Python 3.x**
 - **Obsidian** (open your vault where you want the notes to live)
 
 **Run**
 1. Run the PowerShell parser to create `edges.csv`
 2. Run the Python generator to create the Obsidian notes inside your vault
 3. Open your vault in Obsidian and use **Graph view**
 
-![Running the Python generator and choosing the output location](docs/screenshots/screenshot_2.png)
+![Running the Python generator and choosing the output location](assets/img/screenshot_2.png)
 
 ---
 
 ## How to use
 
 ### 1) Create `edges.csv` from a PCAP (PowerShell)
 
 Run the parser and provide:
 - the path to your `.pcap` / `.pcapng`
 - an output folder (recommended: a clean output folder, not your scripts directory)
 
 Example flow:
 
-![PowerShell PCAP parsing and edges.csv creation](docs/screenshots/screenshot_1.png)
+![PowerShell PCAP parsing and edges.csv creation](assets/img/screenshot_1.png)
 
 **Output produced**
 - `edges.csv` (directional, weighted): `count,src_ip,dst_ip`
 
 ---
 
 ### 2) Generate Obsidian IP notes (Python)
 
 Run the generator and provide:
 - the path to `edges.csv`
 - a capture name (optional)
 - **an output folder inside your Obsidian vault** (recommended), e.g. `YourVault/PCAP_Entities/IPs`
 
 Once generated, open your vault and explore the network (Graph view + backlinks):
 
-![Obsidian graph view after import](docs/screenshots/screenshot_3.png)
+![Obsidian graph view after import](assets/img/screenshot_3.png)
 
 ---
 
 ### 3) Explore results inside Obsidian
 
 Open any IP note to see the highest-volume peers (outbound and inbound), plus a capture reference:
 
-![Example IP note with peer lists](docs/screenshots/screenshot_4.png)
+![Example IP note with peer lists](assets/img/screenshot_4.png)
 
 ---
 
 ## Project layout (suggested)
 
 ```text
 network_mapper/
   pcap-to-edges.ps1
   csv_to_obsidian_ip_notes.py
   README.md
-  docs/
-    screenshots/
-      screenshot_1.png
-      screenshot_2.png
-      screenshot_3.png
-      screenshot_4.png
+  assets/
+    img/
+      screenshot_1.png
+      screenshot_2.png
+      screenshot_3.png
+      screenshot_4.png
