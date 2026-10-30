import unittest

from tool_rec import ToolRecommendationEngine


def make_engine(max_history=5):
    engine = ToolRecommendationEngine(max_history=max_history)
    engine.add_tool("jira", "create and update jira bug ticket")
    engine.add_tool("email", "send email message to a person")
    engine.add_tool("chart", "draw a chart of sales data")
    return engine


class ConstructorTests(unittest.TestCase):
    def test_rejects_max_history_below_one(self):
        with self.assertRaises(ValueError):
            ToolRecommendationEngine(max_history=0)
        with self.assertRaises(ValueError):
            ToolRecommendationEngine(max_history=-3)


class Req1AddToolTests(unittest.TestCase):
    def test_new_tool_is_recommended_immediately(self):
        engine = ToolRecommendationEngine(max_history=3)
        engine.add_message("u", "file a bug ticket")
        self.assertEqual(engine.recommend("u", 5), [])
        engine.add_tool("jira", "bug ticket tracker")
        self.assertEqual(engine.recommend("u", 5), ["jira"])

    def test_add_tool_returns_none(self):
        self.assertIsNone(ToolRecommendationEngine(1).add_tool("t", "d"))


class Req2HistoryCapTests(unittest.TestCase):
    def test_oldest_message_is_evicted_at_cap(self):
        engine = make_engine(max_history=2)
        engine.add_message("u", "bug ticket")
        engine.add_message("u", "send email")
        self.assertEqual(set(engine.recommend("u", 5)), {"jira", "email"})
        engine.add_message("u", "send email")
        self.assertEqual(engine.recommend("u", 5), ["email"])

    def test_max_history_one_keeps_only_latest(self):
        engine = make_engine(max_history=1)
        engine.add_message("u", "bug ticket")
        engine.add_message("u", "draw chart")
        self.assertEqual(engine.recommend("u", 5), ["chart"])

    def test_below_cap_keeps_everything(self):
        engine = make_engine(max_history=10)
        for text in ("bug ticket", "send email", "draw chart"):
            engine.add_message("u", text)
        self.assertEqual(len(engine.recommend("u", 10)), 3)


class Req3CosineTests(unittest.TestCase):
    def test_scores_match_hand_computed_cosine(self):
        engine = ToolRecommendationEngine(max_history=3)
        engine.add_tool("t", "x y")
        engine.add_message("u", "y z")
        # tf("x y") and tf("y z") share one of two equal terms: cosine 0.5
        self.assertEqual([tid for tid, _ in engine.explain("u", 5)], ["t"])
        self.assertAlmostEqual(engine.explain("u", 5)[0][1], 0.5)

    def test_user_vector_is_sum_of_message_vectors(self):
        engine = ToolRecommendationEngine(max_history=3)
        engine.add_tool("t", "x")
        engine.add_message("u", "x")
        engine.add_message("u", "y")
        # user vector (1, 1) vs tool (1, 0): cosine = 1 / sqrt(2)
        self.assertAlmostEqual(engine.explain("u", 5)[0][1], 2 ** -0.5)

    def test_message_order_does_not_change_scores(self):
        a, b = make_engine(), make_engine()
        for text in ("bug ticket", "send email"):
            a.add_message("u", text)
        for text in ("send email", "bug ticket"):
            b.add_message("u", text)
        self.assertEqual(a.explain("u", 5), b.explain("u", 5))


class Req4RankingTests(unittest.TestCase):
    def test_results_are_in_descending_score_order(self):
        engine = make_engine()
        engine.add_message("u", "bug bug ticket send email")
        scores = [score for _, score in engine.explain("u", 5)]
        self.assertEqual(scores, sorted(scores, reverse=True))
        self.assertEqual(engine.recommend("u", 5)[0], "jira")

    def test_returns_at_most_k(self):
        engine = make_engine()
        engine.add_message("u", "bug ticket send email draw chart")
        self.assertEqual(len(engine.recommend("u", 2)), 2)

    def test_k_larger_than_matches_returns_all_matches(self):
        engine = make_engine()
        engine.add_message("u", "bug ticket")
        self.assertEqual(engine.recommend("u", 100), ["jira"])

    def test_recommend_returns_list_of_ids(self):
        engine = make_engine()
        engine.add_message("u", "bug ticket")
        self.assertEqual(engine.recommend("u", 1), ["jira"])


class Req5TieBreakTests(unittest.TestCase):
    def test_equal_scores_sort_by_tool_id(self):
        engine = ToolRecommendationEngine(max_history=3)
        for tool_id in ("zeta", "alpha", "mid"):
            engine.add_tool(tool_id, "same words")
        engine.add_message("u", "same words")
        self.assertEqual(engine.recommend("u", 3), ["alpha", "mid", "zeta"])

    def test_tie_break_applies_before_k_cut(self):
        engine = ToolRecommendationEngine(max_history=3)
        for tool_id in ("zeta", "alpha"):
            engine.add_tool(tool_id, "same words")
        engine.add_message("u", "same words")
        self.assertEqual(engine.recommend("u", 1), ["alpha"])


class Req6ZeroSimilarityTests(unittest.TestCase):
    def test_zero_similarity_tools_are_excluded(self):
        engine = make_engine()
        engine.add_message("u", "draw chart")
        self.assertEqual(engine.recommend("u", 10), ["chart"])

    def test_tool_with_empty_description_is_excluded(self):
        engine = make_engine()
        engine.add_tool("blank", "")
        engine.add_message("u", "draw chart")
        self.assertNotIn("blank", engine.recommend("u", 10))


class Req7EmptyResultTests(unittest.TestCase):
    def test_k_zero_and_negative(self):
        engine = make_engine()
        engine.add_message("u", "bug ticket")
        self.assertEqual(engine.recommend("u", 0), [])
        self.assertEqual(engine.recommend("u", -1), [])

    def test_unknown_user(self):
        self.assertEqual(make_engine().recommend("ghost", 3), [])

    def test_no_matching_tools(self):
        engine = make_engine()
        engine.add_message("u", "quantum entanglement")
        self.assertEqual(engine.recommend("u", 3), [])

    def test_no_tools_registered(self):
        engine = ToolRecommendationEngine(max_history=2)
        engine.add_message("u", "bug ticket")
        self.assertEqual(engine.recommend("u", 3), [])

    def test_empty_message_matches_nothing(self):
        engine = make_engine()
        engine.add_message("u", "")
        self.assertEqual(engine.recommend("u", 3), [])


class Req8ToolUpdateTests(unittest.TestCase):
    def test_update_replaces_previous_description(self):
        engine = make_engine()
        engine.add_message("u", "bug ticket")
        self.assertEqual(engine.recommend("u", 5), ["jira"])
        engine.add_tool("jira", "draw pictures")
        self.assertEqual(engine.recommend("u", 5), [])

    def test_update_does_not_duplicate_tool(self):
        engine = ToolRecommendationEngine(max_history=2)
        engine.add_tool("t", "bug")
        engine.add_tool("t", "bug ticket")
        engine.add_message("u", "bug ticket")
        self.assertEqual(engine.recommend("u", 5), ["t"])


class Req9UserIndependenceTests(unittest.TestCase):
    def test_users_do_not_share_messages(self):
        engine = make_engine()
        engine.add_message("alice", "bug ticket")
        engine.add_message("bob", "draw chart")
        self.assertEqual(engine.recommend("alice", 5), ["jira"])
        self.assertEqual(engine.recommend("bob", 5), ["chart"])

    def test_one_users_eviction_does_not_affect_another(self):
        engine = make_engine(max_history=1)
        engine.add_message("alice", "bug ticket")
        engine.add_message("bob", "send email")
        engine.add_message("bob", "draw chart")
        self.assertEqual(engine.recommend("alice", 5), ["jira"])


if __name__ == "__main__":
    unittest.main()
