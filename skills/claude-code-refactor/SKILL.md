---
name: claude-code-refactor
description: "Refactoring assistant for Claude Code. Automatically refactors code following best practices, reduces complexity, and maintains behavior."
version: 1.0.0
author: Claude Code Skills
license: MIT
platforms: [claude-code]
metadata:
  hermes:
    tags: [refactoring, claude-code, code-quality, automation]
    homepage: https://github.com/ClaudeCode/ClaudeCode
---

# Claude Code Refactor Assistant

This skill automates code refactoring for Claude Code, focusing on clean, maintainable code while preserving functionality.

## What it does
- Analyzes code for refactoring opportunities
- Identifies complex functions, duplicated code, and poor naming
- Applies systematic refactoring steps
- Maintains all existing behavior
- Provides detailed change reports

## Refactoring rules applied
- Functions smaller than 15 lines
- Descriptive naming conventions
- Single responsibility principle
- Reduced nesting levels
- Eliminated code duplication
- Improved error handling

## Usage
Use when Claude Code generates code that needs cleanup:
```
$claude-code-refactor
<apply to selected code>
```
