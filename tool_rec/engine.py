from collections import deque

from tool_rec.vectors import Vector, cosine, tf


class ToolRecommendationEngine:
    def __init__(self, max_history: int):
        """
        Args:
            max_history: Maximum number of messages retained per user (>= 1).
        """
        if max_history < 1:
            raise ValueError("max_history must be >= 1")
        self.max_history = max_history
        self._tools: dict[str, Vector] = {}
        # Per user: retained (message, TF vector) pairs, oldest first.
        self._history: dict[str, deque[tuple[str, Vector]]] = {}

    def add_tool(self, tool_id: str, description: str) -> None:
        """Register a tool. A repeated tool_id replaces its old description."""
        self._tools[tool_id] = tf(description)

    def add_message(self, user_id: str, message: str) -> None:
        """Add a user message. The oldest message leaves when the cap is exceeded."""
        history = self._history.setdefault(user_id, deque(maxlen=self.max_history))
        history.append((message, tf(message)))

    def messages(self, user_id: str) -> list[str]:
        """Return the retained messages for a user, oldest first."""
        return [text for text, _ in self._history.get(user_id, ())]

    def user_vector(self, user_id: str) -> Vector:
        """Return the sum of the user's retained message vectors."""
        total: Vector = {}
        for _, vector in self._history.get(user_id, ()):
            for term, weight in vector.items():
                total[term] = total.get(term, 0.0) + weight
        return total

    def explain(self, user_id: str, k: int) -> list[tuple[str, float]]:
        """
        Return the top-k (tool_id, score) pairs.

        Order: descending cosine score, then ascending tool_id.
        Tools with zero similarity are excluded. Returns [] when k <= 0
        or the user has no messages.
        """
        if k <= 0:
            return []

        user_vector = self.user_vector(user_id)
        scored = [
            (tool_id, cosine(user_vector, tool_vector))
            for tool_id, tool_vector in self._tools.items()
        ]
        hits = [(tool_id, score) for tool_id, score in scored if score > 0.0]
        hits.sort(key=lambda hit: (-hit[1], hit[0]))
        return hits[:k]

    def recommend(self, user_id: str, k: int) -> list[str]:
        """Return the top-k most relevant tool IDs for the user."""
        return [tool_id for tool_id, _ in self.explain(user_id, k)]
