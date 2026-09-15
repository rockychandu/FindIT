from config import Config

class ScoreCalculator:
    """
    Calculates weighted match score across individual signal scores.
    Handles dynamic redistribution of weights when optional signals (like images) are unavailable.
    """

    def __init__(self,
                 text_w: float = None,
                 category_w: float = None,
                 location_w: float = None,
                 time_w: float = None,
                 image_w: float = None):
        self.default_weights = {
            'text': text_w or Config.MATCH_WEIGHT_TEXT,
            'category': category_w or Config.MATCH_WEIGHT_CATEGORY,
            'location': location_w or Config.MATCH_WEIGHT_LOCATION,
            'time': time_w or Config.MATCH_WEIGHT_TIME,
            'image': image_w or Config.MATCH_WEIGHT_IMAGE,
        }

    def calculate_overall_score(self,
                                text_score: float,
                                category_score: float,
                                location_score: float,
                                time_score: float,
                                image_score: float | None) -> tuple[float, dict]:
        """
        Calculates overall score (0.0 to 100.0) and returns (overall_score, effective_weights).
        Dynamically redistributes weights if image_score is None.
        """
        available_scores = {
            'text': text_score,
            'category': category_score,
            'location': location_score,
            'time': time_score,
        }

        if image_score is not None:
            available_scores['image'] = image_score

        # Calculate sum of default weights for available signals
        active_weight_sum = sum(self.default_weights[signal] for signal in available_scores)

        if active_weight_sum <= 0:
            return 0.0, self.default_weights

        # Normalize effective weights so they sum to 1.0
        effective_weights = {
            signal: self.default_weights[signal] / active_weight_sum
            for signal in available_scores
        }

        # Calculate weighted sum
        total_score = sum(available_scores[signal] * effective_weights[signal] for signal in available_scores)

        return round(total_score, 2), effective_weights
