class CategoryMatcher:
    """
    Evaluates category compatibility between lost and found reports.
    Supports category IDs, category names, hierarchy (parent-child), and category synonyms.
    """

    # Predefined category synonym / compatibility matrix
    SYNONYM_GROUPS = [
        {'wallet', 'purse', 'pouch', 'card holder', 'money clip'},
        {'phone', 'smartphone', 'mobile', 'iphone', 'android', 'cellphone'},
        {'laptop', 'macbook', 'notebook', 'computer'},
        {'headphone', 'earphone', 'airpods', 'earbuds', 'headset'},
        {'id card', 'college id', 'student id', 'license', 'passport', 'card'},
        {'bottle', 'water bottle', 'flask', 'thermos'},
        {'watch', 'smartwatch', 'fitness band'},
        {'bag', 'backpack', 'handbag', 'tote', 'duffel'},
        {'keys', 'keychain', 'car key'},
        {'calculator', 'scientific calculator'}
    ]

    def calculate_similarity(self, lost_cat_id: int, found_cat_id: int, lost_cat_name: str = "", found_cat_name: str = "", parent_lost_id: int = None, parent_found_id: int = None) -> float:
        """
        Calculates category similarity score (0.0 to 100.0).
        """
        if not lost_cat_id or not found_cat_id:
            # Handle missing category
            return 50.0

        # Exact category ID match
        if lost_cat_id == found_cat_id:
            return 100.0

        # Parent/Child category relationship match
        if (parent_lost_id and parent_lost_id == found_cat_id) or (parent_found_id and parent_found_id == lost_cat_id):
            return 80.0
        
        if parent_lost_id and parent_found_id and parent_lost_id == parent_found_id:
            return 70.0

        # Name-based synonym evaluation
        name1 = (lost_cat_name or "").lower().strip()
        name2 = (found_cat_name or "").lower().strip()

        if name1 and name2:
            if name1 == name2:
                return 100.0
            
            # Check synonym groups
            for group in self.SYNONYM_GROUPS:
                if any(s in name1 for s in group) and any(s in name2 for s in group):
                    return 75.0

        # Category mismatch
        return 0.0
