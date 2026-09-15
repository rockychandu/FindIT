from datetime import date
from app.models import db
from app.models.item import ItemReport, Category
from app.models.claim import Claim, VerificationQuestion
from app.services.claim_service import submit_claim, process_claim_decision

def test_claim_submission_and_admin_review(app):
    with app.app_context():
        cat = Category.query.first()

        # Reporter 1 reports lost
        lost = ItemReport(
            public_report_id='LF-2026-000201',
            report_type='LOST',
            user_id=2,  # student
            category_id=cat.id,
            item_name='AirPods Pro',
            description='White AirPods Pro case',
            location='Library',
            date=date(2026, 9, 12),
            status='REPORTED_LOST'
        )
        db.session.add(lost)
        db.session.flush()

        # Secret question
        vq = VerificationQuestion(
            item_report_id=lost.id,
            question='What initials are engraved on the back?',
            private_expected_answer='AJ'
        )
        db.session.add(vq)

        # Reporter 2 reports found
        found = ItemReport(
            public_report_id='LF-2026-000202',
            report_type='FOUND',
            user_id=1,  # admin
            category_id=cat.id,
            item_name='AirPods Pro Case',
            description='Found white AirPods Pro case',
            location='Library 1st floor',
            date=date(2026, 9, 12),
            status='REPORTED_FOUND'
        )
        db.session.add(found)
        db.session.commit()

        # Student submits claim answering question
        claim = submit_claim(
            claimant_id=2,
            found_report_id=found.id,
            lost_report_id=lost.id,
            responses_data=[{'question_id': vq.id, 'answer': 'AJ'}]
        )

        assert claim.status == 'AWAITING_AUTHORITY_DECISION'
        assert len(claim.responses) == 1
        assert claim.responses[0].similarity_score == 1.0

        # Admin approves claim
        approved_claim = process_claim_decision(
            claim_id=claim.id,
            admin_id=1,
            approved=True,
            decision_reason='Verification answer AJ matches expected initials exactly.'
        )

        assert approved_claim.status == 'CLAIM_APPROVED'
        assert found.status == 'HANDOVER_PENDING'
        assert lost.status == 'HANDOVER_PENDING'
