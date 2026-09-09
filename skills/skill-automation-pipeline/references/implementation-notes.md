# Implementation Notes for Skill Automation Pipeline

## Background

This pipeline implements the automation pattern developed in the cicada programming bundle. The goal was to automatically detect task types and load the appropriate book rules without manual invocation, reducing cognitive load and improving workflow efficiency.

## Technical Approach

### Three-Layer Architecture

1. **Task Detection Layer** (`cicada-automate` pattern)
   - Keyword-based scanning of conversation context
   - Mapping detected tasks to skill names
   - Baseline application when no specific signal found

2. **Context-Aware Selection Layer** (`cicada-smart-rules` pattern)
   - File type analysis (extracted from file extensions)
   - Git context analysis (commits, branches, changes)
   - Project type analysis (architecture, patterns, dependencies)

3. **Baseline Enforcement Layer** (`cicada-on-task` pattern)
   - Always apply baseline rules for safe starting point
   - Signal when auto-detection pipeline is running
   - Trigger conditions based on task initiation

## Key Design Decisions

### Task Keyword Mapping
Based on user feedback and observed patterns, the following task types were identified:

- **Refactoring**: refactor, clean up, smell, duplication, messy
- **New Code**: write, create, new function, implement, build
- **Architecture/Design**: architecture, design, system, layers, patterns
- **Domain Modeling**: domain, business logic, model, bounded context
- **Legacy Code**: legacy, old code, untested, no tests, fragile
- **Production/Reliability**: production, deploy, bug, error, timeout, incident
- **Data Systems**: database, schema, data, consistency, replication
- **General Engineering**: optimize, improve, best practice, review, test

### Rule Selection Logic

**File Type Analysis**
- Python files (`*.py`): clean-code, code-complete, pragmatic-programmer
- JavaScript/TypeScript (`*.js`, `*.ts`): clean-code, clean-architecture
- Java/C# (`*.java`, `*.cs`): clean-code, clean-architecture, domain-driven-design
- Go/Ruby (`*.go`, `*.rb`): clean-code, pragmatic-programmer

**Git Context Analysis**
- Refactor commits → `$book-rules-refactoring`
- Bug fix commits → `$book-rules-release-it`
- Architecture commits → `$book-rules-clean-architecture`

**Project Type Analysis**
- Microservice architecture → clean-architecture, release-it
- DDD project → domain-driven-design, implementing-domain-driven-design
- Data pipeline → designing-data-intensive-applications

## Implementation Details

### Detection Function
```python
def detect_task_type(conversation_text):
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
```

### Rule Selection Function
```python
def select_rules(file_type, git_context, project_type):
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
    
    return list(set(rules))
```

## Testing and Validation

### Test Cases

1. **Clear refactoring signal**
   - Input: "Please refactor this authentication module"
   - Expected: `$book-rules-refactoring`

2. **New code signal**
   - Input: "Write a Python class for user authentication"
   - Expected: `$book-rules-clean-code`

3. **Architecture signal**
   - Input: "Design a clean architecture for this system"
   - Expected: `$book-rules-clean-architecture`

4. **Domain modeling signal**
   - Input: "Implement domain-driven design for banking system"
   - Expected: `$book-rules-domain-driven-design`

5. **No specific signal (baseline)**
   - Input: "Create a simple utility script"
   - Expected: `$book-rules-clean-code` + `$book-rules-the-pragmatic-programmer`

### Edge Cases

1. **Multiple signals**
   - Input: "Refactor and improve the architecture"
   - Expected: Both `$book-rules-refactoring` and `$book-rules-clean-architecture`

2. **Ambiguous signal**
   - Input: "Optimize this algorithm"
   - Expected: `$book-rules-the-pragmatic-programmer` (general)

3. **File-specific context**
   - File: `auth.py`, Input: "Add authentication functionality"
   - Expected: `$book-rules-clean-code`, `$book-rules-code-complete`, `$book-rules-pragmatic-programmer`

## Integration with cicada Pattern

This pipeline was extracted from the cicada programming bundle, which contains:

- `$book-rules-clean-code` through `$book-rules-working-effectively-with-legacy-code`
- `$cicada-automate` — auto-detection and skill selection
- `$cicada-smart-rules` — context-aware rule selection
- `$cicada-on-task` — baseline enforcement

## Best Practices

1. **Avoid over-engineering** — Keep rules minimal and focused
2. **Maintain baseline** — Always have safe starting rules
3. **Context awareness** — Use file, git, and project context
4. **Explicit rules win** — User's explicit skill calls override auto-detection
5. **Completeness over scope** — Load all matching rules, don't limit arbitrarily

## Future Enhancements

1. **Machine learning** — Improve keyword detection with ML models
2. **User feedback loop** — Learn from user's corrections and rule overrides
3. **Performance optimization** — Cache rule selection results
4. **Customizable rules** — Allow users to customize task detection keywords
5. **Multi-language support** — Extend to non-English conversations