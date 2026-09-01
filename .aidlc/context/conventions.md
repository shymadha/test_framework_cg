# Aster FW — Conventions

## File Organization
- Run from CWD: aster_fw
- Primary entrypoints: framework/ui/ui_agentic_ai.py (LLM flow), framework/ui/ui.py (manual flow)
- Tests: framework/tests/<domain> with classes ending in `Test` (excluding BaseTest)
- Logs: logs/<timestamp>/framework.log
- Reports: reports/*.md
- Vector store: chroma_db/
- Security tests: tests/security/

## Naming
- Test classes end with `Test`
- Python modules and packages use lowercase with underscores
- ADR files under .aidlc/context/decisions use `ADR-YYYYMMDD-<slug>.md`

## Testing
- Framework: pytest
- Discovery: files *.py; classes ending with `Test`
- Execution: via Manual UI or orchestration engine
- Coverage: not enforced; recommend adding critical-path tests for UI, executor, and device adapters

## Error Handling
- Propagate exceptions with contextual logging to logs/<timestamp>/framework.log
- Prefer explicit checks for environment (.env) and testbed.json; fail fast with actionable messages

## Git Conventions
- Ignore logs/, reports/, chroma_db/, .env, caches
- Branch naming: feature/<slug>, bugfix/<slug>, chore/<slug>
- Commits: imperative mood; reference Jira ticket if used
- PRs: concise summary, test evidence (logs/report excerpts), and risk notes
