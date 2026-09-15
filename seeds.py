from flask import has_app_context
from app import create_app
from app.models import db
from app.models.user import User
from app.models.item import Category

def seed_database(app=None):
    if not has_app_context() and app is None:
        app = create_app()
        ctx = app.app_context()
        ctx.push()
    else:
        ctx = None

    try:
        # Seed Categories
        categories = [
            "Electronics & Gadgets",
            "Wallets, Bags & Purses",
            "Student IDs & Cards",
            "Books & Stationery",
            "Keys & Keychains",
            "Apparel & Accessories",
            "Jewelry & Watches",
            "Sports & Fitness Gear",
            "Other"
        ]

        for cat_name in categories:
            if not Category.query.filter_by(name=cat_name).first():
                c = Category(name=cat_name)
                db.session.add(c)

        # Seed Admin User
        admin_email = "admin@college.edu"
        admin = User.query.filter_by(email=admin_email).first()
        if not admin:
            admin = User(
                name="College Authority Admin",
                email=admin_email,
                mobile_number="9876543210",
                role="ADMIN"
            )
            admin.set_password("AuthorityAdmin2026!")
            db.session.add(admin)
        else:
            admin.set_password("AuthorityAdmin2026!")

        # Seed Sample Student User for demonstration
        student_email = "student@college.edu"
        if not User.query.filter_by(email=student_email).first():
            student = User(
                name="Alex Johnson",
                email=student_email,
                mobile_number="9876543211",
                role="STUDENT"
            )
            student.set_password("StudentPass123!")
            db.session.add(student)

        db.session.commit()
    finally:
        if ctx:
            ctx.pop()

if __name__ == '__main__':
    seed_database()
    print("Database seeded successfully!")
