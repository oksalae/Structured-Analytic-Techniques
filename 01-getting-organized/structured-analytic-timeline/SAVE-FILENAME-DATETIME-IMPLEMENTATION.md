# Save button: date and time in downloaded filename

This doc describes how the **Save** button (header red button and its export) names the downloaded file with the current date and time, so you can replicate the same behavior for the same button or another export.

## Behavior

- **Before:** `timeline-events.json`
- **After:** `timeline-events-YYYY-MM-DD_HH-mm-ss.json` (e.g. `timeline-events-2025-02-10_14-30-45.json`)

The timestamp is the **current** date and time at the moment the user clicks Save (client local time). Format is filesystem-safe (no colons in the time part) and sorts correctly as text.

## Where it’s implemented

- **File:** `app.js`
- **Function:** `exportEventsToJson()` (called when the header “Save” button is clicked)
- **UI:** The red “Save” button is `#btn-save-header` in `index.html`; its click handler calls `exportEventsToJson()`.

## Implementation steps

1. **Ensure a zero-pad helper exists** in the same function (or in scope). In `exportEventsToJson()` we use:
   ```js
   function pad2(n) { return n < 10 ? "0" + n : String(n); }
   ```
   If the export function doesn’t have `pad2`, add it or reuse an existing one.

2. **Right before creating the download link**, get the current time and build a timestamp string:
   ```js
   var now = new Date();
   var dateTimeStr = now.getFullYear() + "-" + pad2(now.getMonth() + 1) + "-" + pad2(now.getDate()) + "_" + pad2(now.getHours()) + "-" + pad2(now.getMinutes()) + "-" + pad2(now.getSeconds());
   ```
   Format: `YYYY-MM-DD_HH-mm-ss` (24-hour, hyphen-separated).

3. **Use that string in the download filename** instead of a fixed name:
   ```js
   a.download = "timeline-events-" + dateTimeStr + ".json";
   ```
   For another feature, keep the same pattern: `"<base-name>-" + dateTimeStr + ".<ext>"`.

4. **Leave the rest of the export flow unchanged**: create blob, create object URL, set `a.href`, trigger click, revoke URL.

## Full snippet (pattern only)

```js
// Inside the export/save function, after you have the blob and before a.click():

function pad2(n) { return n < 10 ? "0" + n : String(n); }  // if not already in scope

var now = new Date();
var dateTimeStr = now.getFullYear() + "-" + pad2(now.getMonth() + 1) + "-" + pad2(now.getDate()) + "_" + pad2(now.getHours()) + "-" + pad2(now.getMinutes()) + "-" + pad2(now.getSeconds());

var a = document.createElement("a");
a.href = url;   // your blob URL
a.download = "timeline-events-" + dateTimeStr + ".json";  // base name + timestamp + extension
a.click();
URL.revokeObjectURL(url);
```

To apply this to **the same Save button**: the logic already lives in `exportEventsToJson()` in `app.js`; no change needed unless you want a different format or base name. To apply to **another button** (e.g. another export): use the same `dateTimeStr` pattern and set `a.download` to `"<your-base-name>-" + dateTimeStr + ".<ext>"`.
