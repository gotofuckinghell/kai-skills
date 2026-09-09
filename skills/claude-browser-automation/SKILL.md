---
name: claude-browser-automation
description: "Converted from Claude-Skills: engineering/browser-automation. # Browser Automation  > **Category:** Engineering > **Domain:** Web Automation  ## Overview  The **B"
version: 1.0.0
author: borghei (Claude-Skills)
license: MIT + Commons Clause
platforms: [claude-code, hermes]
metadata:
  hermes:
    tags: [engineering, claude-skills, converted]
    source: https://github.com/borghei/Claude-Skills
    source_path: engineering/browser-automation
---

# Browser Automation

> **Category:** Engineering
> **Domain:** Web Automation

## Overview

The **Browser Automation** skill provides tools for building robust web automation, checking scripts for bot detection signatures, generating form automation code, and creating web scraping solutions with rate limiting and best practices.

## Clarify First

Before generating automation, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Target site & task** — the URL and exactly what to automate or scrape (drives the generated selectors and flow)
- [ ] **Which tool** — audit an existing script, build form automation, or generate a scraper (selects `anti_detection_checker.py` vs `form_automation_builder.py` vs `scraping_toolkit.py`)
- [ ] **Politeness strategy & authorization** — polite vs aggressive, robots.txt compliance, and that you are permitted to automate this target (sets request delays and backoff in the generated code)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Quick Start

```bash
# Check automation script for detection signatures
python scripts/anti_detection_checker.py --file ./my_scraper.py

# Generate form automation code from HTML
python scripts/form_automation_builder.py --url https://example.com/form --output form_script.py

# Generate scraping code with rate limiting
python scripts/scraping_toolkit.py --url https://example.com --strategy polite --output scraper.py
```

## Tools Overview

| Tool | Purpose | Key Flags |
|------|---------|-----------|
| `anti_detection_checker.py` | Audit automation code for bot detection signatures | `--file`, `--format` |
| `form_automation_builder.py` | Generate form filling scripts from HTML analysis | `--url`, `--html-file`, `--output` |
| `scraping_toolkit.py` | Generate web scraping code with rate limiting | `--url`, `--strategy`, `--output` |

## Workflows

### Build Reliable Scraper
1. Analyze target with `scraping_toolkit.py` to generate base code
2. Check generated code with `anti_detection_checker.py`
3. Address any detection signatures found
4. Test with progressive rate limiting

### Automate Form Submission
1. Provide form HTML to `form_automation_builder.py`
2. Review generated script for field mappings
3. Customize data sources and validation
4. Run anti-detection check on final script

## Reference Documentation

- [Browser Automation Guide](references/browser-automation-guide.md) - Anti-detection techniques, rate limiting strategies, ethical scraping practices

## Common Patterns

### Polite Scraping
- Respect robots.txt directives
- Implement exponential backoff on errors
- Use 2-5 second delays between requests
- Identify your bot with a descriptive User-Agent
- Cache responses to minimize repeat requests

### Anti-Detection Best Practices
- Rotate User-Agent strings realistically
- Randomize request timing (avoid fixed intervals)
- Handle cookies and sessions properly
- Avoid headless browser fingerprinting tells