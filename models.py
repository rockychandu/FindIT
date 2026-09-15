from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    college_id = db.Column(db.String(50), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    role = db.Column(db.String(20), default='user', nullable=False)  # 'user', 'admin'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    lost_reports = db.relationship('LostReport', backref='owner', lazy='dynamic')
    found_reports = db.relationship('FoundReport', backref='reporter', lazy='dynamic')
    claims = db.relationship('Claim', backref='claimant', lazy='dynamic')
    notifications = db.relationship('Notification', backref='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        return self.role == 'admin'

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'college_id': self.college_id,
            'role': self.role
        }


class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)

    parent = db.relationship('Category', remote_side=[id], backref='subcategories')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'parent_id': self.parent_id
        }


class LostReport(db.Model):
    __tablename__ = 'lost_reports'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    
    item_name = db.Column(db.String(128), nullable=False, index=True)
    description = db.Column(db.Text, nullable=False)
    brand = db.Column(db.String(64), nullable=True)
    color = db.Column(db.String(64), nullable=True)
    distinguishing_features = db.Column(db.Text, nullable=True)

    location_text = db.Column(db.String(255), nullable=False)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)

    lost_date = db.Column(db.Date, nullable=False)
    lost_time = db.Column(db.Time, nullable=True)

    image_path = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(32), default='ACTIVE', nullable=False)  # ACTIVE, MATCHED, CLAIMED, CLOSED, RESOLVED
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    category = db.relationship('Category', backref='lost_reports')
    matches = db.relationship('Match', backref='lost_report', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'owner_name': self.owner.full_name if self.owner else None,
            'item_name': self.item_name,
            'category_id': self.category_id,
            'category_name': self.category.name if self.category else None,
            'description': self.description,
            'brand': self.brand,
            'color': self.color,
            'distinguishing_features': self.distinguishing_features,
            'location_text': self.location_text,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'lost_date': self.lost_date.isoformat() if self.lost_date else None,
            'lost_time': self.lost_time.isoformat() if self.lost_time else None,
            'image_path': self.image_path,
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }


class FoundReport(db.Model):
    __tablename__ = 'found_reports'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    
    item_name = db.Column(db.String(128), nullable=False, index=True)
    description = db.Column(db.Text, nullable=False)
    brand = db.Column(db.String(64), nullable=True)
    color = db.Column(db.String(64), nullable=True)
    distinguishing_features = db.Column(db.Text, nullable=True)

    location_text = db.Column(db.String(255), nullable=False)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)

    found_date = db.Column(db.Date, nullable=False)
    found_time = db.Column(db.Time, nullable=True)

    storage_location = db.Column(db.String(255), nullable=True)  # e.g., Campus Security Office Box 4
    image_path = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(32), default='ACTIVE', nullable=False)  # ACTIVE, MATCHED, CLAIMED, CLOSED, RESOLVED
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    category = db.relationship('Category', backref='found_reports')
    verification_questions = db.relationship('VerificationQuestion', backref='found_report', lazy='dynamic', cascade='all, delete-orphan')
    matches = db.relationship('Match', backref='found_report', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'reporter_name': self.reporter.full_name if self.reporter else None,
            'item_name': self.item_name,
            'category_id': self.category_id,
            'category_name': self.category.name if self.category else None,
            'description': self.description,
            'brand': self.brand,
            'color': self.color,
            'distinguishing_features': self.distinguishing_features,
            'location_text': self.location_text,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'found_date': self.found_date.isoformat() if self.found_date else None,
            'found_time': self.found_time.isoformat() if self.found_time else None,
            'storage_location': self.storage_location,
            'image_path': self.image_path,
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }


class Match(db.Model):
    __tablename__ = 'matches'
    __table_args__ = (
        db.UniqueConstraint('lost_report_id', 'found_report_id', name='uq_match_pair'),
    )

    id = db.Column(db.Integer, primary_key=True)
    lost_report_id = db.Column(db.Integer, db.ForeignKey('lost_reports.id'), nullable=False, index=True)
    found_report_id = db.Column(db.Integer, db.ForeignKey('found_reports.id'), nullable=False, index=True)

    text_score = db.Column(db.Float, nullable=False, default=0.0)
    category_score = db.Column(db.Float, nullable=False, default=0.0)
    location_score = db.Column(db.Float, nullable=False, default=0.0)
    time_score = db.Column(db.Float, nullable=False, default=0.0)
    image_score = db.Column(db.Float, nullable=True)  # None if unavailable
    overall_score = db.Column(db.Float, nullable=False, default=0.0)

    confidence_level = db.Column(db.String(20), nullable=False, default='NOT_SUITABLE') # HIGH, MEDIUM, LOW, NOT_SUITABLE
    status = db.Column(db.String(32), default='POSSIBLE', nullable=False) # POSSIBLE, CLAIMED, REJECTED, CONFIRMED, EXPIRED

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    claims = db.relationship('Claim', backref='match', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'lost_report_id': self.lost_report_id,
            'found_report_id': self.found_report_id,
            'lost_item_name': self.lost_report.item_name if self.lost_report else None,
            'found_item_name': self.found_report.item_name if self.found_report else None,
            'lost_user_id': self.lost_report.user_id if self.lost_report else None,
            'scores': {
                'text_score': round(self.text_score, 1),
                'category_score': round(self.category_score, 1),
                'location_score': round(self.location_score, 1),
                'time_score': round(self.time_score, 1),
                'image_score': round(self.image_score, 1) if self.image_score is not None else None,
                'overall_score': round(self.overall_score, 1)
            },
            'confidence_level': self.confidence_level,
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }


class VerificationQuestion(db.Model):
    __tablename__ = 'verification_questions'

    id = db.Column(db.Integer, primary_key=True)
    found_report_id = db.Column(db.Integer, db.ForeignKey('found_reports.id'), nullable=False, index=True)
    question_text = db.Column(db.String(255), nullable=False)
    
    # CRITICAL: expected_answer MUST ONLY BE STORED SERVER-SIDE! NEVER RETURNED TO CLAIMANT!
    expected_answer = db.Column(db.Text, nullable=False)
    question_order = db.Column(db.Integer, default=1)
    is_active = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_public_dict(self):
        # Excludes expected_answer to protect security
        return {
            'id': self.id,
            'question_text': self.question_text,
            'question_order': self.question_order
        }

    def to_admin_dict(self):
        # Internal / admin access only
        return {
            'id': self.id,
            'question_text': self.question_text,
            'expected_answer': self.expected_answer,
            'question_order': self.question_order
        }


class Claim(db.Model):
    __tablename__ = 'claims'

    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey('matches.id'), nullable=False, index=True)
    claimant_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    lost_report_id = db.Column(db.Integer, db.ForeignKey('lost_reports.id'), nullable=False)
    found_report_id = db.Column(db.Integer, db.ForeignKey('found_reports.id'), nullable=False)

    status = db.Column(db.String(32), default='SUBMITTED', nullable=False) # SUBMITTED, UNDER_VERIFICATION, APPROVED, REJECTED
    verification_score = db.Column(db.Float, nullable=True) # % score calculated by answer matcher
    verification_confidence = db.Column(db.String(32), nullable=True) # STRONG_VERIFICATION, PARTIAL_VERIFICATION, WEAK_VERIFICATION

    remarks = db.Column(db.Text, nullable=True) # Additional notes from claimant
    admin_notes = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    lost_report = db.relationship('LostReport', backref='claims')
    found_report = db.relationship('FoundReport', backref='claims')
    answers = db.relationship('ClaimAnswer', backref='claim', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'match_id': self.match_id,
            'claimant_id': self.claimant_id,
            'claimant_name': self.claimant.full_name if self.claimant else None,
            'lost_report_id': self.lost_report_id,
            'found_report_id': self.found_report_id,
            'status': self.status,
            'verification_score': round(self.verification_score, 1) if self.verification_score is not None else None,
            'verification_confidence': self.verification_confidence,
            'remarks': self.remarks,
            'admin_notes': self.admin_notes,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class ClaimAnswer(db.Model):
    __tablename__ = 'claim_answers'

    id = db.Column(db.Integer, primary_key=True)
    claim_id = db.Column(db.Integer, db.ForeignKey('claims.id'), nullable=False, index=True)
    question_id = db.Column(db.Integer, db.ForeignKey('verification_questions.id'), nullable=False)
    answer_text = db.Column(db.Text, nullable=False)
    similarity_score = db.Column(db.Float, nullable=False, default=0.0) # Similarity vs expected answer
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    question = db.relationship('VerificationQuestion')


class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    title = db.Column(db.String(128), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(32), default='INFO') # MATCH_FOUND, CLAIM_SUBMITTED, CLAIM_APPROVED, CLAIM_REJECTED, VERIFICATION_SUBMITTED
    is_read = db.Column(db.Boolean, default=False)

    related_report_id = db.Column(db.Integer, nullable=True)
    related_claim_id = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'message': self.message,
            'type': self.type,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat()
        }


class AuditLog(db.Model):
    __tablename__ = 'audit_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    action = db.Column(db.String(64), nullable=False)
    details = db.Column(db.Text, nullable=False)
    ip_address = db.Column(db.String(45), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User')
