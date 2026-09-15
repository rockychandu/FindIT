from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.services.auth_service import register_user, authenticate_user, logout_user

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        mobile_number = request.form.get('mobile_number')
        password = request.form.get('password')
        role = request.form.get('role', 'STUDENT')

        try:
            user = register_user(name, email, mobile_number, password, role)
            flash('Registration successful! Please log in with your credentials.', 'success')
            return redirect(url_for('auth.login', splash='true'))
        except ValueError as ve:
            flash(str(ve), 'danger')
        except Exception as e:
            flash('An unexpected error occurred during registration. Please try again.', 'danger')

    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = authenticate_user(email, password)
        if user:
            flash(f'Welcome back, {user.name}!', 'success')
            next_url = request.args.get('next')
            if user.role == 'ADMIN':
                return redirect(next_url or url_for('admin.dashboard', splash='true'))
            return redirect(next_url or url_for('main.dashboard', splash='true'))
        else:
            flash('Invalid email or password. Please try again.', 'danger')

    return render_template('auth/login.html')


@auth_bp.route('/authority-login', methods=['GET', 'POST'])
def authority_login():
    if 'user_id' in session:
        user = authenticate_user(session.get('email'), '') if False else None
        return redirect(url_for('admin.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = authenticate_user(email, password)
        if user and user.role == 'ADMIN':
            flash(f'Welcome, Authority Admin {user.name}!', 'success')
            return redirect(url_for('admin.dashboard', splash='true'))
        elif user:
            flash('Access Denied: Only authorized college authority credentials can log into the Authority Portal.', 'danger')
        else:
            flash('Invalid authority email or password. Please try again.', 'danger')

    return render_template('auth/authority_login.html')


@auth_bp.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out safely.', 'info')
    return redirect(url_for('main.index', splash='true'))
