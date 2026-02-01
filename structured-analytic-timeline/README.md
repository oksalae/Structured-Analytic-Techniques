# Timeline Creator

A localhost web app that displays a timeline and lets you add events via a form. Events require **Name**, **Description**, and **Time** (date + time). Data is validated and persisted in the browser with `localStorage`.

## Features

- **Form**: Name, Description, Time (date+time) with required validation and trimmed inputs
- **Time**: Stored as ISO 8601; timeline sorted by time (ascending)
- **Persistence**: Events saved to `localStorage` and survive page refresh
- **UI**: Field-level error messages, empty state when no events, immediate render on submit (no refresh)

## Run instructions

1. **Option A – Open file directly**  
   Double-click `index.html` or open it in your browser (e.g. drag and drop into Chrome).  
   Works as-is; some browsers may restrict `file://` for scripts. If the app doesn’t load, use Option B.

2. **Option B – Local server (recommended)**  
   From this directory, start a simple HTTP server:

   **Node (npx):**
   ```bash
   npx --yes serve -l 3000
   ```
   Then open: **http://localhost:3000**

   **Python 3:**
   ```bash
   python -m http.server 3000
   ```
   Then open: **http://localhost:3000**

3. Use the form to add events; they appear on the timeline immediately and are kept in `localStorage`.

## Project layout

- `index.html` – Page structure, form, timeline container
- `styles.css` – Layout and styling
- `app.js` – Validation, `localStorage`, unique IDs, timeline render
- `README.md` – This file

No build step or dependencies required for Option A; for Option B you only need Node or Python.
