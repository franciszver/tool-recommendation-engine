#!/usr/bin/env python3
"""Live demo of the ToolRecommendationEngine.

    python3 demo.py                 scripted run, no input needed
    python3 demo.py --pause         scripted run, press Enter between scenes
    python3 demo.py --interactive   type tools and messages yourself
"""
import argparse
import sys

from tool_rec import ToolRecommendationEngine

TOOLS = {
    "jira": "create jira bug ticket",
    "email": "send email message",
    "chart": "draw sales chart",
    "calendar": "schedule meeting calendar",
}


def say(text=""):
    print(text)


def scene(number, title, pause):
    if pause:
        try:
            input("\n[press Enter for the next scene] ")
        except EOFError:
            pass
    say(f"\n{'=' * 64}\nScene {number}: {title}\n{'=' * 64}")


def show_state(engine, user_id, k=10):
    """Print the user's messages, user vector, and the scored ranking."""
    say(f"messages kept for {user_id}: {engine.messages(user_id)}")
    vector = engine.user_vector(user_id)
    terms = ", ".join(f"{t}={w:.4f}" for t, w in sorted(vector.items()))
    say(f"user vector: {{{terms}}}")
    ranking = engine.explain(user_id, k)
    if not ranking:
        say("ranking: (empty)")
    for rank, (tool_id, score) in enumerate(ranking, start=1):
        say(f"  {rank}. {tool_id:<10} score={score:.4f}")


def check(actual, expected):
    assert actual == expected, f"expected {expected}, got {actual}"
    say(f"CHECK ok: recommend -> {actual}")


def new_engine(max_history, tools=TOOLS):
    engine = ToolRecommendationEngine(max_history=max_history)
    for tool_id, description in tools.items():
        engine.add_tool(tool_id, description)
    return engine


def run_scripted(pause):
    scene(1, "Rank tools by cosine similarity", pause)
    engine = new_engine(max_history=5)
    for tool_id, description in TOOLS.items():
        say(f"add_tool({tool_id!r}, {description!r})")
    engine.add_message("alice", "file bug ticket")
    engine.add_message("alice", "send email bug")
    say('add_message("alice", ...) x2')
    show_state(engine, "alice")
    check(engine.recommend("alice", 2), ["jira", "email"])

    scene(2, "Ties break by tool ID, alphabetically", pause)
    engine = new_engine(5, {"zeta": "same words", "alpha": "same words", "mid": "same words"})
    engine.add_message("bob", "same words")
    show_state(engine, "bob")
    check(engine.recommend("bob", 3), ["alpha", "mid", "zeta"])
    check(engine.recommend("bob", 1), ["alpha"])

    scene(3, "Tools with zero similarity are excluded", pause)
    engine = new_engine(5)
    engine.add_message("carol", "draw chart")
    show_state(engine, "carol")
    check(engine.recommend("carol", 4), ["chart"])

    scene(4, "Updating a tool replaces its old description", pause)
    engine = new_engine(5)
    engine.add_message("dave", "bug ticket")
    check(engine.recommend("dave", 3), ["jira"])
    say('add_tool("jira", "draw pictures")  # same ID, new description')
    engine.add_tool("jira", "draw pictures")
    show_state(engine, "dave")
    check(engine.recommend("dave", 3), [])

    scene(5, "max_history=2 drops the oldest message (FIFO)", pause)
    engine = new_engine(max_history=2)
    engine.add_message("erin", "file bug ticket")
    engine.add_message("erin", "send email")
    say("after 2 messages:")
    show_state(engine, "erin")
    check(engine.recommend("erin", 3), ["email", "jira"])
    engine.add_message("erin", "send another email")
    say("after a 3rd message, the bug ticket message is gone:")
    show_state(engine, "erin")
    check(engine.recommend("erin", 3), ["email"])

    scene(6, "User profiles stay independent", pause)
    engine = new_engine(5)
    engine.add_message("frank", "bug ticket")
    engine.add_message("grace", "schedule meeting")
    say("frank:")
    show_state(engine, "frank")
    say("grace:")
    show_state(engine, "grace")
    check(engine.recommend("frank", 3), ["jira"])
    check(engine.recommend("grace", 3), ["calendar"])

    scene(7, "Edge cases return []", pause)
    engine = new_engine(5)
    engine.add_message("heidi", "bug ticket")
    say("k=0:")
    check(engine.recommend("heidi", 0), [])
    say("k=-1:")
    check(engine.recommend("heidi", -1), [])
    say("unknown user:")
    check(engine.recommend("nobody", 3), [])
    say("no matching tool:")
    engine.add_message("ivan", "quantum entanglement")
    check(engine.recommend("ivan", 3), [])

    say("\nAll demo checks passed.")


HELP = """commands:
  tool <id> <description>   register or replace a tool
  msg <user> <text>         add a user message
  rec <user> <k>            top-k tool IDs
  show <user>               messages, user vector, scored ranking
  quit                      leave"""


def run_interactive(max_history):
    engine = ToolRecommendationEngine(max_history=max_history)
    say(f"Interactive mode (max_history={max_history}).\n{HELP}")
    while True:
        try:
            line = input("> ")
        except EOFError:
            return
        parts = line.strip().split(maxsplit=2)
        if not parts:
            continue
        command = parts[0].lower()
        if command == "quit":
            return
        elif command == "tool" and len(parts) == 3:
            engine.add_tool(parts[1], parts[2])
            say(f"tool {parts[1]} saved")
        elif command == "msg" and len(parts) == 3:
            engine.add_message(parts[1], parts[2])
            say(f"message saved for {parts[1]}")
        elif command == "rec" and len(parts) == 3 and parts[2].lstrip("-").isdigit():
            ranking = engine.explain(parts[1], int(parts[2]))
            shown = ", ".join(f"{t} ({s:.4f})" for t, s in ranking) or "[]"
            say(f"recommendations for {parts[1]}: {shown}")
        elif command == "show" and len(parts) == 2:
            show_state(engine, parts[1])
        else:
            say(f"Unknown command or wrong arguments: {line!r}\n{HELP}")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--pause", action="store_true", help="wait for Enter between scenes")
    parser.add_argument("--interactive", action="store_true", help="type your own tools and messages")
    parser.add_argument("--max-history", type=int, default=5, help="interactive mode history cap")
    args = parser.parse_args(argv)

    if args.interactive:
        run_interactive(args.max_history)
    else:
        run_scripted(args.pause)
    return 0


if __name__ == "__main__":
    sys.exit(main())
