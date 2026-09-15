# Testing Strategy & Automated Test Suite

## Test Execution Command
Run the complete automated test suite using `pytest`:

```bash
pytest -v
```

## Test Modules Overview

| Test Module | Coverage Area |
| :--- | :--- |
| `tests/test_preprocessing.py` | Text cleaning, lowercasing, punctuation stripping, stop-word filtering |
| `tests/test_text_matcher.py` | TF-IDF vectorization & Cosine Similarity across item fields |
| `tests/test_category_location_time.py` | Category matrix, Haversine geo distance, text location fallbacks, temporal proximity decay |
| `tests/test_image_matcher.py` | PIL/NumPy local dHash and RGB color histogram matching |
| `tests/test_matching_engine.py` | Score calculator, dynamic weight redistribution, confidence mapping |
| `tests/test_claim_verification.py` | AnswerMatcher sequence ratio & token overlap, VerificationScorer multi-question aggregation |
| `tests/test_security_authorization.py` | IDOR protection, private verification answer protection (verifying expected answers are omitted) |
| `tests/test_e2e_flow.py` | Full end-to-end integration lifecycle test |
