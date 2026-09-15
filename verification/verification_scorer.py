from config import Config

class VerificationScorer:
    """
    Aggregates multi-question answer scores into an overall verification score and confidence level.
    """

    @staticmethod
    def map_verification_confidence(score: float) -> str:
        """Maps overall verification score to confidence level."""
        if score >= Config.VERIFICATION_STRONG:
            return 'STRONG_VERIFICATION'
        elif score >= Config.VERIFICATION_PARTIAL:
            return 'PARTIAL_VERIFICATION'
        else:
            return 'WEAK_VERIFICATION'

    def calculate_overall_verification(self, answer_scores: list[float]) -> tuple[float, str]:
        """
        Calculates average verification score (0.0 to 100.0) and confidence.
        """
        if not answer_scores:
            return 0.0, 'WEAK_VERIFICATION'

        avg_score = round(sum(answer_scores) / float(len(answer_scores)), 2)
        confidence = self.map_verification_confidence(avg_score)
        return avg_score, confidence
