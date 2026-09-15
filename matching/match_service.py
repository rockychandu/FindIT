from models import db, Match, LostReport, FoundReport, Notification
from matching.text_matcher import TextMatcher
from matching.category_matcher import CategoryMatcher
from matching.location_matcher import LocationMatcher
from matching.time_matcher import TimeMatcher
from matching.image_matcher import ImageMatcher
from matching.score_calculator import ScoreCalculator
from matching.ranking import MatchRanker
from matching.candidate_selector import CandidateSelector

class MatchService:
    """
    Central service layer for running the FindIT Intelligent Matching Engine.
    Orchestrates signal matchers, computes overall scores, ranks matches, and manages DB persistence.
    """

    def __init__(self):
        self.text_matcher = TextMatcher()
        self.category_matcher = CategoryMatcher()
        self.location_matcher = LocationMatcher()
        self.time_matcher = TimeMatcher()
        self.image_matcher = ImageMatcher()
        self.score_calculator = ScoreCalculator()
        self.ranker = MatchRanker()

    def evaluate_pair(self, lost_report: LostReport, found_report: FoundReport) -> dict:
        """
        Evaluates signal scores between a single LostReport and FoundReport.
        Returns score dictionary.
        """
        lost_dict = lost_report.to_dict()
        found_dict = found_report.to_dict()

        # 1. Text Similarity Score
        text_score = self.text_matcher.calculate_similarity(lost_dict, found_dict)

        # 2. Category Similarity Score
        category_score = self.category_matcher.calculate_similarity(
            lost_cat_id=lost_report.category_id,
            found_cat_id=found_report.category_id,
            lost_cat_name=lost_report.category.name if lost_report.category else "",
            found_cat_name=found_report.category.name if found_report.category else "",
            parent_lost_id=lost_report.category.parent_id if lost_report.category else None,
            parent_found_id=found_report.category.parent_id if found_report.category else None
        )

        # 3. Location Similarity Score
        location_score = self.location_matcher.calculate_similarity(lost_dict, found_dict)

        # 4. Time Proximity Score
        time_score = self.time_matcher.calculate_similarity(lost_dict, found_dict)

        # 5. Local Image Similarity Score (Optional)
        image_score = self.image_matcher.calculate_similarity(lost_report.image_path, found_report.image_path)

        # 6. Overall Score & Dynamic Weights
        overall_score, weights = self.score_calculator.calculate_overall_score(
            text_score=text_score,
            category_score=category_score,
            location_score=location_score,
            time_score=time_score,
            image_score=image_score
        )

        confidence_level = self.ranker.map_confidence_level(overall_score)

        return {
            'lost_report_id': lost_report.id,
            'found_report_id': found_report.id,
            'text_score': text_score,
            'category_score': category_score,
            'location_score': location_score,
            'time_score': time_score,
            'image_score': image_score,
            'overall_score': overall_score,
            'confidence_level': confidence_level,
            'weights_used': weights
        }

    def run_matches_for_lost_report(self, lost_report_id: int) -> list[Match]:
        """
        Executes matching engine for a specific LostReport against all active FoundReports.
        Saves or updates Match records in the database.
        """
        lost_report = LostReport.query.get(lost_report_id)
        if not lost_report or lost_report.status != 'ACTIVE':
            return []

        candidates = CandidateSelector.get_found_candidates_for_lost(lost_report)
        generated_matches = []

        for candidate in candidates:
            res = self.evaluate_pair(lost_report, candidate)

            # Skip NOT_SUITABLE scores below LOW threshold
            if res['confidence_level'] == 'NOT_SUITABLE':
                continue

            # Check if match record already exists
            existing = Match.query.filter_by(
                lost_report_id=lost_report.id,
                found_report_id=candidate.id
            ).first()

            if existing:
                existing.text_score = res['text_score']
                existing.category_score = res['category_score']
                existing.location_score = res['location_score']
                existing.time_score = res['time_score']
                existing.image_score = res['image_score']
                existing.overall_score = res['overall_score']
                existing.confidence_level = res['confidence_level']
                match_obj = existing
            else:
                match_obj = Match(
                    lost_report_id=lost_report.id,
                    found_report_id=candidate.id,
                    text_score=res['text_score'],
                    category_score=res['category_score'],
                    location_score=res['location_score'],
                    time_score=res['time_score'],
                    image_score=res['image_score'],
                    overall_score=res['overall_score'],
                    confidence_level=res['confidence_level'],
                    status='POSSIBLE'
                )
                db.session.add(match_obj)
                
                # Create notification for lost report owner
                notif = Notification(
                    user_id=lost_report.user_id,
                    title="Possible Match Found!",
                    message=f"A possible match ({res['overall_score']}%) was found for your lost '{lost_report.item_name}'.",
                    type="MATCH_FOUND",
                    related_report_id=lost_report.id
                )
                db.session.add(notif)

            generated_matches.append(match_obj)

        db.session.commit()
        return generated_matches

    def run_matches_for_found_report(self, found_report_id: int) -> list[Match]:
        """
        Executes matching engine for a specific FoundReport against all active LostReports.
        """
        found_report = FoundReport.query.get(found_report_id)
        if not found_report or found_report.status != 'ACTIVE':
            return []

        candidates = CandidateSelector.get_lost_candidates_for_found(found_report)
        generated_matches = []

        for candidate in candidates:
            res = self.evaluate_pair(candidate, found_report)

            if res['confidence_level'] == 'NOT_SUITABLE':
                continue

            existing = Match.query.filter_by(
                lost_report_id=candidate.id,
                found_report_id=found_report.id
            ).first()

            if existing:
                existing.text_score = res['text_score']
                existing.category_score = res['category_score']
                existing.location_score = res['location_score']
                existing.time_score = res['time_score']
                existing.image_score = res['image_score']
                existing.overall_score = res['overall_score']
                existing.confidence_level = res['confidence_level']
                match_obj = existing
            else:
                match_obj = Match(
                    lost_report_id=candidate.id,
                    found_report_id=found_report.id,
                    text_score=res['text_score'],
                    category_score=res['category_score'],
                    location_score=res['location_score'],
                    time_score=res['time_score'],
                    image_score=res['image_score'],
                    overall_score=res['overall_score'],
                    confidence_level=res['confidence_level'],
                    status='POSSIBLE'
                )
                db.session.add(match_obj)

                notif = Notification(
                    user_id=candidate.user_id,
                    title="Possible Match Found!",
                    message=f"A possible match ({res['overall_score']}%) was found for your lost '{candidate.item_name}'.",
                    type="MATCH_FOUND",
                    related_report_id=candidate.id
                )
                db.session.add(notif)

            generated_matches.append(match_obj)

        db.session.commit()
        return generated_matches

    def run_all_matches(self) -> int:
        """Runs matching engine across all active lost and found reports."""
        active_lost = LostReport.query.filter_by(status='ACTIVE').all()
        count = 0
        for lost in active_lost:
            matches = self.run_matches_for_lost_report(lost.id)
            count += len(matches)
        return count
