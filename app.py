import os
from app import create_app
from seeds import seed_database

app = create_app()

if __name__ == '__main__':
    # Auto seed database if fresh
    with app.app_context():
        from app.models.item import Category
        if Category.query.count() == 0:
            seed_database()

    port = int(os.environ.get('PORT', 5000))
    print(f"\n========================================================")
    print(f" FindIT Application Starting on http://127.0.0.1:{port}/")
    print(f"========================================================\n")
    app.run(host='127.0.0.1', port=port, debug=True)
