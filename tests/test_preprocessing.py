from matching.preprocessing import preprocess_text, tokenize_text

def test_preprocess_text_basic():
    text = "The Black Leather Wallet with Samsung logo!"
    clean = preprocess_text(text)
    tokens = clean.split()
    assert "black" in tokens
    assert "leather" in tokens
    assert "wallet" in tokens
    assert "samsung" in tokens
    assert "the" not in tokens  # Stop word removed
    assert "!" not in clean   # Punctuation removed

def test_preprocess_text_empty_and_punctuation():
    assert preprocess_text("") == ""
    assert preprocess_text(None) == ""
    assert preprocess_text("!!!  ???") == ""

def test_tokenize_text():
    tokens = tokenize_text("Red iPhone 13 Pro Max")
    assert "red" in tokens
    assert "iphone" in tokens
    assert "13" in tokens
