from datetime import date, time
from models import db, User, Category, LostReport, FoundReport, VerificationQuestion, Match, Claim, Notification, AuditLog
from matching.match_service import MatchService
from verification.claim_service import ClaimService

def test_full_e2e_matching_and_claim_lifecycle(client, app):
    with app.app_context():
        # 1. Setup Users & Category
        student_lost = User(username='e2e_student1', email='student1@e2e.edu', full_name='E2E Student One', role='user')
        student_lost.set_password('pass123')

        student_found = User(username='e2e_student2', email='student2@e2e.edu', full_name='E2E Student Two', role='user')
        student_found.set_password('pass123')

        admin = User(username='e2e_admin', email='admin@e2e.edu', full_name='E2E Admin', role='admin')
        admin.set_password('pass123')

        cat = Category.query.filter_by(name='Wallets & Purses').first()
        if not cat:
            cat = Category(name='Wallets & Purses', description='Wallets')
            db.session.add(cat)

        db.session.add_all([student_lost, student_found, admin])
        db.session.commit()

        # 2. Create Lost Report (Student 1)
        lost = LostReport(
            user_id=student_lost.id,
            category_id=cat.id,
            item_name='Black Leather Samsung Wallet',
            description='Black leather wallet containing Samsung branding, student ID card inside, small scratch near zipper.',
            brand='Samsung',
            color='Black',
            distinguishing_features='Small scratch near zipper, college ID card inside',
            location_text='Main Library 2nd Floor Study Room 204',
            latitude=12.9716,
            longitude=77.5946,
            lost_date=date(2026, 9, 14),
            lost_time=time(14, 30),
            status='ACTIVE'
        )
        db.session.add(lost)
        db.session.commit()

        # 3. Create Found Report (Student 2)
        found = FoundReport(
            user_id=student_found.id,
            category_id=cat.id,
            item_name='Black Leather Samsung Wallet',
            description='Black leather wallet with small scratch near zipper found on library table.',
            brand='Samsung',
            color='Black',
            distinguishing_features='Small scratch near zipper',
            location_text='Library 2nd Floor',
            storage_location='Security Desk Box #4',
            latitude=12.9718,
            longitude=77.5948,
            found_date=date(2026, 9, 14),
            found_time=time(16, 0),
            status='ACTIVE'
        )
        db.session.add(found)
        db.session.commit()

        # Add Verification Question (Finder)
        vq = VerificationQuestion(
            found_report_id=found.id,
            question_text="What exact ID card is inside the front pocket?",
            expected_answer="College student ID card for E2E Student One",
            question_order=1
        )
        db.session.add(vq)
        db.session.commit()

        # 4. Run Matching Engine
        matcher = MatchService()
        matches = matcher.run_matches_for_lost_report(lost.id)

        assert len(matches) == 1
        m = matches[0]
        assert m.overall_score >= 80.0
        assert m.confidence_level == 'HIGH'
        assert m.status == 'POSSIBLE'

        # 5. Student 1 Submits Claim
        claim_service = ClaimService()
        claim = claim_service.submit_claim(match_id=m.id, claimant_id=student_lost.id, remarks="This is my lost wallet!")
        assert claim.status == 'SUBMITTED'

        # 6. Student 1 Answers Verification Question
        answers_dict = {vq.id: "College student ID card for E2E Student One"}
        updated_claim = claim_service.submit_verification_answers(claim_id=claim.id, claimant_id=student_lost.id, answers_dict=answers_dict)

        assert updated_claim.status == 'UNDER_VERIFICATION'
        assert updated_claim.verification_score >= 85.0
        assert updated_claim.verification_confidence == 'STRONG_VERIFICATION'

        # 7. Admin Reviews and Approves Claim
        approved_claim = claim_service.review_claim_admin(claim_id=claim.id, admin_id=admin.id, approved=True, admin_notes="Approved after verifying student ID.")

        # 8. Verify Final DB State
        assert approved_claim.status == 'APPROVED'
        assert m.status == 'CONFIRMED'
        assert lost.status == 'CLAIMED'
        assert found.status == 'CLAIMED'

        # Verify Notifications & Audit Logs created
        notifs = Notification.query.filter_by(user_id=student_lost.id).all()
        assert len(notifs) >= 2

        audits = AuditLog.query.all()
        assert len(audits) >= 3
