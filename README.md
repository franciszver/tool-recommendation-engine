# ToolRecommendationEngine

> **Built with Claude Code.** Claude Code planned and built this repo from `docs/PRD.md`
> and `docs/definedFunctions.md`. Francisco de Guzman prompted the plan and reviewed it
> before the build. Read the approved plan in
> [`docs/EXECUTION-PLAN.md`](docs/EXECUTION-PLAN.md). The live task list is
> [`docs/CURR-AGENT-EFFORT.md`](docs/CURR-AGENT-EFFORT.md).

An in-memory engine that recommends tools to a user. It reads the user's recent
messages and ranks registered tools by cosine similarity of term-frequency vectors.

Python 3.13 or later. No third-party packages.

## Quick start

```python
from tool_rec import ToolRecommendationEngine

engine = ToolRecommendationEngine(max_history=5)
engine.add_tool("jira", "create jira bug ticket")
engine.add_tool("email", "send email message")

engine.add_message("alice", "file bug ticket")
engine.recommend("alice", 2)   # ['jira']
engine.explain("alice", 2)     # [('jira', 0.5774)]
```

## Commands

| Task | Command |
|---|---|
| Run all tests | `python3 -m unittest discover -s tests -v` |
| Run the scripted demo | `python3 demo.py` |
| Run the demo with a pause between scenes | `python3 demo.py --pause` |
| Type your own tools and messages | `python3 demo.py --interactive` |

Interactive commands: `tool <id> <description>`, `msg <user> <text>`,
`rec <user> <k>`, `show <user>`, `quit`.

## API

| Method | Behavior |
|---|---|
| `ToolRecommendationEngine(max_history)` | Create an engine. Raises `ValueError` if `max_history < 1`. |
| `add_tool(tool_id, description)` | Register a tool. A repeated `tool_id` replaces the old description. |
| `add_message(user_id, message)` | Add a message. The oldest message leaves when the user exceeds `max_history`. |
| `recommend(user_id, k)` | Return up to `k` tool IDs, best first. |
| `explain(user_id, k)` | Same ranking as `recommend`, as `(tool_id, score)` pairs. |
| `user_vector(user_id)` | Return the sum of the user's retained message vectors. |
| `messages(user_id)` | Return the user's retained messages, oldest first. |

## How scoring works

1. `tf(text)` lowercases the text, splits it into alphanumeric words, counts them, and scales the counts to unit length.
2. The user vector is the sum of the TF vectors of the retained messages.
3. `score = cosine(user_vector, tool_vector)`.
4. The engine drops tools with a score of 0, sorts by descending score, then by ascending tool ID, and keeps the first `k`.

`recommend` returns `[]` when `k <= 0`, the user is unknown, or no tool matches.
Each user has an independent message history.

## Limits

- All data lives in memory. A restart clears it.
- There is no IDF weighting and no stop-word list. Shared common words such as "a" or "the" raise a score.
  Write tool descriptions with content words for the best results.
- Old messages are dropped, not summarized.

## License

MIT. See `LICENSE`. A short plain-language overview is in `summary.md`.

## Layout

```
tool_rec/vectors.py   tf, cosine
tool_rec/engine.py    ToolRecommendationEngine
tests/                unit tests and demo tests
demo.py               scripted and interactive demo
docs/                 PRD, function spec, working plan
```
