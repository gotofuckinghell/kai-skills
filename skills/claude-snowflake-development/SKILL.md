---
name: claude-snowflake-development
description: "Converted from Claude-Skills: engineering/snowflake-development. # Snowflake Development  > **Category:** Engineering > **Domain:** Data Warehouse  ## Overview  The "
version: 1.0.0
author: borghei (Claude-Skills)
license: MIT + Commons Clause
platforms: [claude-code, hermes]
metadata:
  hermes:
    tags: [engineering, claude-skills, converted]
    source: https://github.com/borghei/Claude-Skills
    source_path: engineering/snowflake-development
---

# Snowflake Development

> **Category:** Engineering
> **Domain:** Data Warehouse

## Overview

The **Snowflake Development** skill provides tools for analyzing and optimizing Snowflake SQL queries, recommending warehouse sizing, and enforcing Snowflake-specific best practices. Helps data engineers reduce costs and improve query performance.

## Clarify First

Before analyzing or sizing, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Action** — analyze / optimize / warehouse-sizing (`--action`; selects the workflow)
- [ ] **SQL file or query** — the specific query(ies) to optimize (`--file`; the subject of the analysis)
- [ ] **Workload type & data volume** — ETL / BI / ad-hoc and the GB scale (`--workload`/`--data-volume`; drives the warehouse recommendation)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Quick Start

```bash
# Analyze a Snowflake SQL file for optimization opportunities
python scripts/snowflake_query_helper.py --file queries.sql --action analyze

# Get warehouse sizing recommendations
python scripts/snowflake_query_helper.py --action warehouse-sizing --workload "etl" --data-volume "500GB"

# Optimize a specific query
python scripts/snowflake_query_helper.py --file slow_query.sql --action optimize
```

## Tools Overview

| Tool | Purpose | Key Flags |
|------|---------|-----------|
| `snowflake_query_helper.py` | Analyze, optimize Snowflake SQL and recommend warehouse sizes | `--file`, `--action`, `--workload`, `--data-volume` |

## Workflows

### Query Performance Optimization
1. Collect slow queries from query history
2. Run analyzer to identify optimization opportunities
3. Apply recommended changes
4. Compare before/after execution plans

### Warehouse Right-Sizing
1. Identify workload type (ETL, BI, ad-hoc, etc.)
2. Run warehouse-sizing with data volume
3. Review recommendations
4. Implement multi-cluster settings if applicable

## Reference Documentation

- [Snowflake Best Practices](references/snowflake-best-practices.md) - Query patterns, warehouse management, cost optimization

## Common Patterns

### Cost Reduction
- Right-size warehouses (don't use XL for small queries)
- Set auto-suspend to 60 seconds for ad-hoc warehouses
- Use materialized views for frequently accessed aggregations
- Partition large tables with clustering keys
- Avoid SELECT * in production queries