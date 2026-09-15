from app.models import db
from app.models.item import ItemReport
from app.models.match import Match
from app.models.notification import Notification
from app.matching.engine import compute_match_score

def run_matching_for_report(target_report):
    """
    Given a newly reported LOST or FOUND item, compute matches against all existing items of the opposite type.
    """
    if target_report.status in ['RETURNED', 'CLOSED']:
        return []

    opposite_type = 'FOUND' if target_report.report_type == 'LOST' else 'LOST'
    
    # Query candidate items of opposite type that are not closed
    candidates = ItemReport.query.filter(
        ItemReport.report_type == opposite_type,
        ItemReport.status.notin_(['RETURNED', 'CLOSED'])
    ).all()
    
    matches_created = []

    for candidate in candidates:
        if target_report.report_type == 'LOST':
            lost = target_report
            found = candidate
        else:
            lost = candidate
            found = target_report

        scores = compute_match_score(lost, found)
        
        # Only record meaningful matches (>= 30% overall score)
        if scores['overall_score'] >= 0.30:
            # Check if match record already exists
            existing_match = Match.query.filter_by(
                lost_report_id=lost.id,
                found_report_id=found.id
            ).first()

            if not existing_match:
                match_record = Match(
                    lost_report_id=lost.id,
                    found_report_id=found.id,
                    text_score=scores['text_score'],
                    category_score=scores['category_score'],
                    location_score=scores['location_score'],
                    time_score=scores['time_score'],
                    image_score=scores['image_score'],
                    overall_score=scores['overall_score'],
                    status='PENDING'
                )
                db.session.add(match_record)
                matches_created.append(match_record)

                # Update report statuses if still in base reported status
                if lost.status == 'REPORTED_LOST':
                    lost.status = 'POSSIBLE_MATCH'
                if found.status == 'REPORTED_FOUND':
                    found.status = 'POSSIBLE_MATCH'

                # Send internal notification to lost item owner
                notif = Notification(
                    user_id=lost.user_id,
                    message=f"Possible match found for your lost report '{lost.item_name}' (Match score: {int(scores['overall_score']*100)}%).",
                    related_report_id=found.id
                )
                db.session.add(notif)
            else:
                # Update scores if already existing
                existing_match.text_score = scores['text_score']
                existing_match.category_score = scores['category_score']
                existing_match.location_score = scores['location_score']
                existing_match.time_score = scores['time_score']
                existing_match.overall_score = scores['overall_score']
                matches_created.append(existing_match)

    db.session.commit()
    return matches_created
