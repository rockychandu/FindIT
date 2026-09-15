from models import db, Claim, ClaimAnswer, Match, VerificationQuestion, Notification, AuditLog, LostReport, FoundReport
from verification.answer_matcher import AnswerMatcher
from verification.verification_scorer import VerificationScorer

class ClaimService:
    """
    Service for claim submission, private verification scoring, state transitions,
    authorization enforcement, and notifications.
    """

    def __init__(self):
        self.answer_matcher = AnswerMatcher()
        self.scorer = VerificationScorer()

    def submit_claim(self, match_id: int, claimant_id: int, remarks: str = "") -> Claim:
        """
        Submits a claim for a possible match.
        Validates ownership, active report status, and duplicate claim prevention.
        """
        match = Match.query.get(match_id)
        if not match:
            raise ValueError("Match record not found.")

        # Ensure lost report belongs to claimant
        lost_report = match.lost_report
        if lost_report.user_id != claimant_id:
            raise PermissionError("You can only submit claims for your own lost reports.")

        # Check for existing active claim on this match
        existing_claim = Claim.query.filter(
            Claim.match_id == match_id,
            Claim.status.in_(['SUBMITTED', 'UNDER_VERIFICATION', 'APPROVED'])
        ).first()

        if existing_claim:
            raise ValueError("An active claim already exists for this match.")

        claim = Claim(
            match_id=match.id,
            claimant_id=claimant_id,
            lost_report_id=match.lost_report_id,
            found_report_id=match.found_report_id,
            status='SUBMITTED',
            remarks=remarks
        )

        db.session.add(claim)
        
        # Audit Log
        audit = AuditLog(
            user_id=claimant_id,
            action="CLAIM_SUBMITTED",
            details=f"Claim #{claim.id} submitted for Match #{match.id}"
        )
        db.session.add(audit)

        db.session.commit()
        return claim

    def submit_verification_answers(self, claim_id: int, claimant_id: int, answers_dict: dict[int, str]) -> Claim:
        """
        Processes claimant's verification answers, calculates similarity against server-side expected answers,
        computes overall verification score, and updates status to UNDER_VERIFICATION.
        """
        claim = Claim.query.get(claim_id)
        if not claim:
            raise ValueError("Claim not found.")

        if claim.claimant_id != claimant_id:
            raise PermissionError("Unauthorized claim access.")

        if claim.status not in ['SUBMITTED', 'UNDER_VERIFICATION']:
            raise ValueError(f"Cannot submit verification for claim in status '{claim.status}'.")

        # Fetch questions for this found report
        questions = VerificationQuestion.query.filter_by(
            found_report_id=claim.found_report_id,
            is_active=True
        ).all()

        answer_scores = []

        # Clear existing answers if resubmitting during verification
        ClaimAnswer.query.filter_by(claim_id=claim.id).delete()

        for q in questions:
            user_ans = answers_dict.get(q.id, "").strip()
            score = self.answer_matcher.calculate_answer_similarity(
                expected=q.expected_answer,  # Server-side evaluation ONLY
                claimant=user_ans
            )

            claim_answer = ClaimAnswer(
                claim_id=claim.id,
                question_id=q.id,
                answer_text=user_ans,
                similarity_score=score
            )
            db.session.add(claim_answer)
            answer_scores.append(score)

        # Calculate overall verification score and confidence level
        avg_score, confidence = self.scorer.calculate_overall_verification(answer_scores)

        claim.verification_score = avg_score
        claim.verification_confidence = confidence
        claim.status = 'UNDER_VERIFICATION'

        # Notify claimant
        notif = Notification(
            user_id=claimant_id,
            title="Verification Submitted",
            message=f"Your verification answers for Claim #{claim.id} were submitted and are now under admin review.",
            type="VERIFICATION_SUBMITTED",
            related_claim_id=claim.id
        )
        db.session.add(notif)

        # Audit Log
        audit = AuditLog(
            user_id=claimant_id,
            action="VERIFICATION_ANSWERS_SUBMITTED",
            details=f"Verification submitted for Claim #{claim.id}. Score: {avg_score}% ({confidence})"
        )
        db.session.add(audit)

        db.session.commit()
        return claim

    def review_claim_admin(self, claim_id: int, admin_id: int, approved: bool, admin_notes: str = "") -> Claim:
        """
        Admin decision workflow (Member 3 integration bridge).
        Approves or rejects claim. Updates Lost/Found report statuses accordingly.
        """
        claim = Claim.query.get(claim_id)
        if not claim:
            raise ValueError("Claim not found.")

        if approved:
            claim.status = 'APPROVED'
            claim.match.status = 'CONFIRMED'
            claim.lost_report.status = 'CLAIMED'
            claim.found_report.status = 'CLAIMED'

            notif_msg = f"Great news! Your claim #{claim.id} for item '{claim.lost_report.item_name}' has been APPROVED by admin."
            notif_type = "CLAIM_APPROVED"
        else:
            claim.status = 'REJECTED'
            claim.match.status = 'REJECTED'

            notif_msg = f"Your claim #{claim.id} for item '{claim.lost_report.item_name}' was REJECTED by admin."
            notif_type = "CLAIM_REJECTED"

        claim.admin_notes = admin_notes

        # Notify claimant
        notif = Notification(
            user_id=claim.claimant_id,
            title=f"Claim {claim.status.capitalize()}",
            message=notif_msg,
            type=notif_type,
            related_claim_id=claim.id
        )
        db.session.add(notif)

        # Audit Log
        audit = AuditLog(
            user_id=admin_id,
            action=f"CLAIM_{claim.status}",
            details=f"Admin #{admin_id} set Claim #{claim.id} status to {claim.status}. Notes: {admin_notes}"
        )
        db.session.add(audit)

        db.session.commit()
        return claim
