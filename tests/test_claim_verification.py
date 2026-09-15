from verification.answer_matcher import AnswerMatcher
from verification.verification_scorer import VerificationScorer

def test_answer_matcher_fuzzy_similarity():
    am = AnswerMatcher()

    expected = "small blue sticker near the bottom"
    claimant_good = "blue small sticker at bottom"
    claimant_wrong = "red sticker on top"

    score_good = am.calculate_answer_similarity(expected, claimant_good)
    score_wrong = am.calculate_answer_similarity(expected, claimant_wrong)

    assert score_good >= 75.0, f"Expected high similarity for good answer, got {score_good}%"
    assert score_wrong < 40.0, f"Expected low similarity for wrong answer, got {score_wrong}%"

def test_verification_scorer_aggregation():
    vs = VerificationScorer()

    avg_score, confidence = vs.calculate_overall_verification([90.0, 80.0])
    assert avg_score == 85.0
    assert confidence == 'STRONG_VERIFICATION'

    avg_weak, conf_weak = vs.calculate_overall_verification([30.0, 20.0])
    assert avg_weak == 25.0
    assert conf_weak == 'WEAK_VERIFICATION'
