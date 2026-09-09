# Task Detection Reference

## Keyword-to-Skill Mapping

This reference documents the task detection logic used in the skill automation pipeline. When a conversation is analyzed for task type, the following keywords map to specific skills:

### Task Type Mapping

| Task Type | Keywords | Primary Skill |
|-----------|----------|---------------|
| **Refactoring** | refactor, clean up, smell, duplication, messy | `$book-rules-refactoring` |
| **New Code** | write, create, new function, implement, build | `$book-rules-clean-code` |
| **Architecture/Design** | architecture, design, system, layers, patterns | `$book-rules-clean-architecture` |
| **Domain Modeling (DDD)** | domain, business logic, model, bounded context, ubiquitous language | `$book-rules-domain-driven-design` |
| **Legacy Code** | legacy, old code, untested, no tests, fragile, technical debt | `$book-rules-working-effectively-with-legacy-code` |
| **Production/Reliability** | production, deploy, bug, error, timeout, incident, reliability, observability | `$book-rules-release-it` |
| **Data Systems** | database, schema, data, consistency, replication, transactions, streams | `$book-rules-designing-data-intensive-applications` |
| **General Engineering** | optimize, improve, best practice, review, test, quality, standards | `$book-rules-the-pragmatic-programmer` |

### Implementation Notes

#### Keyword Matching Strategy
- **Case-insensitive matching**: All keywords are converted to lowercase before matching
- **Substring matching**: Full words are preferred, but substrings work (e.g., "refactor" matches "refactoring")
- **Multiple signals**: If multiple task types are detected, all corresponding skills are loaded

#### Order of Precedence
When multiple task types are detected, skills are applied in this priority order:

1. **Legacy code** (highest priority — safety first)
2. **Production/reliability** (critical for systems)  
3. **Refactoring** (structural improvements)
4. **Architecture/design** (system design)
5. **Domain modeling** (business logic)
6. **Data systems** (data management)
7. **Clean code** (baseline)
8. **Pragmatic programmer** (baseline)

#### Keyword Definitions

##### Refactoring Keywords
- `refactor`: Explicit refactoring request
- `clean up`: Code cleanup request
- `smell`: Code smell detection
- `duplication`: Duplicate code reduction
- `messy`: Poor code structure mentioned

##### New Code Keywords
- `write`: Create new code
- `create`: Build something new
- `new function`: Function creation
- `implement`: Implementation request
- `build`: System building

##### Architecture Keywords
- `architecture`: System architecture design
- `design`: System design
- `system`: System creation/modification
- `layers`: Layered architecture
- `patterns`: Design pattern application

##### Domain Modeling Keywords
- `domain`: Domain-specific logic
- `business logic`: Business layer implementation
- `model`: Data modeling
- `bounded context`: DDD context separation
- `ubiquitous language`: Domain language

##### Legacy Code Keywords
- `legacy`: Legacy system handling
- `old code`: Existing codebase
- `untested`: Test coverage missing
- `no tests`: Testing absence
- `fragile`: Unstable code
- `technical debt`: Debt reduction

##### Production Keywords
- `production`: Production deployment
- `deploy`: Deployment process
- `bug`: Bug fixing
- `error`: Error handling
- `timeout`: Performance issues
- `incident`: System incidents
- `reliability`: Reliability concerns
- `observability`: Monitoring/observability

##### Data Systems Keywords
- `database`: Database operations
- `schema`: Schema design/definition
- `data`: Data manipulation/processing
- `consistency`: Consistency requirements
- `replication`: Data replication
- `transactions`: Transaction handling
- `streams`: Stream processing

##### General Engineering Keywords
- `optimize`: Performance optimization
- `improve`: Code improvement
- `best practice`: Best practice application
- `review`: Code review
- `test`: Testing requirements
- `quality`: Quality assurance
- `standards`: Standards compliance

#### Example Detection Scenarios

1. **Clear refactoring request**
   ```
   Input: "Refactor this authentication module to reduce complexity"
   Detected: ["refactoring"]
   Loaded skills: `$book-rules-refactoring`
   ```

2. **New code with domain modeling**
   ```
   Input: "Implement a domain-driven design for banking system"
   Detected: ["new_code", "ddd"]
   Loaded skills: `$book-rules-clean-code`, `$book-rules-domain-driven-design`
   ```

3. **Architecture and refactoring together**
   ```
   Input: "Refactor and improve the system architecture"
   Detected: ["refactoring", "architecture"]
   Loaded skills: `$book-rules-refactoring`, `$book-rules-clean-architecture`
   ```

4. **Legacy code handling**
   ```
   Input: "The legacy codebase has no tests. Help us modernize it."
   Detected: ["legacy"]
   Loaded skills: `$book-rules-working-effectively-with-legacy-code`
   ```

5. **Production issue**
   ```
   Input: "There's a timeout in production. Fix it."
   Detected: ["production"]
   Loaded skills: `$book-rules-release-it`
   ```

6. **No specific signal (baseline)**
   ```
   Input: "Create a simple utility script"
   Detected: ["general"]
   Loaded skills: `$book-rules-clean-code`, `$book-rules-the-pragmatic-programmer`
   ```

#### Edge Cases

1. **Ambiguous signals**
   - Input: "Improve this code"
   - Detected: ["general"] (falls back to baseline)

2. **Multiple signals**
   - Input: "Refactor and optimize this algorithm"
   - Detected: ["refactoring", "general"]
   - Loaded skills: `$book-rules-refactoring`, `$book-rules-clean-code`, `$book-rules-the-pragmatic-programmer`

3. **Context-dependent**
   - Input: "Write tests for this module"
   - If git context shows "tests" commits: Only `$book-rules-clean-code`
   - If project has no tests: `$book-rules-clean-code`, `$book-rules-code-complete`, `$book-rules-pragmatic-programmer`

## Integration with Context Analysis

Task detection is the first layer of the automation pipeline. The detected task type is then combined with:

1. **File context** (for language-specific rules)
2. **Git context** (for commit-based signals)
3. **Project context** (for architecture patterns)

This multi-layered approach ensures that the right skills are loaded for the right context.

## Testing Task Detection

### Unit Tests
```python
def test_refactoring_detection():
    conversation = "Refactor this authentication module"
    detected = detect_task_type(conversation)
    assert "refactoring" in detected

def test_new_code_detection():
    conversation = "Write a Python class"
    detected = detect_task_type(conversation)
    assert "new_code" in detected

def test_architecture_detection():
    conversation = "Design a clean architecture"
    detected = detect_task_type(conversation)
    assert "architecture" in detected

def test_baseline_detection():
    conversation = "Create a simple script"
    detected = detect_task_type(conversation)
    assert detected == ["general"]
```

### Integration Tests
```python
def test_keyword_overlap():
    # Some keywords might match multiple categories
    conversation = "Clean up and optimize this code"
    detected = detect_task_type(conversation)
    assert "refactoring" in detected
    assert "general" in detected

def test_case_insensitivity():
    conversation = "REFACTOR this code"
    detected = detect_task_type(conversation)
    assert "refactoring" in detected
```

## Future Enhancements

1. **Machine learning**: Use ML models to improve keyword detection
2. **User feedback**: Learn from user corrections to refine keyword mapping
3. **Custom keywords**: Allow users to customize task detection keywords
4. **Context weights**: Assign different weights to keywords based on context
5. **Language support**: Extend to non-English conversations

## References

- `implementation-notes.md` — Background and implementation details
- `context-analysis.md` — Context-aware rule selection logic
- `cicada-pattern.md` — Original cicada bundle automation pattern