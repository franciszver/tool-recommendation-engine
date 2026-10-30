import math
import re
from collections import Counter

Vector = dict[str, float]


def tf(text: str) -> Vector:
    """
    Convert text into an L2-normalized sparse TF vector.

    Steps:
    1. Convert text to lowercase.
    2. Tokenize into alphanumeric words.
    3. Count word frequencies.
    4. Normalize the resulting vector to unit L2 length.

    Empty text produces {}.
    """
    tokens = re.findall(r"[a-z0-9]+", text.lower())

    if not tokens:
        return {}

    counts = Counter(tokens)

    norm = math.sqrt(sum(count * count for count in counts.values()))

    return {word: count / norm for word, count in counts.items()}


def cosine(left: Vector, right: Vector) -> float:
    """Return cosine similarity. Return 0.0 when either vector is empty."""
    if len(left) > len(right):
        left, right = right, left

    dot = sum(weight * right.get(term, 0.0) for term, weight in left.items())
    left_norm = math.sqrt(sum(w * w for w in left.values()))
    right_norm = math.sqrt(sum(w * w for w in right.values()))

    if left_norm == 0.0 or right_norm == 0.0:
        return 0.0

    return dot / (left_norm * right_norm)
