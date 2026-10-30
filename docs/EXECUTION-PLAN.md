# Claude execution plan

Francisco de Guzman prompted this plan and reviewed it before the build.
Claude Code wrote the plan and then built this repo from it. The plan is saved unchanged below the divider.
Two details changed during the build:

- `add_vectors` was removed. It became dead code after `user_vector` summed vectors in place.
- The final review pass fixed a crash in the interactive `rec` command on malformed `k` values.

The live working copy of the plan is `docs/CURR-AGENT-EFFORT.md`.

---

# Plan: ToolRecommendationEngine (local Python, in-memory)

## Context
`PRD.md` and `definedFunctions.md` (repo root, not `docs/`) define an in-memory tool recommender.
Callers register tools (id + description), add user messages (capped at `max_history` per user, FIFO),
then call `recommend(user_id, k)`. Ranking is cosine similarity between the user vector (sum of retained
per-message TF vectors) and each tool TF vector. The given `tf()` helper is the vectorizer.
Goal: working engine, tests, narrated demo (scripted + interactive), README.md and summary.md.

Decisions from the user: FIFO only (no summarization); move the two docs into `docs/`; demo has both
scripted and interactive modes; local-only light process (no remote, no GitHub issues/PRs).

## Layout
```
docs/PRD.md, docs/definedFunctions.md   (moved from root)
docs/CURR-AGENT-EFFORT.md               (live plan: scope, red-first, done-when per phase)
tool_rec/__init__.py                    exports ToolRecommendationEngine, tf
tool_rec/vectors.py                     tf() copied verbatim from definedFunctions.md; cosine(), add_vectors()
tool_rec/engine.py                      ToolRecommendationEngine
tests/test_vectors.py, tests/test_engine.py
demo.py                                 --interactive flag; --pause flag for live pacing
README.md, summary.md
```
Stdlib only (`unittest`, matching the `import unittest` in the source doc). Python version: verify with `python3 --version` first.

## Engine design (`tool_rec/engine.py`)
- `__init__(max_history)`: raise `ValueError` if `max_history < 1`. State: `_tools: dict[str, dict[str, float]]` (id -> TF vector),
  `_descriptions: dict[str, str]`, `_history: dict[str, deque[str]]` with per-message vectors stored beside the text.
- `add_tool(tool_id, description)`: store `tf(description)`; overwrite on repeat id (req 1, 8). Takes effect on the next `recommend`.
- `add_message(user_id, message)`: append; when length exceeds `max_history`, `popleft()` the oldest (deque `maxlen` does this). Users independent (req 9).
- `recommend(user_id, k)`: return `[]` if `k <= 0` or user unknown. Sum retained message vectors, compute `cosine` against each tool,
  drop score <= 0, sort by `(-score, tool_id)`, slice `[:k]`. Return `list[str]`.
- Extra read-only helper `explain(user_id, k)` returning `[(tool_id, score)]`, used by the demo to show its work. `recommend` calls it.
- cosine of two vectors is dot / (|a||b|); the user vector is a sum so it is NOT unit length, so normalize it. Guard zero norm.
- Note: `definedFunctions.md` sketch counts "hits" and returns 0 from `add_tool`. The docstrings and PRD win: score by cosine, return `None`.

## Phases (red first: failing test committed before implementation)
Branch per phase off `main` (rename `master` -> `main`; no commits exist yet). Conventional commits.
1. **P1 setup**: rename branch, move docs, write `docs/CURR-AGENT-EFFORT.md`, `.gitignore`, first commit.
2. **P2 vectors**: tests for `tf` (spec example `bug bug ticket` -> 0.894427/0.447213, empty -> `{}`, case, punctuation) and `cosine`; then `vectors.py`.
3. **P3 engine**: one test per PRD requirement 1-9 plus edge cases (below); then `engine.py`.
4. **P4 demo + docs**: `demo.py`, `README.md`, `summary.md`.
5. **Gates before final merge**: simplify -> security review -> code review -> clean-code lens -> prove. Run the code-review gates as fresh subagents
   (Haiku for mechanical checks, Sonnet for correctness), fix every finding, re-run the full suite. Two review rounds is the cap.
Implementation by Sonnet subagents per CLAUDE.md; I orchestrate and do not edit files directly. Prose follows `ste-writing` (no em dashes).

## Tests (named by requirement)
Req 1 add + update live; 2 FIFO eviction at cap (old message stops influencing results), `max_history=1`, invalid `max_history`;
3 cosine ranking with hand-computed expected scores (assertAlmostEqual); 4 descending order, exactly k results, k > tool count;
5 tie -> lexicographic ids; 6 zero-similarity excluded; 7 `k=0`, `k<0`, unknown user, no matches, no tools, empty message -> `[]`;
8 replacement drops old terms; 9 two users do not leak. Plus: repeated words weight, case/punctuation, message order independence of the sum.
Each test must be seen failing before the implementation lands.

## Demo (`demo.py`)
- Default: scripted, no input needed, prints each step with headings: register tools, add messages, show user vector, per-tool score table,
  ranked output. Scenes: basic ranking, tie-break, zero-score exclusion, tool update changes ranking, FIFO eviction changes ranking, two independent users, `k<=0`.
- `--pause`: wait for Enter between scenes (live presenting).
- `--interactive`: REPL commands `tool <id> <desc>`, `msg <user> <text>`, `rec <user> <k>`, `show <user>`, `quit`; prints scores via `explain`.
- Exit code 0; demo asserts its own expected outputs so a regression fails loudly.

## Docs
- `README.md`: install (none), run tests, run demo, API table, scoring formula, design notes, limits (in-memory, no IDF, no persistence).
- `summary.md`: one page, plain language: what it does, how to use it, example session.

## Verification
- `python3 -m unittest discover -s tests -v` all green; quote the final line.
- `python3 demo.py` exits 0 and prints each scene; scripted asserts pass. Run `--interactive` with piped input as a smoke test.
- Mutation check: break the tie-break and the FIFO cap, confirm the tests fail, then restore.
- Final report uses "I verified / I did not verify".
