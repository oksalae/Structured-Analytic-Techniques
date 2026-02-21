# Depth Event Map (Structured Analysis of Leaders)

A single-page web UI for building a **Depth Event Map**: a rooted, branching map around a central **Root** event with events arranged in depth lanes (left and right). Layout is fully automatic; no drag-and-drop.

## Features

- **Root at center** with two “+” buttons (left / right) to add Depth 1 events.
- **Depth lanes**: vertical columns labeled Depth 1, 2, 3… on each side; nodes align by (side, depth).
- **Curved connectors** (Bezier) from parent to child.
- **Editable event boxes**: click to edit text; blur to save.
- **Add child**: “+” on the outer edge of any node adds a child in the next depth lane on the same side.
- **Delete**: select a node (click) and press Delete/Backspace; confirm to remove the node and its subtree.
- **Pan**: drag the background. **Zoom**: mouse wheel. **Center on Root** / **Fit to view** toolbar buttons.
- **Import JSON**: load a previously exported nested JSON (validated; errors shown without changing current state).
- **Export**: **Copy JSON** / **Download JSON** in nested format with `children` arrays.
- **Nesting panel**: **Outline** (collapsible tree) and **JSON** (formatted export + Copy).

## Data format

Export is a nested tree:

- `version: 1`
- `root`: `{ id: "root", text: "...", children: [ ... ] }`
- Each non-root node has `side: "left" | "right"` and `children: []`.

Import requires valid structure, unique IDs, and `side` on non-root nodes.

## How to run

Open `index.html` in a modern browser (no server required).
