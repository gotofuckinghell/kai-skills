---
name: cicada-automate
description: "Automatically apply book-rules skills based on task detection. Triggered when starting any programming task in cicada mode."
version: 1.0.0
author: ciembor (agent-rules-books) + Hermes port
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [automation, cicada, book-rules, programming, task-detection]
    homepage: https://github.com/ciembor/agent-rules-books
---

# Cicada Automate — Auto-Apply Book Rules

Detects the task type from the conversation context and automatically loads the appropriate book rule(s). No manual skill selection needed.

## Detection logic

Scan the conversation for these task signals:

### Refactoring
Keywords: refactor, refactoring, clean up, ugly, smell, duplication, messy, restructure, improve structure, code smell, rewrite, rework
→ Load: `$book-rules-refactoring` + `$book-rules-refactoring-guru`

### Writing new code
Keywords: write, create, new function, new class, implement, add, build, code, feature, develop
→ Load: `$book-rules-clean-code`

### Architecture / Design
Keywords: architecture, design, system, structure, layers, patterns, component, module, package
→ Load: `$book-rules-clean-architecture` + `$book-rules-a-philosophy-of-software-design`

### Domain modeling
Keywords: domain, business logic, model, entity, value object, bounded context, ubiquitous language, DDD
→ Load: `$book-rules-domain-driven-design` + `$book-rules-domain-driven-design-distilled`

### Legacy code
Keywords: legacy, old code, untested, no tests, messy, spaghetti, quick fix, hotfix, emergency, fragile
→ Load: `$book-rules-working-effectively-with-legacy-code`

### Production / Reliability
Keywords: production, deploy, bug, error, fix, timeout, retry, circuit breaker, outage, incident, monitoring, observability
→ Load: `$book-rules-release-it`

### Data systems
Keywords: database, schema, data, query, migration, replication, consistency, partition, transaction, streaming, event
→ Load: `$book-rules-designing-data-intensive-applications`

### General engineering
Keywords: optimize, improve, best practice, review, test, documentation, style, convention, standard
→ Load: `$book-rules-the-pragmatic-programmer` + `$book-rules-code-complete`

## Execution

When `$cicada-automate` is triggered:

1. Scan conversation for task keywords
2. Load the matching book rule(s)
3. Apply ALL rules from loaded skills as `MUST`
4. Output a brief summary: "Applied: {rule names}"
5. Enforce the rules on the code

If no specific signal found, apply baseline: `$book-rules-clean-code` + `$book-rules-the-pragmatic-programmer`

## Conflict resolution

If multiple rules match, load ALL of them. The rules are complementary, not contradictory. Apply them in priority order:

1. Legacy code rules (highest priority — safety first)
2. Production/reliability rules
3. Refactoring rules
4. Architecture/design rules
5. Domain rules
6. Data systems rules
7. Clean code rules (baseline)
8. Pragmatic programmer (baseline)
