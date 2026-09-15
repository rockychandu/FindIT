from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from matching.preprocessing import preprocess_text

class TextMatcher:
    """
    Computes text similarity using TF-IDF Vectorization and Cosine Similarity.
    Evaluates item_name, description, brand, color, and distinguishing_features.
    """

    def __init__(self, name_weight=0.35, desc_weight=0.30, brand_weight=0.15, color_weight=0.10, feature_weight=0.10):
        self.name_weight = name_weight
        self.desc_weight = desc_weight
        self.brand_weight = brand_weight
        self.color_weight = color_weight
        self.feature_weight = feature_weight

    @staticmethod
    def compute_field_similarity(text1: str, text2: str) -> float:
        """Calculates TF-IDF Cosine Similarity between two text strings."""
        clean1 = preprocess_text(text1)
        clean2 = preprocess_text(text2)

        if not clean1 or not clean2:
            return 0.0

        if clean1 == clean2:
            return 1.0

        try:
            # Unigram vectorizer for word overlap
            vec_uni = TfidfVectorizer(ngram_range=(1, 1))
            mat_uni = vec_uni.fit_transform([clean1, clean2])
            sim_uni = float(cosine_similarity(mat_uni[0:1], mat_uni[1:2])[0][0])

            # Bigram vectorizer for phrase order
            vec_bi = TfidfVectorizer(ngram_range=(1, 2))
            mat_bi = vec_bi.fit_transform([clean1, clean2])
            sim_bi = float(cosine_similarity(mat_bi[0:1], mat_bi[1:2])[0][0])

            sim = (sim_uni * 0.70) + (sim_bi * 0.30)
            return float(sim)
        except Exception:
            # Fallback simple token overlap Jaccard ratio
            t1 = set(clean1.split())
            t2 = set(clean2.split())
            if not t1 or not t2:
                return 0.0
            return len(t1.intersection(t2)) / float(len(t1.union(t2)))

    def calculate_similarity(self, lost_item: dict, found_item: dict) -> float:
        """
        Calculates overall text similarity score (0.0 to 100.0) between lost and found items.
        """
        name_sim = self.compute_field_similarity(lost_item.get('item_name', ''), found_item.get('item_name', ''))
        desc_sim = self.compute_field_similarity(lost_item.get('description', ''), found_item.get('description', ''))
        brand_sim = self.compute_field_similarity(lost_item.get('brand', ''), found_item.get('brand', ''))
        color_sim = self.compute_field_similarity(lost_item.get('color', ''), found_item.get('color', ''))
        feat_sim = self.compute_field_similarity(lost_item.get('distinguishing_features', ''), found_item.get('distinguishing_features', ''))

        # Combine weighted field similarities
        weighted_score = (
            (name_sim * self.name_weight) +
            (desc_sim * self.desc_weight) +
            (brand_sim * self.brand_weight) +
            (color_sim * self.color_weight) +
            (feat_sim * self.feature_weight)
        )

        # Scale to percentage 0 - 100
        return round(weighted_score * 100.0, 2)
