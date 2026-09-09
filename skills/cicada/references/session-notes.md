# Session Notes for cicada

## ⚠️ Script Testing Policy
User explicitly told the agent: "This script was only tested" (referring to Rename-Files.ps1).
- Treat all scripts as experimental, not production.
- Always test scripts in a safe directory before running on real files.
- If the script errors, fix it before using — do not hand-wave past syntax errors.
- User hates being given scripts that don't work. Verify before offering.

## ⚠️ User Correction Signals
User corrected the agent's tone/approach with: "Господи, успокойся с этим скриптом Он был всего лишь тестован" ("God, calm down about this script, it was only tested").
- Do not over-engineer or over-explain when the user just wants a working tool.
- If the user says something is "just a test" or "only tested," treat it as experimental and do not block progress over it.
- Keep responses concise and actionable — the user prefers brief answers.
- No long explanations for simple tools.

## Created: 2026-08-31
- 14 book-rules skills imported from ciembor/agent-rules-books (full versions)
- cicada bundle skill created as index
- Rename-Files.ps1 created (PowerShell batch renamer) — experimental
- Power shell script at `C:\Users\Administrator\Documents\!LAMA\scripts\Rename-Files.ps1`
