import unittest
import re

def extract_between_triple_brackets(text):
    """
    Returns the content inside exactly three square brackets [[[ ... ]]].
    If multiple matches are found, returns a list of all matches.
    Returns None if no matches are found.
    """
    matches = re.findall(r'\[\[\[(.*?)\]\]\]', text)
    if not matches:
        return None
    return matches if len(matches) > 1 else matches[0]


class TestExtractBetweenTripleBrackets(unittest.TestCase):
    def test_single_match(self):
        """
        Test with one single triple-bracket match.
        The function should return a string for exactly one match.
        """
        text = "Ein einfacher Test: [[[Inhalt]]] und sonst nichts."
        expected = "Inhalt"
        self.assertEqual(extract_between_triple_brackets(text), expected)

    def test_multiple_matches(self):
        """
        Test with multiple triple-bracket matches in the same string.
        The function should return a list containing each match in order.
        """
        text = "Zwei Treffer: [[[Alpha]]]... und hier noch [[[Beta]]]."
        expected = ["Alpha", "Beta"]
        self.assertEqual(extract_between_triple_brackets(text), expected)

    def test_mixed_brackets(self):
        """
        Ensure that only exactly three brackets are matched.
        Double or single brackets should not be returned.
        """
        text = "Hier [[[Triple]]] und hier nur [[doppelt]] und [einfach]."
        expected = "Triple"
        self.assertEqual(extract_between_triple_brackets(text), expected)

    def test_nested_triple_brackets(self):
        """
        Demonstrates how the non-greedy capture will stop as soon as it finds the first closing ']]]'.
        Even if there is more bracket-like text inside.
        """
        text = "Vorsicht, hier geht es los: [[[test[[[nested]]]test]]]."
        # Because of the non-greedy capture, the match will end immediately after 'nested]]]'.
        # So we expect the capture to be: "test[[[nested"
        expected = "test[[[nested"
        self.assertEqual(extract_between_triple_brackets(text), expected)

    def test_no_triple_brackets(self):
        """
        Tests the scenario when no triple-bracket patterns exist in the text.
        The function should return None.
        """
        text = "Obwohl hier [brackets] und [[zweifach]] vorhanden sind, fehlt die dreifache Klammer."
        self.assertIsNone(extract_between_triple_brackets(text))


if __name__ == '__main__':
    unittest.main()
