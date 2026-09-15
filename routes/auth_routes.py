from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User
from services.audit_service import AuditService

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('report.dashboard'))

    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            username = data.get('username')
            email = data.get('email')
            password = data.get('password')
            full_name = data.get('full_name')
            college_id = data.get('college_id')
            role = data.get('role', 'user')
        else:
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            full_name = request.form.get('full_name')
            college_id = request.form.get('college_id')
            role = request.form.get('role', 'user')

        if not username or not email or not password or not full_name:
            err = "All required fields must be filled."
            return jsonify({'error': err}), 400 if request.is_json else (flash(err, 'danger') or render_template('auth/register.html'))

        if User.query.filter((User.username == username) | (User.email == email)).first():
            err = "Username or Email already registered."
            return jsonify({'error': err}), 400 if request.is_json else (flash(err, 'danger') or render_template('auth/register.html'))

        user = User(
            username=username,
            email=email,
            full_name=full_name,
            college_id=college_id,
            role=role if role in ['user', 'admin'] else 'user'
        )
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        AuditService.log_action(user.id, "USER_REGISTERED", f"User registered: {username}")

        if request.is_json:
            return jsonify({'message': 'Registration successful', 'user': user.to_dict()}), 201

        flash("Registration successful! Please login.", "success")
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('report.dashboard'))

    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            username = data.get('username')
            password = data.get('password')
        else:
            username = request.form.get('username')
            password = request.form.get('password')

        user = User.query.filter((User.username == username) | (User.email == username)).first()

        if not user or not user.check_password(password):
            err = "Invalid username or password."
            if request.is_json:
                return jsonify({'error': err}), 401
            flash(err, 'danger')
            return render_template('auth/login.html')

        login_user(user)
        AuditService.log_action(user.id, "USER_LOGIN", f"User logged in: {user.username}")

        if request.is_json:
            return jsonify({'message': 'Login successful', 'user': user.to_dict()}), 200

        flash(f"Welcome back, {user.full_name}!", "success")
        next_page = request.args.get('next')
        return redirect(next_page or url_for('report.dashboard'))

    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    AuditService.log_action(current_user.id, "USER_LOGOUT", f"User logged out: {current_user.username}")
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for('auth.login'))
