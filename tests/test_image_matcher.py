import os
from PIL import Image
from matching.image_matcher import ImageMatcher

def test_image_matcher_local_files(tmp_path):
    # Create two test images locally
    img1_path = str(tmp_path / "img1.png")
    img2_path = str(tmp_path / "img2.png")

    img1 = Image.new('RGB', (100, 100), color='red')
    img2 = Image.new('RGB', (100, 100), color='red')
    img1.save(img1_path)
    img2.save(img2_path)

    im = ImageMatcher()
    score = im.calculate_similarity(img1_path, img2_path)
    assert score is not None
    assert score == 100.0

def test_image_matcher_missing_file():
    im = ImageMatcher()
    assert im.calculate_similarity(None, "non_existent.png") is None
