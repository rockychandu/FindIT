from datetime import date
from app.models import db
from app.models.item import ItemReport, Category
from app.models.claim import Claim
from app.models.handover import Handover
from app.services.claim_service import (
    complete_handover,
    finder_confirm_submission,
    authority_receive_item,
    claimant_confirm_collection
)

def test_handover_completion_and_state_transition(app):
    with app.app_context():
        cat = Category.query.first()

        found = ItemReport(
            public_report_id='LF-2026-000301',
            report_type='FOUND',
            user_id=1,
            category_id=cat.id,
            item_name='Calculator',
            description='Scientific Casio',
            location='Lab',
            date=date(2026, 9, 10),
            status='HANDOVER_PENDING'
        )
        lost = ItemReport(
            public_report_id='LF-2026-000302',
            report_type='LOST',
            user_id=2,
            category_id=cat.id,
            item_name='Calculator',
            description='Scientific Casio',
            location='Lab',
            date=date(2026, 9, 10),
            status='HANDOVER_PENDING'
        )
        db.session.add_all([found, lost])
        db.session.flush()

        claim = Claim(
            found_report_id=found.id,
            lost_report_id=lost.id,
            claimant_id=2,
            status='CLAIM_APPROVED'
        )
        db.session.add(claim)
        db.session.flush()

        handover = Handover(
            report_id=found.id,
            claim_id=claim.id,
            claimant_id=2,
            authorized_by=1,
            status='PENDING'
        )
        db.session.add(handover)
        db.session.commit()

        # Step 1: Finder confirms submission
        ho_finder = finder_confirm_submission(handover.id, finder_user_id=1)
        assert ho_finder.found_person_submitted is True
        assert ho_finder.status == 'FOUND_SUBMITTED'

        # Step 2: Authority receives physical item
        ho_received = authority_receive_item(handover.id, admin_id=1, condition_notes="Good condition")
        assert ho_received.authority_received is True
        assert ho_received.status == 'RECEIVED_BY_AUTHORITY'
        assert found.status == 'ITEM_RECEIVED_BY_AUTHORITY'
        assert lost.status == 'READY_FOR_COLLECTION'

        # Step 3: Claimant confirms collection request
        ho_coll = claimant_confirm_collection(handover.id, claimant_user_id=2)
        assert ho_coll.lost_person_collected is True

        # Step 4: Authority completes final handover
        completed = complete_handover(handover.id, admin_id=1, notes="Verified Student ID Card #9021")

        assert completed.status == 'COMPLETED'
        assert found.status == 'RETURNED'
        assert lost.status == 'CLOSED'

        # Verify duplicate handover prevention
        try:
            complete_handover(handover.id, admin_id=1, notes="Duplicate attempt")
            assert False, "Should have raised ValueError for duplicate handover completion"
        except ValueError as ve:
            assert "already been completed" in str(ve)
