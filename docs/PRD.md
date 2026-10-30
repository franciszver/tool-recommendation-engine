Problem: Real-Time Tool Recommendation Engine.

You are building a recommendation engine for an AI assistant.

The engine continuously receives:
1. Tool registrations containing natural-language descriptions.
2. User messages describing tasks and intentions.

When recommend(user_id, k) is called, return the top-k
most relevant tools for that user.

**K is total recommend to return

AddTool(Tool: this)
Okay so you can register tools based on tool name + natural language description

User messaging + context window (messages, in memory)

A Term Frequency (TF) helper is provided. (vectorizes the tool input)

REQUIREMENTS
------------
1. Store and update tool descriptions in real time. (A user can input a tool)
2. Maintain at most max_history messages per user. (A user max messages + summary+compaction)
3. Rank tools using cosine similarity. (Vectorization matching)
4. Return the top-k tool IDs in descending score order. (recommend(k) -> K.ids in descending score order
5. Break score ties lexicographically by tool ID. (
6. Exclude tools with zero similarity.
7. Return [] when k <= 0 or no matching tools exist.
8. Updating a tool replaces its previous description.
9. User profiles must remain independent.
SCORING
-------
Each tool description and user message is converted
into a sparse TF vector.

User vector = Sum of retained message vectors.

Score(user, tool) = cosine(user_vector, tool_vector)
