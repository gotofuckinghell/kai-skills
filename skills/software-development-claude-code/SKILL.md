---
name: claude-code
description: "Meta-skill for all Claude Code utilities. Automatically applies the appropriate Claude Code tool based on task type."
version: 1.0.0
author: Claude Code Skills
license: MIT
platforms: [claude-code]
metadata:
  hermes:
    tags: [claude-code, meta-skill, automation, programming]
    homepage: https://github.com/ClaudeCode/ClaudeCode
---

# Claude Code — Meta-Skill

Automatically selects and applies the right Claude Code utility skill based on the task context.

## Automatic selection

| Task detected | Skill applied |
|---|---|
| Code needs cleanup/refactoring | `$claude-code-refactor` |
| Bug or error in code | `$claude-code-debug` |
| Performance issues | `$claude-code-optimize` |
| Writing tests or test coverage | `$claude-code-test` |
| Security concerns | `$claude-code-security` |
| Documentation needed | `$claude-code-document` |
| General coding | `$claude-code-refactor` + `$claude-code-test` |

## How it works

When `$claude-code` is invoked:
1. Analyze the conversation context
2. Detect the task type
3. Load the appropriate skill(s)
4. Apply the rules automatically

## Usage
```
$claude-code
# Automatically detects and applies the right skill
```

## Available skills
- `$claude-code-refactor` — Code refactoring and cleanup
- `$claude-code-debug` — Bug detection and fixing
- `$claude-code-optimize` — Performance optimization
- `$claude-code-test` — Test suite creation
- `$claude-code-security` — Security analysis
- `$claude-code-document` — Documentation generation
