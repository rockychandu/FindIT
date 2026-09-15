import math
from matching.preprocessing import preprocess_text

class LocationMatcher:
    """
    Evaluates location compatibility using Haversine distance for coordinates
    or normalized text similarity for campus building/room location names.
    No external Google Maps API required.
    """

    @staticmethod
    def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculates distance between two lat/lon points in meters using Haversine formula."""
        R = 6371000.0  # Earth radius in meters
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)

        a = math.sin(delta_phi / 2.0)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0)**2
        c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))

        return R * c

    def score_from_distance(self, distance_meters: float) -> float:
        """Converts distance in meters to a 0 - 100 similarity score."""
        if distance_meters <= 50:
            return 100.0
        elif distance_meters <= 200:
            return 90.0 - ((distance_meters - 50) / 150.0) * 15.0  # 90 -> 75
        elif distance_meters <= 500:
            return 75.0 - ((distance_meters - 200) / 300.0) * 25.0  # 75 -> 50
        elif distance_meters <= 2000:
            return 50.0 - ((distance_meters - 500) / 1500.0) * 40.0 # 50 -> 10
        else:
            return 0.0

    def score_from_text(self, loc1: str, loc2: str) -> float:
        """Calculates text-based location similarity using token overlap, min-overlap ratio, and keyword matching."""
        clean1 = preprocess_text(loc1)
        clean2 = preprocess_text(loc2)

        if not clean1 or not clean2:
            return 50.0  # Neutral fallback if location is unspecified

        if clean1 == clean2:
            return 100.0

        t1 = set(clean1.split())
        t2 = set(clean2.split())

        intersection = t1.intersection(t2)
        union = t1.union(t2)

        if not union:
            return 0.0

        jaccard = len(intersection) / float(len(union))
        min_overlap = len(intersection) / float(min(len(t1), len(t2)))
        
        # Combined overlap ratio
        overlap_score = (jaccard * 0.40) + (min_overlap * 0.60)

        # Number matching bonus (e.g., room 204, lab 3)
        nums1 = {w for w in t1 if w.isdigit()}
        nums2 = {w for w in t2 if w.isdigit()}
        
        number_match_bonus = 0.0
        if nums1 and nums2 and nums1.intersection(nums2):
            number_match_bonus = 0.20

        score = min(1.0, overlap_score + number_match_bonus) * 100.0
        return round(score, 2)

    def calculate_similarity(self, lost_item: dict, found_item: dict) -> float:
        """
        Calculates location similarity score (0.0 to 100.0).
        Prioritizes geo-coordinates if available, otherwise relies on text location.
        """
        lat1 = lost_item.get('latitude')
        lon1 = lost_item.get('longitude')
        lat2 = found_item.get('latitude')
        lon2 = found_item.get('longitude')

        if lat1 is not None and lon1 is not None and lat2 is not None and lon2 is not None:
            try:
                distance = self.haversine_distance(float(lat1), float(lon1), float(lat2), float(lon2))
                geo_score = self.score_from_distance(distance)
                
                # Also calculate text score if available
                text_score = self.score_from_text(lost_item.get('location_text', ''), found_item.get('location_text', ''))
                # Combine 70% geo + 30% text
                return round((geo_score * 0.70) + (text_score * 0.30), 2)
            except (ValueError, TypeError):
                pass

        # Fallback to text location matching
        return self.score_from_text(lost_item.get('location_text', ''), found_item.get('location_text', ''))
