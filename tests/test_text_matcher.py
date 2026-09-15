from matching.text_matcher import TextMatcher

def test_text_matcher_exact_and_similar():
    matcher = TextMatcher()

    item_lost = {
        'item_name': 'Black leather wallet Samsung',
        'description': 'Black leather wallet with small scratch near zipper college ID inside',
        'brand': 'Samsung',
        'color': 'Black',
        'distinguishing_features': 'small scratch near zipper'
    }

    item_found = {
        'item_name': 'Black leather Samsung wallet',
        'description': 'Black leather Samsung wallet small scratch near zipper',
        'brand': 'Samsung',
        'color': 'Black',
        'distinguishing_features': 'small scratch near zipper'
    }

    score = matcher.calculate_similarity(item_lost, item_found)
    assert score > 80.0, f"Expected high similarity score >80%, got {score}%"

def test_text_matcher_completely_different():
    matcher = TextMatcher()

    item_lost = {
        'item_name': 'Red Nike Backpack',
        'description': 'Red backpack containing math textbooks and water bottle',
        'brand': 'Nike',
        'color': 'Red',
        'distinguishing_features': 'math textbook'
    }

    item_found = {
        'item_name': 'Silver Apple MacBook Air',
        'description': 'Silver 13 inch laptop with Apple logo sticker',
        'brand': 'Apple',
        'color': 'Silver',
        'distinguishing_features': 'apple sticker'
    }

    score = matcher.calculate_similarity(item_lost, item_found)
    assert score < 20.0, f"Expected low similarity score <20%, got {score}%"
