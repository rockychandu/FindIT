from datetime import date
from models import db, VerificationQuestion, FoundReport, LostReport, Match, Claim

def test_private_answer_security(client, seed_users):
    """
    CRITICAL SECURITY TEST: Ensure expected_answer is NEVER exposed through public API endpoints.
    """
    # 1. Login user 1
    client.post('/login', data={'username': 'test_user1', 'password': 'password123'})

    with client.application.app_context():
        # Create found report & question
        found = FoundReport(
            user_id=seed_users['user2_id'],
            category_id=seed_users['cat_id'],
            item_name='Secret Wallet',
            description='Wallet found',
            location_text='Library',
            found_date=date(2026, 9, 14)
        )
        lost = LostReport(
            user_id=seed_users['user1_id'],
            category_id=seed_users['cat_id'],
            item_name='Secret Wallet',
            description='Wallet lost',
            location_text='Library',
            lost_date=date(2026, 9, 14)
        )
        db.session.add_all([found, lost])
        db.session.commit()

        q = VerificationQuestion(
            found_report_id=found.id,
            question_text="What hidden emblem is inside?",
            expected_answer="CLASSIFIED_SECRET_ANSWER_123"
        )
        match = Match(lost_report_id=lost.id, found_report_id=found.id, overall_score=90.0, confidence_level='HIGH')
        db.session.add_all([q, match])
        db.session.commit()

        claim = Claim(match_id=match.id, claimant_id=seed_users['user1_id'], lost_report_id=lost.id, found_report_id=found.id)
        db.session.add(claim)
        db.session.commit()
        claim_id = claim.id

    # 2. Fetch claim endpoint
    res = client.get(f'/api/claims/{claim_id}')
    assert res.status_code == 200
    json_data = res.get_json()

    # Assert expected_answer is NOT present in any question dict in JSON response
    questions = json_data.get('verification_questions', [])
    assert len(questions) > 0
    for q_dict in questions:
        assert 'expected_answer' not in q_dict
        assert 'CLASSIFIED_SECRET_ANSWER_123' not in str(q_dict)

def test_idor_protection(client, seed_users):
    """
    Tests IDOR protection: User 2 attempting to view User 1's claim should be blocked with 403.
    """
    with client.application.app_context():
        found = FoundReport(user_id=seed_users['user2_id'], category_id=seed_users['cat_id'], item_name='Wallet', description='Found', location_text='Lib', found_date=date(2026, 9, 14))
        lost = LostReport(user_id=seed_users['user1_id'], category_id=seed_users['cat_id'], item_name='Wallet', description='Lost', location_text='Lib', lost_date=date(2026, 9, 14))
        db.session.add_all([found, lost])
        db.session.commit()

        match = Match(lost_report_id=lost.id, found_report_id=found.id, overall_score=85.0, confidence_level='HIGH')
        db.session.add(match)
        db.session.commit()

        claim = Claim(match_id=match.id, claimant_id=seed_users['user1_id'], lost_report_id=lost.id, found_report_id=found.id)
        db.session.add(claim)
        db.session.commit()
        claim_id = claim.id

    # Login as User 2 (not the claimant)
    client.post('/login', data={'username': 'test_user2', 'password': 'password123'})
    res = client.get(f'/api/claims/{claim_id}')
    assert res.status_code == 403
