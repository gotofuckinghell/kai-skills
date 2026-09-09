---
name: web-document-extraction
description: "Extract web docs incl. image-embedded text; render to PDF."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [web, extraction, scraping, ocr, pdf, feishu, notion, browser]
    related_skills: [ocr-and-documents, pdf]
---

# Web Document Extraction & PDF Rendering

Extract content from web pages and web-hosted documents (Feishu, Notion,
Confluence, Tencent Docs, wikis), then optionally render it to a clean PDF.

## When to use

- User pastes a URL and says "вытяни эту страницу / extract this page".
- User asks to turn a web page or web doc into a PDF.
- A page's visible text looks incomplete or truncated after a naive extract.

## The single most important insight

**Rich web-doc platforms (Feishu, Notion, Confluence) store the actual body
content in embedded IMAGES (screenshots of the product/instructions), not in
DOM text.** `document.body.innerText` returns only a skeleton — titles,
section headings, changelog entries, download links — while the real "meat"
(step-by-step instructions, screenshots, tables) lives in `<img>` elements
that innerText never sees.

So a naive `innerText` extract that "looks complete" is usually MISSING most
of the value. Always sanity-check: if the page is a product guide / tutorial
and the extracted text is suspiciously thin, the content is in images.

## Workflow — three paths

### Path 1: plain text page (articles, docs with real text)
Use `web_extract` (needs a real extract backend, e.g. `parallel` — not ddgs,
which is search-only) or `browser_exec` with `js("document.body.innerText")`.
Scroll to the bottom first to trigger lazy-load:
```python
for i in range(10):
    js("window.scrollTo(0, document.body.scrollHeight)")
    time.sleep(1)
```

### Path 2: image-heavy doc (Feishu/Notion guide, tutorial)
Do NOT trust innerText. Two options, both validated:
1. **Print to PDF via CDP** — captures the images as-is:
   `cdp("Page.printToPDF", printBackground=True, preferCSSPageSize=True)`
   (decode the base64 `data` field, write to `.pdf`). Result is image-based:
   text is NOT searchable, but content is complete.
2. **Screenshot each page + OCR** — for searchable text. Render the saved PDF
   or page screenshots through `scripts/ocr_pdf.py` (see below).

### Path 3: turn the extracted content into a clean, searchable PDF
Use `fpdf2`. See pitfall about Unicode below. Combine: extract full text (via
OCR if Path 2), then lay it out with `fpdf2` into a clean PDF.

## Pitfalls

- **Feishu login wall**: sections gated behind "Log In or Sign Up" are NOT in
  the DOM or the images. State plainly to the user which sections are missing;
  offer to let them log in via the browser so you can re-extract the full page.
- **fpdf2 core fonts are latin-1 only.** Characters like `—` (em-dash),
  `–` (en-dash), CJK, `'` (curly quote) raise `FPDFUnicodeEncodingException`.
  Fix: replace with ASCII (`--`, `-`, `'`) OR `pdf.add_font()` a Unicode TTF
  (e.g. DejaVuSans.ttf). Simplest: sanitize every string before writing.
- **`web_extract` with ddgs backend fails** — DuckDuckGo is search-only. Set
  `hermes config set web.extract_backend parallel` (or firecrawl/tavily/exa).
- **Screenshot/printToPDF can time out on heavy pages** — the CDP call has a
  default timeout; retry or raise the timeout for large image-heavy pages.
- **capture_screenshot on big pages** may time out; prefer printToPDF or
  per-page rendering + OCR.

## Offline OCR toolchain (no tesseract needed)

Works entirely offline and cross-platform:
```bash
# in the Hermes venv:
uv pip install pymupdf rapidocr-onnxruntime
```
`rapidocr-onnxruntime` bundles ONNX models (first run downloads them to
`~/.cache`). Render PDF pages with `pymupdf`, then OCR the numpy array.
Ready-to-run script: `scripts/ocr_pdf.py` (usage:
`python ocr_pdf.py "file.pdf"` → prints page-by-page text).

## Reading pages via browser — search-engine captcha notes

When scraping search results through `browser_exec`:
- **DuckDuckGo** (`html.duckduckgo.com/html/?q=`) and **Brave**
  (`search.brave.com/search?q=`) return results instantly.
- **Startpage** and **Yandex** self-resolve their PoW/captcha after a few
  seconds — poll `document.title` until "Verifying"/"robot" disappears, THEN
  read `document.body.innerText`. Do not read immediately after `wait_for_load()`.
- **Ecosia** and public **SearXNG** instances sit behind hard Cloudflare — skip.

See `references/feishu-and-rich-docs.md` for the worked Feishu example and the
search-engine captcha table.
