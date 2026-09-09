---
name: cicada
description: "Programming session bundle: 14 book-rules skills + automated skill application pipeline."
version: 1.2.0
author: ciembor (agent-rules-books) + Hermes port
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [programming, coding, refactoring, book-rules, cicada, automation]
    homepage: https://github.com/ciembor/agent-rules-books
---

# Cicada — Programming Session Bundle

A self-contained programming session toolkit. Contains all 14 book-rule skills from `agent-rules-books` plus an automated skill application pipeline.

## What's included

### Book rules (14 skills, full versions)
- `$book-rules-clean-code` — everyday coding, naming, functions, classes, tests, review
- `$book-rules-refactoring` — safe restructuring, code smells, incremental changes
- `$book-rules-refactoring-guru` — diagnose smells → choose treatment → preserve behavior
- `$book-rules-the-pragmatic-programmer` — general engineering, DRY, automation, feedback
- `$book-rules-a-philosophy-of-software-design` — module design, interfaces, complexity
- `$book-rules-clean-architecture` — system boundaries, dependency rule
- `$book-rules-domain-driven-design` — domain modeling, ubiquitous language
- `$book-rules-domain-driven-design-distilled` — pragmatic DDD
- `$book-rules-implementing-domain-driven-design` — real DDD: aggregates, events
- `$book-rules-patterns-of-enterprise-application-architecture` — layers, repository, UoW
- `$book-rules-designing-data-intensive-applications` — reliability, scalability, consistency
- `$book-rules-code-complete` — disciplined construction, defensive coding
- `$book-rules-release-it` — production survival, timeouts, retries, circuit breakers
- `$book-rules-working-effectively-with-legacy-code` — characterization tests, seams

### Automation pipeline
- **`$cicada-automate`** — auto-apply skills based on task detection
- **`$cicada-on-task`** — hook triggered on each programming task
- **`$cicada-smart-rules`** — intelligent rule selection based on context

## Automated skill application

### `$cicada-automate`
Automatically applies the appropriate book rules based on the task detected in the conversation. No manual invocation needed.

```
$cicada-automate
# → Detects task type → loads matching book rules → applies them
```

### Task detection rules
| Task keywords | Auto-loaded rule |
|---|---|
| refactor, clean up, smell, ugly code | `$book-rules-refactoring` |
| write code, new function, class, test | `$book-rules-clean-code` |
| architecture, design, system, layers | `$book-rules-clean-architecture` |
| domain model, business logic, bounded context | `$book-rules-domain-driven-design` |
| legacy, old code, messy, no tests | `$book-rules-working-effectively-with-legacy-code` |
| production, bug, deploy, timeout, error | `$book-rules-release-it` |
| data, database, schema, flow, consistency | `$book-rules-designing-data-intensive-applications` |
| general, improve, optimize, best practices | `$book-rules-the-pragmatic-programmer` |
```

### `$cicada-on-task`
Hook that runs automatically when a programming task starts. Applies baseline rules and prepares context.

```
$cicada-on-task
# → Loads: clean-code + pragmatic-programmer (baseline)
# → Waits for task-specific signal to add domain rules
```

### `$cicada-smart-rules`
Intelligent rule selection that considers the full context (current file, recent changes, project type).

```
$cicada-smart-rules
# → Analyzes: file type, recent commits, project structure
# → Selects: minimal set of applicable rules
# → Applies: only the needed rules
```

## How the automation works

The system uses a **context-aware pipeline**:

1. **Detect**: Identify task type from conversation keywords and file context
2. **Select**: Pick the most relevant book rule(s)
3. **Apply**: Load and activate the selected rules
4. **Enforce**: Apply rules to the code being written
5. **Verify**: Check output against the rule checklist

No manual skill loading needed for routine tasks. The system automatically applies the right book rules when it detects a programming task.

## Rules are applied automatically

When this skill is active (i.e., the cicada pipeline is running), ALL rules are treated as `MUST` (unless otherwise stated). `Prefer` = `SHOULD`, `Do not/Avoid/Never` = `MUST NOT`. The rules are always active when working on code.
