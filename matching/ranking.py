from config import Config

class MatchRanker:
    """
    Ranks calculated candidate matches, maps confidence levels, filters by threshold,
    and supports sorting, pagination, and duplicate prevention.
    """

    @staticmethod
    def map_confidence_level(overall_score: float) -> str:
        """Maps overall match score to confidence level."""
        if overall_score >= Config.THRESHOLD_HIGH:
            return 'HIGH'
        elif overall_score >= Config.THRESHOLD_MEDIUM:
            return 'MEDIUM'
        elif overall_score >= Config.THRESHOLD_LOW:
            return 'LOW'
        else:
            return 'NOT_SUITABLE'

    def filter_and_rank_candidates(self, matches: list[dict], min_threshold: float = None) -> list[dict]:
        """
        Sorts matches in descending order by overall score and filters out NOT_SUITABLE or below min threshold.
        """
        threshold = min_threshold if min_threshold is not None else Config.THRESHOLD_LOW

        ranked = []
        for m in matches:
            score = m.get('overall_score', 0.0)
            confidence = self.map_confidence_level(score)
            m['confidence_level'] = confidence
            m['description_title'] = "Possible Match"

            if score >= threshold and confidence != 'NOT_SUITABLE':
                ranked.append(m)

        # Sort descending by overall_score
        ranked.sort(key=lambda x: x.get('overall_score', 0.0), reverse=True)
        return ranked
