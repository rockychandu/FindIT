from app.models import db
from app.models.user import User
from app.models.item import ItemReport, Category
from app.models.match import Match
from app.models.claim import Claim
from app.models.handover import Handover
from app.services.claim_service import (
    process_claim_decision,
    complete_handover,
    finder_confirm_submission,
    authority_receive_item,
    claimant_confirm_collection
)

def test_full_findit_end_to_end_workflow(client, app):
    """
    Complete integration test covering:
    Registration with Mobile Number -> Report Lost -> Report Found -> Matching -> Verification Submission -> Awaiting Authority Decision -> Authority Dual-Party Review -> Approval -> Finder Submission -> Authority Receipt -> Claimant Collection -> Handover -> RETURNED -> CLOSED
    """
    # 1. Register new Student User (Claimant - Lost Person) with Mobile Number
    res_reg = client.post('/register', data={
        'name': 'Charlie Student',
        'email': 'charlie@college.edu',
        'mobile_number': '9876543999',
        'password': 'CharliePassword123!',
        'role': 'STUDENT'
    }, follow_redirects=True)
    assert res_reg.status_code == 200

    # 2. Login as Charlie
    res_login = client.post('/login', data={
        'email': 'charlie@college.edu',
        'password': 'CharliePassword123!'
    }, follow_redirects=True)
    assert res_login.status_code == 200

    with app.app_context():
        cat = Category.query.first()
        cat_id = cat.id

    # 3. Report Lost Item with Secret Verification Question
    res_lost = client.post('/report-lost', data={
        'item_name': 'Blue Jansport Backpack',
        'category_id': str(cat_id),
        'description': 'Dark blue canvas backpack with laptop compartment',
        'color': 'Blue',
        'brand': 'Jansport',
        'location': 'Student Union Dining Hall',
        'date': '2026-09-15',
        'question[]': ['What keychain is attached to front zipper?'],
        'answer[]': ['Silver NASA Space Shuttle Keychain']
    }, follow_redirects=True)
    assert res_lost.status_code == 200

    with app.app_context():
        charlie_user = User.query.filter_by(email='charlie@college.edu').first()
        assert charlie_user.mobile_number == '9876543999'
        lost_report = ItemReport.query.filter_by(user_id=charlie_user.id, report_type='LOST').first()
        assert lost_report is not None
        assert lost_report.public_report_id.startswith('LF-2026-')
        vq = lost_report.verification_questions[0]
        assert vq.question == 'What keychain is attached to front zipper?'
        assert vq.private_expected_answer == 'Silver NASA Space Shuttle Keychain'

    # 4. Login as Reporter 2 (Alex Johnson - Found Person) and Report Found Item
    client.get('/logout')
    client.post('/login', data={'email': 'student@college.edu', 'password': 'StudentPass123!'})

    res_found = client.post('/report-found', data={
        'item_name': 'Blue Jansport Backpack',
        'category_id': str(cat_id),
        'description': 'Found navy blue Jansport backpack with laptop compartment',
        'color': 'Blue',
        'brand': 'Jansport',
        'location': 'Student Union Hallway',
        'date': '2026-09-15'
    }, follow_redirects=True)
    assert res_found.status_code == 200

    # 5. Verify Matching Engine Execution
    with app.app_context():
        found_report = ItemReport.query.filter_by(report_type='FOUND', item_name='Blue Jansport Backpack').first()
        assert found_report is not None

        match_record = Match.query.filter_by(
            lost_report_id=lost_report.id,
            found_report_id=found_report.id
        ).first()
        assert match_record is not None
        assert match_record.overall_score >= 0.50

    # 6. Login back as Charlie (Lost Person) & Submit Verification
    client.get('/logout')
    client.post('/login', data={'email': 'charlie@college.edu', 'password': 'CharliePassword123!'})

    res_claim = client.post(f'/claim/{found_report.id}', data={
        f'question_{vq.id}': 'Silver NASA Space Shuttle Keychain'
    }, follow_redirects=True)
    assert res_claim.status_code == 200
    assert b'submitted to the college authority' in res_claim.data

    with app.app_context():
        claim_rec = Claim.query.filter_by(found_report_id=found_report.id, claimant_id=charlie_user.id).first()
        assert claim_rec is not None
        assert claim_rec.status == 'AWAITING_AUTHORITY_DECISION'

    # 7. Login as Authority Admin & Inspect Dual-Party Details
    client.get('/logout')
    client.post('/authority-login', data={'email': 'admin@college.edu', 'password': 'AuthorityAdmin2026!'})

    res_review_page = client.get(f'/admin/claim/{claim_rec.id}')
    assert res_review_page.status_code == 200
    assert b'9876543999' in res_review_page.data  # Admin sees mobile number
    assert b'Silver NASA Space Shuttle Keychain' in res_review_page.data

    # Authority approves claim
    res_decision = client.post(f'/admin/claim/{claim_rec.id}', data={
        'action': 'approve',
        'decision_reason': 'Verification answer matches NASA keychain perfectly.',
        'location': 'College Lost & Found Office',
        'scheduled_date': '2026-09-16',
        'scheduled_time': '11:00 AM'
    }, follow_redirects=True)
    assert res_decision.status_code == 200

    # 8. Complete Multi-Step Handover Workflow
    with app.app_context():
        claim_after = Claim.query.get(claim_rec.id)
        assert claim_after.status == 'CLAIM_APPROVED'

        handover_rec = Handover.query.filter_by(claim_id=claim_rec.id).first()
        assert handover_rec is not None
        assert handover_rec.status == 'PENDING'

        # Finder confirms submission
        ho_finder = finder_confirm_submission(handover_rec.id, finder_user_id=found_report.user_id)
        assert ho_finder.found_person_submitted is True

        # Authority receives physical item
        ho_rx = authority_receive_item(handover_rec.id, admin_id=1, condition_notes="Received in good condition")
        assert ho_rx.authority_received is True

        # Claimant confirms collection request
        ho_col = claimant_confirm_collection(handover_rec.id, claimant_user_id=charlie_user.id)
        assert ho_col.lost_person_collected is True

        # Authority finalizes physical handover
        completed_ho = complete_handover(handover_rec.id, admin_id=1, notes='Student ID Card verified.')
        assert completed_ho.status == 'COMPLETED'

        # Check final DB state synchronization across records
        updated_found = ItemReport.query.get(found_report.id)
        updated_lost = ItemReport.query.get(lost_report.id)

        assert updated_found.status == 'RETURNED'
        assert updated_lost.status == 'CLOSED'


def test_authority_rejection_workflow(app):
    """
    Test Authority decision NO - DO NOT GIVE ITEM TO LOST PERSON.
    """
    from datetime import date
    with app.app_context():
        cat = Category.query.first()
        lost = ItemReport(
            public_report_id='LF-2026-000888',
            report_type='LOST',
            user_id=2,
            category_id=cat.id,
            item_name='Watch',
            description='Gold watch',
            location='Gym',
            date=date(2026, 9, 15),
            status='REPORTED_LOST'
        )
        found = ItemReport(
            public_report_id='LF-2026-000889',
            report_type='FOUND',
            user_id=1,
            category_id=cat.id,
            item_name='Watch',
            description='Silver watch',
            location='Gym',
            date=date(2026, 9, 15),
            status='REPORTED_FOUND'
        )
        db.session.add_all([lost, found])
        db.session.flush()

        claim = Claim(
            found_report_id=found.id,
            lost_report_id=lost.id,
            claimant_id=2,
            status='AWAITING_AUTHORITY_DECISION'
        )
        db.session.add(claim)
        db.session.commit()

        rejected_claim = process_claim_decision(
            claim_id=claim.id,
            admin_id=1,
            approved=False,
            decision_reason='Item color (silver vs gold) does not match reported description.'
        )

        assert rejected_claim.status == 'CLAIM_REJECTED'
        assert rejected_claim.decision_reason == 'Item color (silver vs gold) does not match reported description.'
        assert found.status == 'REPORTED_FOUND'
        assert lost.status == 'REPORTED_LOST'

