import math
import unittest

from tool_rec.vectors import add_vectors, cosine, tf


class TfTests(unittest.TestCase):
    def test_spec_example(self):
        vec = tf("bug bug ticket")
        self.assertAlmostEqual(vec["bug"], 0.894427, places=5)
        self.assertAlmostEqual(vec["ticket"], 0.447213, places=5)

    def test_empty_text_gives_empty_vector(self):
        self.assertEqual(tf(""), {})
        self.assertEqual(tf("   !!! ..."), {})

    def test_lowercases_and_strips_punctuation(self):
        self.assertEqual(tf("Bug, BUG!"), tf("bug bug"))

    def test_vector_has_unit_length(self):
        vec = tf("create a jira ticket for the login bug")
        self.assertAlmostEqual(math.sqrt(sum(v * v for v in vec.values())), 1.0)


class CosineTests(unittest.TestCase):
    def test_identical_vectors_score_one(self):
        vec = tf("send email")
        self.assertAlmostEqual(cosine(vec, vec), 1.0)

    def test_disjoint_vectors_score_zero(self):
        self.assertEqual(cosine(tf("send email"), tf("draw chart")), 0.0)

    def test_empty_vector_scores_zero(self):
        self.assertEqual(cosine({}, tf("send email")), 0.0)
        self.assertEqual(cosine(tf("send email"), {}), 0.0)

    def test_partial_overlap_hand_computed(self):
        # a = (1/sqrt2, 1/sqrt2) over {x, y}; b = (1/sqrt2, 1/sqrt2) over {y, z}
        self.assertAlmostEqual(cosine(tf("x y"), tf("y z")), 0.5)

    def test_not_unit_length_input_is_normalized(self):
        a = {"x": 3.0, "y": 4.0}
        b = {"x": 3.0, "y": 4.0}
        self.assertAlmostEqual(cosine(a, b), 1.0)


class AddVectorsTests(unittest.TestCase):
    def test_sums_per_term(self):
        total = add_vectors({"a": 1.0, "b": 2.0}, {"b": 3.0, "c": 4.0})
        self.assertEqual(total, {"a": 1.0, "b": 5.0, "c": 4.0})

    def test_does_not_mutate_inputs(self):
        left = {"a": 1.0}
        add_vectors(left, {"a": 2.0})
        self.assertEqual(left, {"a": 1.0})


if __name__ == "__main__":
    unittest.main()
