# Feishu (and rich web-doc) extraction — worked example

Session: extracting a Feishu doc (SPD Flash Programmer guide) to PDF.

## What happened

1. `js("document.body.innerText")` returned ~2 KB of text — title, section
   headings ("1. Software Tool Download", "3. Operation Flow"), changelog,
   download links, contact. It looked complete enough to be plausible.
2. But the ACTUAL instructions (install steps, driver setup, unlock procedure,
   FAQ answers, timing calculator table) were all in embedded `<img>`
   screenshots. innerText never sees `<img>` content.
3. A browser print-to-PDF of the same page produced 6 pages / 20 images /
   1.5 MB — the FULL content, but as images (not searchable).
4. OCR of that print-to-PDF (pymupdf render + rapidocr-onnxruntime) recovered
   all the text: video links, cable order, CH340 driver install, unlock steps,
   FAQ, the tRFC/tRP/tRAS/tRC calculator table, and a CMOS-reset tip.

## The lesson, distilled

- For Feishu / Notion / Confluence guides, the DOM text is a **skeleton**.
- To know if you're missing content: check whether the page is a
  product-guide/tutorial AND the innerText looks thin for the topic.
- Always prefer print-to-PDF (captures images) over innerText for these.
- If searchable text is required, OCR the print-to-PDF (see
  `scripts/ocr_pdf.py`).

## Feishu specifics

- Login-gated sections show "Log In or Sign Up" and are NOT in the DOM or
  images — tell the user which sections are missing, offer to re-extract
  after they log in via the browser.
- Feishu docs render timestamps ("8/27/26, 12:28 PM"), page markers ("1/6"),
  and the doc URL in a header/footer on every printed page — strip these
  when rebuilding a clean PDF.

## Search-engine captcha behavior (browser_exec)

Tested against a live Chromium via CDP. Timing matters more than the engine:

| Engine | Endpoint | Behavior |
|--------|----------|----------|
| DuckDuckGo | `html.duckduckgo.com/html/?q=` | Instant results, no captcha |
| Brave | `search.brave.com/search?q=` | Instant results, own index |
| Startpage | `startpage.com/sp/search?query=` | PoW captcha, self-resolves ~3-8s |
| Yandex | `yandex.com/search/?text=` | SmartCaptcha, self-resolves ~3-8s |
| Ecosia | `ecosia.org/search?q=` | Hard Cloudflare block |
| SearXNG (public) | `searx.be/search?q=` | Hard Cloudflare block |

For Startpage/Yandex: after `wait_for_load()`, poll in a loop until
`document.title` no longer contains "Verifying"/"robot"/"robot", THEN read
`document.body.innerText`. Reading immediately returns the captcha page.
The initial "these engines don't work" conclusion was WRONG — they just need
the wait-and-poll, not an instant read.
