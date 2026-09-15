import os
from flask import Flask, render_template, send_from_directory, redirect, url_for
from flask_login import LoginManager
from config import Config
from models import db, User, Category

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register Blueprints
    from routes.auth_routes import auth_bp
    from routes.report_routes import report_bp
    from routes.match_routes import match_bp
    from routes.claim_routes import claim_bp
    from routes.admin_routes import admin_bp
    from routes.notification_routes import notification_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(report_bp)
    app.register_blueprint(match_bp)
    app.register_blueprint(claim_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(notification_bp)

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/static/uploads/<filename>')
    def uploaded_file(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    with app.app_context():
        db.create_all()
        seed_default_categories()

    return app


def seed_default_categories():
    """Seeds default item categories if database is empty."""
    if Category.query.count() == 0:
        default_categories = [
            ("Wallets & Purses", "Wallets, purses, pouches, card holders"),
            ("Mobile Phones & Accessories", "Smartphones, chargers, power banks, cases"),
            ("Laptops & Computers", "Laptops, tablets, keyboards, mice, adapters"),
            ("Headphones & Audio", "Earphones, airpods, headsets, bluetooth speakers"),
            ("ID Cards & Documents", "College IDs, passports, driver licenses, certificates"),
            ("Keys & Keychains", "House keys, car keys, room keys, keychains"),
            ("Water Bottles & Flasks", "Water bottles, thermos, travel mugs"),
            ("Watches & Wearables", "Wristwatches, smartwatches, fitness bands"),
            ("Bags & Backpacks", "College bags, handbags, duffels, luggage"),
            ("Books & Stationery", "Textbooks, notebooks, calculators, pencil cases, pens"),
            ("Clothing & Apparel", "Jackets, sweaters, caps, umbrellas, glasses"),
            ("Other Items", "Miscellaneous campus items")
        ]

        for name, desc in default_categories:
            cat = Category(name=name, description=desc)
            db.session.add(cat)

        db.session.commit()


app = create_app()

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
