import difflib
from matching.preprocessing import preprocess_text

class AnswerMatcher:
    """
    Evaluates claimant verification answer against owner expected answer.
    Utilizes text normalization, sequence ratio (Levenshtein/Ratcliff-Obershelp),
    and keyword token overlap.
    Never exposes expected answers to client-side.
    """

    @staticmethod
    def calculate_answer_similarity(expected: str, claimant: str) -> float:
        """
        Calculates similarity score (0.0 to 100.0) between expected answer and claimant answer.
        """
        clean_exp = preprocess_text(expected)
        clean_cla = preprocess_text(claimant)

        if not clean_exp or not clean_cla:
            return 0.0

        if clean_exp == clean_cla:
            return 100.0

        # 1. Sequence Ratio (50% weight)
        seq_ratio = difflib.SequenceMatcher(None, clean_exp, clean_cla).ratio()

        # 2. Token Overlap Jaccard Index (50% weight)
        t_exp = set(clean_exp.split())
        t_cla = set(clean_cla.split())

        intersection = t_exp.intersection(t_cla)
        union = t_exp.union(t_cla)

        jaccard = len(intersection) / float(len(union)) if union else 0.0

        combined = (seq_ratio * 0.50) + (jaccard * 0.50)
        return round(combined * 100.0, 2)
