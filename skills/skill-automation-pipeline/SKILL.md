---
name: skill-automation-pipeline
description: "Auto-load skills by detecting task type from context."
version: 1.0.0
author: Hermes Agent (derived from cicada automation pattern)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [automation, skill-routing, task-detection, context-aware]
---

# Skill Automation Pipeline

Automatically detect task type from conversation context and load the appropriate skill without manual invocation. This skill captures the pattern developed for the cicada programming bundle and is reusable for any skill library.

## Architecture

Three-layer pipeline:

```
Task Detection → Skill Selection → Skill Application
     ↓                ↓                  ↓
 cicada-automate  cicada-smart-rules  cicada-on-task
 (keyword scan)   (context analysis)  (baseline + enforce)
```

## Layer 1: Task Detection (`cicada-automate` pattern)

Scan conversation for task keywords and map to skill names:

| Keywords detected | Skill to load |
|---|---|
| refactor, clean up, smell, duplication, messy | `$book-rules-refactoring` |
| write, create, new function, implement, build | `$book-rules-clean-code` |
| architecture, design, system, layers, patterns | `$book-rules-clean-architecture` |
| domain, business logic, model, bounded context | `$book-rules-domain-driven-design` |
| legacy, old code, untested, no tests, fragile | `$book-rules-working-effectively-with-legacy-code` |
| production, deploy, bug, error, timeout, incident | `$book-rules-release-it` |
| database, schema, data, consistency, replication | `$book-rules-designing-data-intensive-applications` |
| optimize, improve, best practice, review, test | `$book-rules-the-pragmatic-programmer` |

If no specific signal found, apply baseline: `$book-rules-clean-code` + `$book-rules-the-pragmatic-programmer`.

## Layer 2: Context-Aware Selection (`cicada-smart-rules` pattern)

Instead of loading all skills at once, analyze context and pick the minimal set:

### File type analysis
| File pattern | Rules applied |
|---|---|
| `*.py` | clean-code, code-complete, pragmatic-programmer |
| `*.js`, `*.ts` | clean-code, clean-architecture |
| `*.cs`, `*.java` | clean-code, clean-architecture, domain-driven-design |
| `*.go`, `*.rb` | clean-code, pragmatic-programmer |
| `*.md`, `*.rst` | (documentation — no specific rules) |

### Git context analysis
| Pattern | Rules added |
|---|---|
| Refactor commits | `$book-rules-refactoring` |
| New feature commits | `$book-rules-clean-code` |
| Bug fix commits | `$book-rules-release-it` |
| Architecture commits | `$book-rules-clean-architecture` |

### Project type analysis
| Signal | Rules added |
|---|---|
| Tests exist | code-complete, pragmatic-programmer |
| No tests | working-effectively-with-legacy-code |
| Microservice architecture | clean-architecture, release-it |
| DDD project | domain-driven-design, implementing-domain-driven-design |
| Data pipeline | designing-data-intensive-applications |

## Layer 3: Baseline Enforcement (`cicada-on-task` pattern)

On every programming task, always apply baseline rules:

### Always-active baseline
- `$book-rules-clean-code` — readable, maintainable code
- `$book-rules-the-pragmatic-programmer` — engineering discipline

### Trigger conditions
This layer runs when:
- User starts a coding task
- `$cicada-automate` is loaded
- `$cicada-smart-rules` is the active mode

## Conflict resolution

If the user explicitly invokes a skill (e.g., `$book-rules-refactoring`), that skill overrides automatic selection. Explicit wins over automatic.

If multiple rules match, load ALL of them. Rules are complementary, not contradictory. Apply in priority order:

1. Legacy code rules (highest priority — safety first)
2. Production/reliability rules
3. Refactoring rules
4. Architecture/design rules
5. Domain rules
6. Data systems rules
7. Clean code rules (baseline)
8. Pragmatic programmer (baseline)

## Implementation pattern

```python
def detect_task_type(conversation_text):
    """Scan conversation for task keywords and return matching skill names."""
    signals = {
        "refactoring": ["refactor", "clean up", "smell", "duplication", "messy"],
        "new_code": ["write", "create", "new function", "implement", "build"],
        "architecture": ["architecture", "design", "system", "layers", "patterns"],
        "ddd": ["domain", "business logic", "model", "bounded context"],
        "legacy": ["legacy", "old code", "untested", "no tests", "fragile"],
        "production": ["production", "deploy", "bug", "error", "timeout", "incident"],
        "data": ["database", "schema", "data", "consistency", "replication"],
        "general": ["optimize", "improve", "best practice", "review", "test"],
    }
    
    detected = []
    for task_type, keywords in signals.items():
        if any(kw in conversation_text.lower() for kw in keywords):
            detected.append(task_type)
    
    return detected if detected else ["general"]


def select_rules(file_type, git_context, project_type):
    """Pick minimal set of rules based on context analysis."""
    rules = []
    
    # File type analysis
    file_rules = {
        ".py": ["clean-code", "code-complete", "pragmatic-programmer"],
        ".js": ["clean-code", "clean-architecture"],
        ".ts": ["clean-code", "clean-architecture"],
        ".cs": ["clean-code", "clean-architecture", "domain-driven-design"],
        ".java": ["clean-code", "clean-architecture", "domain-driven-design"],
        ".go": ["clean-code", "pragmatic-programmer"],
        ".rb": ["clean-code", "pragmatic-programmer"],
    }
    
    ext = os.path.splitext(file_type)[1]
    rules.extend(file_rules.get(ext, ["clean-code", "pragmatic-programmer"]))
    
    # Git context analysis
    if "refactor" in git_context:
        rules.append("refactoring")
    if "bug" in git_context:
        rules.append("release-it")
    
    # Project type analysis
    if "microservice" in project_type:
        rules.extend(["clean-architecture", "release-it"])
    if "ddd" in project_type:
        rules.extend(["domain-driven-design", "implementing-domain-driven-design"])
    
    return list(set(rules))  # deduplicate
```

## User preference: experimental scripts

**Signal captured:** User correction — "Господи, успокойся с этим скриптом Он был всего лишь тестован" ("God, calm down about this script, it was only tested")

When the user says a script is "just tested" or "only tested":
- Treat it as experimental, not production
- Do not block progress over it
- Do not over-explain or over-engineer
- Keep responses concise and actionable
- Verify the script works before offering it
- If it errors, fix it silently — don't make a production issue out of it

## Session workflow

1. **Detect**: Identify task type from conversation keywords
2. **Select**: Apply smart-rules logic to pick minimal rule set
3. **Apply**: Load and enforce selected skills
4. **Enforce**: Apply rules to the code being written
5. **Verify**: Check output against the rule checklist

## References

- `references/implementation-notes.md` — detailed implementation notes from the cicada pattern
- `references/task-detection.md` — keyword-to-skill mapping reference
- `references/context-analysis.md` — file/git/project analysis rules