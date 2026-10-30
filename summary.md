# Summary

## What it does

The engine suggests which tools an AI assistant should offer a user.
You register tools with a name and a plain-language description.
You send it the messages a user writes.
You then ask for the top few tools for that user, and it answers best first.

## How it decides

- Each description and each message becomes a list of word counts.
- The engine adds up the lists for the user's recent messages.
- It compares that total with each tool's list. More shared words give a higher score.
- Tools that share no words with the user are left out.
- If two tools score the same, the one whose ID comes first alphabetically wins.

## Memory limit

The engine keeps only the last `max_history` messages for each user.
When a new message arrives over the limit, the oldest message is forgotten.
Each user is tracked separately.

## How to use it

```python
from tool_rec import ToolRecommendationEngine

engine = ToolRecommendationEngine(max_history=3)
engine.add_tool("jira", "create jira bug ticket")
engine.add_tool("email", "send email message")

engine.add_message("alice", "file bug ticket")
engine.recommend("alice", 2)      # ['jira']

engine.add_tool("jira", "draw pictures")   # replaces the old description
engine.recommend("alice", 2)      # []
```

## Try it

```
python3 -m unittest discover -s tests -v   # run the tests
python3 demo.py                            # watch a scripted demo
python3 demo.py --interactive              # type your own tools and messages
```

The scripted demo has seven scenes: ranking, tie-break, zero-score exclusion,
tool update, message eviction, user independence, and edge cases.
Each scene prints the scores and checks the result.
A final line, "All demo checks passed.", confirms the run.

See `README.md` for the full API and known limits.
