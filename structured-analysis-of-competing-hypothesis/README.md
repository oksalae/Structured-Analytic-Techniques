# Analysis of Competing Hypothesis (ACH) – Evidence List

A single-page tool for building and editing an **Analysis of Competing Hypothesis** matrix: evidence rows × hypothesis columns (H1–H5), with analysis notes and persistence to JSON.

![ACH Evidence List view](assets/img/screenshot.png)  
*Evidence matrix, hypothesis box, and filter/sort.*

---

## How to run

1. From this folder, start the server:
   ```bash
   node server.js
   ```
2. Open **http://localhost:8084** in a browser.  
   The server serves `evidence-list.html` by default and provides APIs to load/save evidence and hypotheses.

**From repo root:** Run `node start-all.js` and open the hub at http://localhost:3000, then click the ACH / Competing Hypothesis link (port 8084). See [HUB-PAGE-INSTRUCTIONS.md](../HUB-PAGE-INSTRUCTIONS.md).

---

## Features

- **Evidence matrix** – Table of evidence rows (with title, description, reliability/credibility badges) vs columns H1–H5 and an Analysis cell per row. Click a cell to open the row-edit modal (H1–H5, Analysis). Click the evidence card to open **Evidence details** (name, description, source, date/time, reliability, credibility, **colour**).
- **Hypothesis box** – Lists H1–H5; click an item to edit title and description. Edits are saved to `hypothesis_example.json`.
- **Filter & sort** – Filter by source reliability/credibility; sort by date (asc/desc), reliability, or credibility. Optional custom order with drag-and-drop.
- **Import / Export** – **Import:** Hypothesis (JSON → server) or Evidence (JSON file → replace tree). **Export:** Hypothesis or Evidence as JSON download.
- **Update from file** – Load evidence from a chosen JSON filename (default `evidence_example.json`); filename is stored in `localStorage`.
- **Row colour** – Each evidence item can have a `color` (hex, e.g. `#6a4c93`) in the JSON. The colour is editable in Evidence details and in Add new evidence, and is shown as a left border and light tint across the full row (Evidence → H1–H5 → Analysis).

---

## Data files

| File | Purpose |
|------|--------|
| `evidence_example.json` | Evidence tree (hierarchical); written by **Save** and by **Import Evidence**. |
| `hypothesis_example.json` | H1–H5 hypotheses (object keyed by id); written by **Save** in the hypothesis modal and by **Import Hypothesis**. |
| `evidence_list.jsonl` | Flat evidence list (one JSON object per line); updated when evidence is saved. |

---

## API (server)

- `GET /` → serves `evidence-list.html`
- `GET /evidence_example.json`, `GET /hypothesis_example.json` → static files
- `POST /api/save-evidence` → body: evidence tree JSON; writes `evidence_example.json` and `evidence_list.jsonl`
- `POST /api/save-hypothesis` → body: hypothesis object JSON; writes `hypothesis_example.json`

---

## Tech

- Single HTML file (`evidence-list.html`) with embedded CSS and JavaScript.
- Node server (`server.js`) for static files and save APIs.
- No build step; run the server and open the app in a browser.
