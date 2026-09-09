---
name: cicada-on-task
description: "Hook triggered on each programming task. Applies baseline rules and prepares context."
version: 1.0.0
author: ciembor (agent-rules-books) + Hermes port
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [automation, cicada, hook, programming, task]
    homepage: https://github.com/ciembor/agent-rules-books
---

# Cicada On-Task — Automatic Hook

This skill is triggered automatically at the start of every programming task in a cicada session. It applies baseline book rules and prepares the context so that `$cicada-automate` can layer domain-specific rules on top.

## What it does

On every programming task (new file, function, class, bug fix, refactor):

1. **Apply baseline rules** (always active):
   - `$book-rules-clean-code` — write readable, maintainable code
   - `$book-rules-the-pragmatic-programmer` — engineering discipline

2. **Signal `$cicada-automate`** that a task has started, triggering the auto-detection pipeline.

3. **Report** which rules are active.

## Baseline rules (always applied)

### Clean Code (MUST)
- Code is written for humans, not just machines.
- Names must reveal intent.
- Functions do one thing.
- Avoid duplication, comments to compensate for bad naming, boolean flags.
- Tests are production-quality code.
- Refactor in small, safe steps.

### Pragmatic Programmer (MUST)
- DRY at the knowledge level, not code level.
- Orthogonality: decouple components.
- Automation: automate everything repetitive.
- Fast feedback: test early, test often.
- Adaptability: prototype, then refine.
- Responsibility: own your code from requirements to deployment.

## Trigger conditions

This skill runs when:
- User starts a coding task ("write a function...", "fix this bug...", "refactor...")
- `$cicada-automate` is loaded
- `$cicada-smart-rules` is the active mode

## Output

After loading, output:
```
Cicada baseline active:
  - book-rules-clean-code (MUST)
  - book-rules-the-pragmatic-programmer (MUST)

$cicada-automate detected task type: {detected type}
Additional rules loaded: {rule names}
```
