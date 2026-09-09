---
name: cicada-smart-rules
description: "Intelligent rule selection based on project context, file type, and recent changes. Minimal rules, maximum relevance."
version: 1.0.0
author: ciembor (agent-rules-books) + Hermes port
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [automation, cicada, intelligent, context-aware, rules, programming]
    homepage: https://github.com/ciembor/agent-rules-books
---

# Cicada Smart Rules — Context-Aware Selection

Intelligent rule selection that analyzes the full context (current file, project type, recent changes) and applies only the rules that are actually relevant. Avoids rule overload — you get just enough guidance, not all 14 books at once.

## How it works

Instead of loading all 14 book-rule skills at once (overwhelming), `$cicada-smart-rules` picks the minimal set based on context:

### 1. Analyze file type
| File pattern | Rules applied |
|---|---|
| `*.py` | clean-code, code-complete, pragmatic-programmer |
| `*.js`, `*.ts` | clean-code, clean-architecture |
| `*.cs` | clean-code, clean-architecture, domain-driven-design |
| `*.java` | clean-code, clean-architecture, domain-driven-design |
| `*.go` | clean-code, pragmatic-programmer |
| `*.rb` | clean-code, pragmatic-programmer |
| `*.md`, `*.rst`, `*.txt` | (documentation — no specific rules) |

### 2. Analyze recent git changes
| Pattern | Rules added |
|---|---|
| Many refactor commits | `$book-rules-refactoring` |
| New feature commits | `$book-rules-clean-code` |
| Bug fix commits | `$book-rules-release-it` |
| Architecture commits | `$book-rules-clean-architecture` |
| Domain commits | `$book-rules-domain-driven-design` |

### 3. Analyze project type
| Signal | Rules added |
|---|---|
| Tests exist (pytest, jest, etc.) | code-complete, pragmatic-programmer |
| No tests | working-effectively-with-legacy-code |
| Microservice architecture | clean-architecture, release-it |
| Monolith | clean-code, code-complete |
| DDD project | domain-driven-design, implementing-domain-driven-design |
| Data pipeline | designing-data-intensive-applications |

### 4. Select and apply
```
$cicada-smart-rules
# → Analyzes context
# → Selects minimal set: e.g., {clean-code, code-complete, clean-architecture}
# → Applies only these rules
```

## Benefits

- **Less noise** — only relevant rules
- **Faster** — fewer rules to scan
- **Sharper** — focused guidance
- **Adapts** — changes as the project evolves

## Example

```
User: "Write a Python class for user authentication"

$cicada-smart-rules
→ Analyzed: Python file + new class + no test + auth domain
→ Selected: clean-code, code-complete, pragmatic-programmer
→ Applied: MUST rules from selected books
```

## Conflict with full pipeline

If the user explicitly invokes a book rule (e.g., `$book-rules-refactoring`), that rule overrides smart selection. Explicit wins over automatic.
