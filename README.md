# Structured Analytic Techniques

A collection of lightweight, analyst-focused tools supporting Structured Analytic Techniques (SAT).  
All tools run client-side, require no backend, and work offline where applicable.

**Hub:** Open **`index.html`** at the repo root (or run a static server here) to see the tool hub. Each button opens a tool in a new tab; start each tool’s server from its folder (see [HUB-PAGE-INSTRUCTIONS.md](HUB-PAGE-INSTRUCTIONS.md) for port assignments). The **Back to Main Screen** button in Causal Map and Timeline opens the hub at **http://localhost:3000/** — run a static server at the repo root on port 3000 for that button to work. **One terminal:** from the repo root run **`node start-all.js`** to start the hub (3000), Causal Map (8765), Timeline (8080), Circleboarding (8082), and Multiple Hypothesis (8083) together; press Ctrl+C to stop all.

## Purpose

These tools integrate Structured Analytic Techniques (SAT) into practical, lightweight workflows.  
The aim is to externalize analytic thinking—making assumptions, relationships, and timelines explicit—while reducing cognitive bias and improving transparency. The tools support exploratory analysis in complex and uncertain problem spaces without imposing heavy frameworks or infrastructure.

![Analysis](assets/img/mainpage.png)
Picture: Structured Analytic Techniques for Intelligence Analysis Richards J. Heuer Jr., Randolph H. Pherson

## Contents

- **structured-analytic-causal-map/** (port 8765)
  - Browser-based causal / concept map editor for SAT. Renders a hierarchical dataset as an interactive node-link graph (SVG); supports node creation, editing, annotation (description + source), colors, pan & zoom, and force-simulation “Float” mode. Use for DIMEFIL/PESTLE/PM-MESII etc. in the Getting Organized phase. JSON import/export; runs offline.

- **structured-analytic-timeline/** (port 8080)
  - Browser-based timeline tool for SAT. Capture timestamped events (name, description, source, date/time), visualize them on a time axis with zoom and scale range, open Event Details for each event, and create/export Indicators (What / Who / When / Where / Why / How) to `Indicators.txt` or via server. For Getting Organized and Diagnostic phase.

- **structured-analytic-circleboarding/** (port 8082)
  - Kanban-style dashboard for 5WH + “So what?” indicators. Six category boxes (Who?, What?, Why?, When?, Where?, How?) plus a 6-lane “So what?” area; drag between them and reorder. Loads from **CircleboardData.txt** or **Indicators.txt** (other tools can export to Indicators.txt). Use **Refresh from Indicators.txt** to merge new items from other modules without losing existing board data.

- **structured-analytic-multiple-hypothesis-generation/** (port 8083)
  - Hypothesis Generation screen: candidate statements from a source list are placed into question columns (Who?, What?, Why?) and a Permutation area, with drag-to-reorder. Source list is populated from **Multiple_Hypothesis_Generation.txt** (or add items in-app). From Circleboarding, use **Save for Hypothesis Generation** in the “So what?” section to write that file; then open this tool to generate and organize hypotheses.

- **scripts/**
  - Miscellaneous and experimental scripts
  - **network_mapper/** — PCAP-to-graph tooling for Obsidian
