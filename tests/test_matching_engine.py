from matching.score_calculator import ScoreCalculator
from matching.ranking import MatchRanker

def test_score_calculator_dynamic_redistribution():
    sc = ScoreCalculator()

    # Image available (text 40, cat 20, loc 15, time 15, img 10)
    score1, weights1 = sc.calculate_overall_score(100.0, 100.0, 100.0, 100.0, 100.0)
    assert score1 == 100.0
    assert abs(weights1['text'] - 0.40) < 0.001

    # Image missing (None) -> 10% image weight redistributed proportionally
    score2, weights2 = sc.calculate_overall_score(100.0, 100.0, 100.0, 100.0, None)
    assert score2 == 100.0
    assert 'image' not in weights2
    assert round(sum(weights2.values()), 4) == 1.0

def test_match_ranker_confidence_levels():
    mr = MatchRanker()
    assert mr.map_confidence_level(91.5) == 'HIGH'
    assert mr.map_confidence_level(72.0) == 'MEDIUM'
    assert mr.map_confidence_level(50.0) == 'LOW'
    assert mr.map_confidence_level(30.0) == 'NOT_SUITABLE'
