from datetime import date, time
from matching.category_matcher import CategoryMatcher
from matching.location_matcher import LocationMatcher
from matching.time_matcher import TimeMatcher

def test_category_matcher():
    cm = CategoryMatcher()
    assert cm.calculate_similarity(1, 1) == 100.0
    assert cm.calculate_similarity(1, 2, lost_cat_name="Wallet", found_cat_name="Purse") == 75.0
    assert cm.calculate_similarity(1, 2, lost_cat_name="Wallet", found_cat_name="Water Bottle") == 0.0

def test_location_matcher_haversine_and_text():
    lm = LocationMatcher()

    # Geo distance close (~30 meters)
    lost_item = {'latitude': 12.9716, 'longitude': 77.5946, 'location_text': 'Library 2nd floor'}
    found_item = {'latitude': 12.9718, 'longitude': 77.5948, 'location_text': 'Library 2nd floor room 204'}

    score = lm.calculate_similarity(lost_item, found_item)
    assert score >= 85.0

    # Text location matching
    text_score = lm.score_from_text("Lab 3 Computer Science Block", "CS Building Lab 3")
    assert text_score >= 60.0

def test_time_matcher_proximity():
    tm = TimeMatcher()

    # Lost 2PM, Found 4PM same day
    lost_item = {'lost_date': date(2026, 9, 14), 'lost_time': time(14, 0)}
    found_item = {'found_date': date(2026, 9, 14), 'found_time': time(16, 0)}

    score = tm.calculate_similarity(lost_item, found_item)
    assert score == 100.0

    # Found 2 days later
    found_later = {'found_date': date(2026, 9, 16), 'found_time': time(16, 0)}
    score_later = tm.calculate_similarity(lost_item, found_later)
    assert score_later == 80.0
