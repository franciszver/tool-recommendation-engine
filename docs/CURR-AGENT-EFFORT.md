# Current effort: ToolRecommendationEngine

Source specs: `docs/PRD.md`, `docs/definedFunctions.md`. Python 3.13, stdlib only, `unittest`.
Decisions: FIFO eviction only (no summary); scripted and interactive demo; local-only process.

## P1 Setup
- Scope: branch `main`, docs moved to `docs/`, this plan, `.gitignore`.
- Red-first: none (no logic).
- Done when: first commit on `main`.

## P2 Vectors (`tool_rec/vectors.py`)
- Scope: `tf` (verbatim from spec), `cosine`.
- Red-first: `tests/test_vectors.py` fails with ImportError before implementation.
- Done when: spec example `tf("bug bug ticket")` gives 0.894427 / 0.447213; empty text gives `{}`; cosine of orthogonal vectors is 0; zero vector is safe.

## P3 Engine (`tool_rec/engine.py`)
- Scope: `ToolRecommendationEngine` with `add_tool`, `add_message`, `recommend`, `explain`.
- Red-first: `tests/test_engine.py`, one test per PRD requirement 1-9 plus edge cases, failing before implementation.
- Done when: all tests pass; mutation checks (break tie-break, break FIFO cap) make tests fail.

## P4 Demo and docs
- Scope: `demo.py` (scripted, `--pause`, `--interactive`), `README.md`, `summary.md`.
- Red-first: a test that runs `demo.py` as a subprocess and expects exit code 0 and key output lines.
- Done when: demo runs clean in all three modes; docs match the real commands.

## P5 Gates
- simplify, security review, code review, clean-code lens, prove. Fix every finding. Cap: two review rounds.
