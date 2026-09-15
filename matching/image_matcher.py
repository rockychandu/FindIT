import os
import numpy as np
from PIL import Image

class ImageMatcher:
    """
    Computes local image similarity using PIL and NumPy.
    Utilizes Difference Hashing (dHash) and RGB Color Histogram distance.
    Returns None if an image is missing or cannot be processed. Zero external API calls.
    """

    @staticmethod
    def compute_dhash(image: Image.Image, hash_size: int = 8) -> np.ndarray:
        """Computes dHash (difference hash) of a PIL Image."""
        # Convert to grayscale and resize to (hash_size + 1, hash_size)
        img = image.convert('L').resize((hash_size + 1, hash_size), Image.Resampling.LANCZOS)
        pixels = np.asarray(img)
        # Compute difference between adjacent pixels horizontally
        diff = pixels[:, 1:] > pixels[:, :-1]
        return diff.flatten()

    @staticmethod
    def compute_color_histogram(image: Image.Image, bins: int = 8) -> np.ndarray:
        """Computes normalized RGB color histogram of a PIL Image."""
        img = image.convert('RGB')
        arr = np.asarray(img)
        # Compute 3D histogram over R, G, B channels
        hist, _ = np.histogramdd(arr.reshape(-1, 3), bins=(bins, bins, bins), range=[(0, 256), (0, 256), (0, 256)])
        # Normalize histogram
        total = hist.sum()
        if total > 0:
            hist = hist / total
        return hist.flatten()

    def calculate_similarity(self, image_path1: str, image_path2: str) -> float | None:
        """
        Calculates image similarity score (0.0 to 100.0) between two local image files.
        Returns None if either image path is missing or invalid.
        """
        if not image_path1 or not image_path2:
            return None

        if not os.path.exists(image_path1) or not os.path.exists(image_path2):
            return None

        try:
            img1 = Image.open(image_path1)
            img2 = Image.open(image_path2)

            # 1. dHash similarity (40% weight)
            hash1 = self.compute_dhash(img1)
            hash2 = self.compute_dhash(img2)
            hamming_distance = np.sum(hash1 != hash2)
            max_bits = len(hash1)
            dhash_sim = max(0.0, 1.0 - (hamming_distance / float(max_bits)))

            # 2. Histogram similarity using Bhattacharyya distance / Intersection (60% weight)
            hist1 = self.compute_color_histogram(img1)
            hist2 = self.compute_color_histogram(img2)
            hist_sim = np.sum(np.minimum(hist1, hist2)) # Histogram intersection

            combined_sim = (dhash_sim * 0.40) + (hist_sim * 0.60)
            return round(combined_sim * 100.0, 2)
        except Exception:
            return None
