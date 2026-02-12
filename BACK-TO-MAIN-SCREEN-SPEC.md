# Back to Main Screen – Implementation Spec

This document describes how **“Back to Main Screen”** is implemented in the SAT tools so another AI or developer can add the same control to a new app (e.g. another tool in this repo).

---

## 1. Purpose

- Provide a single, consistent way for users to **return to the main hub** (the SAT tools landing page) from any tool.
- Use a **link** (not a button) so it works without JavaScript and is clearly navigational.
- Place it in the **tool’s header/toolbar**, typically on the **left**, before other controls (File, View, etc.).

---

## 2. Behavior

- **Click** → Navigate to the hub page in the **same tab** (`target="_self"`).
- **Hub URL**: In this repo the hub runs on port **3000** when using `node start-all.js`, so the href is `http://localhost:3000/`. Adjust the URL if your hub is served differently (e.g. different port, or relative path like `/` when the hub is the same origin).
- No JavaScript is required; the link works with plain HTML.

---

## 3. HTML (markup)

Use an **anchor** with the same structure and classes so styling stays consistent.

### Required

- **Element:** `<a>` (not `<button>`).
- **`href`:** Hub URL. In this repo: `http://localhost:3000/`.
- **`target="_self"`** so the hub opens in the same tab.
- **Visible text:** `Back to Main Screen`.
- **Icon:** An inline SVG (home icon) **before** the text.
- **Classes:** `btn-back-to-hub` (and optionally `btn-back-icon` on the SVG for sizing).
- **Accessibility:** `aria-label="Back to main screen"` and `title="Back to SAT Tools hub"` (or equivalent).

### Markup example

```html
<a href="http://localhost:3000/" target="_self" class="btn-back-to-hub" aria-label="Back to main screen" title="Back to SAT Tools hub">
  <svg class="btn-back-icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z" fill="currentColor"/></svg>
  Back to Main Screen
</a>
```

Notes:

- The SVG path is a **home** icon (house shape). Use `fill="currentColor"` so the icon uses the link’s text color.
- The link is placed in the header/toolbar, usually inside a “left” container (e.g. `timeline-header-left`, `dashboard-header-row`, `toolbar-left`) so it appears first on the left.

---

## 4. CSS (styling)

Use these rules so the control looks like the Timeline and Circleboarding tools. Adapt colors (e.g. to CSS variables) to match your app’s theme.

### Container (link)

- **Display:** `inline-flex`, `align-items: center`, `gap: 0.35rem` (icon + text).
- **Padding:** e.g. `0.35rem 0.75rem`.
- **Font:** `font: inherit`, `font-size: 0.85rem`.
- **Color:** Muted by default (e.g. `color: var(--text-muted)` or `#5c5c5c`), so it doesn’t compete with the main title.
- **Background:** `transparent`.
- **Border:** `1px solid var(--border)` (or your border color), `border-radius: 4px`.
- **Text:** `text-decoration: none`, `cursor: pointer`.

### Hover

- Slightly stronger text color (e.g. `var(--text)` or your primary text color).
- Border color a bit more visible or accent (e.g. `var(--text-muted)` or an accent).

### Icon (SVG)

- **Size:** `width: 1rem; height: 1rem;` (or 18px if you prefer).
- **Shrink:** `flex-shrink: 0` so the icon doesn’t shrink when space is tight.

### Example (variable-based theme)

```css
.btn-back-to-hub {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.35rem 0.75rem;
  font: inherit;
  font-size: 0.85rem;
  color: var(--text-muted);
  background: transparent;
  border: 1px solid var(--border);
  border-radius: 4px;
  text-decoration: none;
  cursor: pointer;
}

.btn-back-to-hub:hover {
  color: var(--text);
  border-color: var(--text-muted);
}

.btn-back-icon {
  width: 1rem;
  height: 1rem;
  flex-shrink: 0;
}
```

If your app doesn’t use CSS variables, replace `var(--text-muted)`, `var(--text)`, and `var(--border)` with your actual colors (e.g. `#8b949e`, `#e6edf3`, `#2d3a4d`).

---

## 5. Placement in the layout

- **Where:** In the **top bar / header** of the tool, on the **left**.
- **Order:** **First** control in that bar (before “File”, “Layouts”, “View”, etc.), so “Back to Main Screen” is the first thing users see when returning to the hub.
- **Container:** Put the link inside whatever wrapper your app uses for the left part of the header (e.g. a `div` with a class like `header-left`, `toolbar-left`, `dashboard-header-row`).

Example (conceptual):

```html
<header class="...">
  <div class="header-left">
    <a href="http://localhost:3000/" target="_self" class="btn-back-to-hub" ...>
      <svg class="btn-back-icon" ...>...</svg>
      Back to Main Screen
    </a>
    <!-- other toolbar items: File, Layouts, etc. -->
  </div>
  ...
</header>
```

---

## 6. Hub URL

- **Default in this repo:** `http://localhost:3000/` (hub started via `node start-all.js`).
- If the hub is served at a different origin (e.g. different port or host), change the `href` to that URL.
- If the hub is the same origin as the tool (e.g. same server, different path), you can use a relative path, e.g. `href="/"` or `href="/index.html"`, and keep `target="_self"`.

---

## 7. Checklist for another tool

- [ ] Add an `<a>` with visible text **“Back to Main Screen”** and class **`btn-back-to-hub`**.
- [ ] Set **`href`** to the hub URL (e.g. `http://localhost:3000/`), **`target="_self"`**.
- [ ] Include the **home icon SVG** before the text, with class **`btn-back-icon`** and **`aria-hidden="true"`**.
- [ ] Add **`aria-label="Back to main screen"`** and **`title="Back to SAT Tools hub"`** (or your hub name).
- [ ] Place the link **first** in the header/toolbar (left side).
- [ ] Add the **CSS** for `.btn-back-to-hub`, `.btn-back-to-hub:hover`, and `.btn-back-icon` (or equivalent if you reuse existing toolbar styles).

---

## 8. Reference implementations

- **Timeline:** `01-getting-organized/structured-analytic-timeline/index.html` (header, first item in `timeline-header-left`), `styles.css` (`.btn-back-to-hub`, `.btn-back-icon`).
- **Circleboarding:** `02-exploration/structured-analytic-circleboarding/index.html` (first item in `dashboard-header-row`), `styles.css` (same class names).
- **Causal Map:** `01-getting-organized/structured-analytic-causal-map/index.html` (first item in `#toolbar-left`); uses `toolbar-menu-btn toolbar-btn-back` and a similar SVG; same link text and href.

Use the Timeline or Circleboarding markup and CSS as the canonical pattern; Causal Map uses the same idea with different toolbar class names.
