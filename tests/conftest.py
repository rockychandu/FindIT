import pytest
from app import create_app
from models import db, User, Category, LostReport, FoundReport

@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SECRET_KEY': 'test-secret-key',
        'WTF_CSRF_ENABLED': False
    })

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

@pytest.fixture
def seed_users(app):
    with app.app_context():
        user1 = User(username='test_user1', email='user1@test.com', full_name='User One', role='user')
        user1.set_password('password123')
        
        user2 = User(username='test_user2', email='user2@test.com', full_name='User Two', role='user')
        user2.set_password('password123')

        admin = User(username='admin_user', email='admin@test.com', full_name='Admin User', role='admin')
        admin.set_password('admin123')

        cat = Category.query.filter_by(name='Wallets & Purses').first()
        if not cat:
            cat = Category(name='Wallets & Purses', description='Wallets')
            db.session.add(cat)

        db.session.add_all([user1, user2, admin])
        db.session.commit()

        return {'user1_id': user1.id, 'user2_id': user2.id, 'admin_id': admin.id, 'cat_id': cat.id}
