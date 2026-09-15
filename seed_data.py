from datetime import date, time
from app import create_app
from models import db, User, Category, LostReport, FoundReport, VerificationQuestion, Match
from matching.match_service import MatchService

def seed_database():
    app = create_app()
    with app.app_context():
        print("Seeding database...")

        # 1. Create Test Users
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@college.edu',
                full_name='Campus Lost&Found Admin',
                college_id='ADM-001',
                role='admin'
            )
            admin.set_password('admin123')
            db.session.add(admin)

        student1 = User.query.filter_by(username='john_doe').first()
        if not student1:
            student1 = User(
                username='john_doe',
                email='john.doe@student.college.edu',
                full_name='John Doe',
                college_id='STU-2024-089',
                role='user'
            )
            student1.set_password('user123')
            db.session.add(student1)

        student2 = User.query.filter_by(username='sarah_smith').first()
        if not student2:
            student2 = User(
                username='sarah_smith',
                email='sarah.smith@student.college.edu',
                full_name='Sarah Smith',
                college_id='STU-2024-114',
                role='user'
            )
            student2.set_password('user123')
            db.session.add(student2)

        db.session.commit()

        # 2. Get Categories
        cat_wallet = Category.query.filter(Category.name.like('%Wallet%')).first()
        cat_phone = Category.query.filter(Category.name.like('%Mobile%')).first()

        # 3. Create Sample Lost Report
        lost1 = LostReport.query.filter_by(item_name='Black Leather Samsung Wallet').first()
        if not lost1 and cat_wallet:
            lost1 = LostReport(
                user_id=student1.id,
                category_id=cat_wallet.id,
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
            db.session.add(lost1)

        # 4. Create Sample Found Report
        found1 = FoundReport.query.filter_by(item_name='Black Leather Samsung Wallet').first()
        if not found1 and cat_wallet:
            found1 = FoundReport(
                user_id=student2.id,
                category_id=cat_wallet.id,
                item_name='Black Leather Samsung Wallet',
                description='Black leather wallet with small scratch near zipper found on library table.',
                brand='Samsung',
                color='Black',
                distinguishing_features='Small scratch near zipper',
                location_text='Library 2nd Floor',
                storage_location='Security Office Desk Box #4',
                latitude=12.9718,
                longitude=77.5948,
                found_date=date(2026, 9, 14),
                found_time=time(16, 0),
                status='ACTIVE'
            )
            db.session.add(found1)
            db.session.commit()

            # Add Verification Questions
            q1 = VerificationQuestion(
                found_report_id=found1.id,
                question_text="What exact ID or card is stored inside the front pocket?",
                expected_answer="College student ID card for John Doe STU-2024-089",
                question_order=1
            )
            q2 = VerificationQuestion(
                found_report_id=found1.id,
                question_text="Where exactly is the distinguishing scratch located?",
                expected_answer="Small scratch near the zipper edge",
                question_order=2
            )
            db.session.add_all([q1, q2])

        db.session.commit()

        # 5. Run Matching Engine to calculate initial match pair
        matcher = MatchService()
        count = matcher.run_all_matches()
        print(f"Seeding completed successfully! Generated {count} initial match(es).")

if __name__ == '__main__':
    seed_database()
