def add_message(
        self,
        user_id: str,
        message: str
    ) -> 
	
	{
		//initial check if FIFO needs to happen
		if (msg[id].totalMsgCount() >= self.max_history)
			{FIFO logic to that ID to keep self.max_history}
		msg[id].add[msg];
	}
		
	None:
        """
        Add a new user message.

        Maintain at most max_history messages per user.

        When the history limit is exceeded, remove
        the oldest message from the user's profile.
        """
        raise NotImplementedError

def recommend(
        self,
        user_id: str,
        k: int
    ) -> list[str]:
        //
	{
	step 1: use userId to get messages
	step 2: take messages and vectorize messages
	step 3: compare vectors to the tool vectors for similaries
	step 4: sort the "hits" of messages + tool
		tool1 . messages = 20 hits
		tool2 . messages = 15 hits
	step 5: create list and sort by similarity (dont know how to do this)
	step 6: so if # hits is the same for tools (tie) sort by lexicographically 	(alphebatical)
	return the list
	}

		"""
        Return the top-k most relevant tool IDs.

        Ranking:
            1. Descending cosine similarity.
            2. Lexicographically ascending tool ID for ties.

        Tools with zero similarity must be excluded.

        Return [] when:
            - k <= 0
            - user does not exist
            - user has no matching tools
        """
        raise NotImplementedError


# ============================================================
# CANDIDATE IMPLEMENTATION
# ============================================================

class ToolRecommendationEngine:

    def __init__(self, max_history: int):
        """
        Initialize the recommendation engine.

        Args:
            max_history:
                Maximum number of messages retained per user.

        Constraint:
            max_history >= 1
        """
	msghistory [{user_id, msg}]
	toolBucket [{id, description, vector}]
        raise NotImplementedError

    def add_tool(
        self,
        tool_id: str,
        description: str
    ) -> None:
        {
		
			IF (toolid exist)
				{update tool.description = this.description}
			Else (tool is new)
				{
					insert into memory, {id, description, tf(description)}
				}
		
		return 0;			
	}


	"""
        Register a new tool or update an existing tool.

        If tool_id already exists, its previous description
        must be replaced.

        Recommendations must immediately reflect updates.
        """
        raise NotImplementedError

"""

import math
import re
import unittest
from collections import Counter


def tf(text: str) -> dict[str, float]:
    """
    Convert text into an L2-normalized sparse TF vector.

    Steps:
    1. Convert text to lowercase.
    2. Tokenize into alphanumeric words.
    3. Count word frequencies.
    4. Normalize the resulting vector to unit L2 length.

    Example:
        tf("bug bug ticket")

        {
            "bug": 0.894427...,
            "ticket": 0.447213...
        }

    Properties:
    - Deterministic
    - No external vocabulary
    - No IDF calculation
    - Unseen words are supported
    - Empty text produces {}
    """

    tokens = re.findall(r"[a-z0-9]+", text.lower())

    if not tokens:
        return {}

    counts = Counter(tokens)

    norm = math.sqrt(
        sum(count * count for count in counts.values())
    )

    return {
        word: count / norm
        for word, count in counts.items()
    }


