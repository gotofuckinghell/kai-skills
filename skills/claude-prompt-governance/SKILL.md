---
name: claude-prompt-governance
description: "Converted from Claude-Skills: engineering/prompt-governance. # Prompt Governance  > **Category:** Engineering > **Domain:** AI Governance  ## Overview  The **Pro"
version: 1.0.0
author: borghei (Claude-Skills)
license: MIT + Commons Clause
platforms: [claude-code, hermes]
metadata:
  hermes:
    tags: [engineering, claude-skills, converted]
    source: https://github.com/borghei/Claude-Skills
    source_path: engineering/prompt-governance
---

# Prompt Governance

> **Category:** Engineering
> **Domain:** AI Governance

## Overview

The **Prompt Governance** skill provides tools for auditing prompts for security vulnerabilities, bias, and safety issues, plus managing a versioned catalog of approved prompts. Essential for organizations deploying LLM-based applications at scale.

## Clarify First

Before auditing or cataloging, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Target prompt(s)** — the exact file/text to audit or the catalog dir to manage (the subject of every check)
- [ ] **Task: audit vs catalog management** — selects `prompt_auditor.py` vs `prompt_catalog_manager.py` and the whole workflow
- [ ] **Check focus** — injection / bias / safety (sets which auditor checks run and the pass/fail bar)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Quick Start

```bash
# Audit a prompt for security and safety issues
python scripts/prompt_auditor.py --file system_prompt.txt

# Audit with specific focus
python scripts/prompt_auditor.py --text "You are a helpful assistant..." --checks injection,bias,safety

# Initialize a prompt catalog
python scripts/prompt_catalog_manager.py --init --catalog-dir ./prompts

# Add a prompt to the catalog
python scripts/prompt_catalog_manager.py --add --name "customer-support-v1" --file prompt.txt --catalog-dir ./prompts

# List all prompts in catalog
python scripts/prompt_catalog_manager.py --list --catalog-dir ./prompts
```

## Tools Overview

| Tool | Purpose | Key Flags |
|------|---------|-----------|
| `prompt_auditor.py` | Audit prompts for injection, bias, and safety | `--file`, `--text`, `--checks`, `--format` |
| `prompt_catalog_manager.py` | Manage versioned prompt catalog | `--init`, `--add`, `--list`, `--diff`, `--catalog-dir` |

## Workflows

### Prompt Review Process
1. Author writes or modifies a prompt
2. Run `prompt_auditor.py` for automated checks
3. Review findings and address critical issues
4. Add approved prompt to catalog with `prompt_catalog_manager.py`
5. Deploy from catalog (never from ad-hoc sources)

### Prompt Versioning
1. Store all prompts in catalog with semantic versioning
2. Use `--diff` to compare versions before promotion
3. Maintain audit trail of all prompt changes
4. Roll back to previous versions when issues detected

## Reference Documentation

- [Prompt Governance Framework](references/prompt-governance-framework.md) - Policies, review processes, and compliance requirements

## Common Patterns

### Prompt Lifecycle
Draft -> Audit -> Review -> Approve -> Deploy -> Monitor -> Retire

### Governance Checklist
- No injection vulnerabilities
- No harmful content generation potential
- Appropriate bias mitigation
- Clear scope boundaries
- Output format constraints
- Error handling instructions