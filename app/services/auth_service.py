from flask import session
from app.models import db
from app.models.user import User
from app.validators.report_validator import validate_registration_data
from app.services.audit_service import log_audit_event

def register_user(name, email, mobile_number, password, role='STUDENT'):
    data = {'name': name, 'email': email, 'mobile_number': mobile_number, 'password': password, 'role': role}
    errors = validate_registration_data(data)
    if errors:
        raise ValueError(errors[0])

    email_clean = email.strip().lower()
    existing_user = User.query.filter_by(email=email_clean).first()
    if existing_user:
        raise ValueError("A user account with this email address already exists.")

    user = User(
        name=name.strip(),
        email=email_clean,
        mobile_number=mobile_number.strip() if mobile_number else None,
        role=role
    )
    user.set_password(password)
    
    db.session.add(user)
    db.session.commit()

    log_audit_event(
        user_id=user.id,
        action='USER_REGISTERED',
        entity_type='User',
        entity_id=user.id,
        description=f"User {user.name} ({user.email}) registered with role {user.role}"
    )

    return user


def authenticate_user(email, password):
    email_clean = email.strip().lower()
    user = User.query.filter_by(email=email_clean).first()
    
    if not user or not user.check_password(password):
        return None

    # Set session
    session['user_id'] = user.id
    session['user_name'] = user.name
    session['user_role'] = user.role

    log_audit_event(
        user_id=user.id,
        action='USER_LOGIN',
        entity_type='User',
        entity_id=user.id,
        description=f"User {user.email} logged in successfully"
    )

    return user


def logout_user():
    user_id = session.get('user_id')
    if user_id:
        log_audit_event(
            user_id=user_id,
            action='USER_LOGOUT',
            entity_type='User',
            entity_id=user_id,
            description=f"User logged out"
        )
    session.clear()
