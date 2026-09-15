from datetime import datetime
from app.models import db

class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    reports = db.relationship('ItemReport', backref='category', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name
        }


class ItemReport(db.Model):
    __tablename__ = 'item_reports'

    id = db.Column(db.Integer, primary_key=True)
    public_report_id = db.Column(db.String(30), unique=True, nullable=False, index=True)
    report_type = db.Column(db.String(10), nullable=False)  # LOST or FOUND
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    
    item_name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    color = db.Column(db.String(50), nullable=True)
    brand = db.Column(db.String(100), nullable=True)
    distinguishing_features = db.Column(db.Text, nullable=True)
    location = db.Column(db.String(200), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=True)
    
    # Status lifecycle:
    # REPORTED_LOST, REPORTED_FOUND, POSSIBLE_MATCH, CLAIM_SUBMITTED, UNDER_VERIFICATION, CLAIM_APPROVED, CLAIM_REJECTED, HANDOVER_PENDING, RETURNED, CLOSED
    status = db.Column(db.String(30), nullable=False, default='REPORTED_LOST')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    images = db.relationship('ItemImage', backref='item_report', cascade='all, delete-orphan', lazy=True)
    verification_questions = db.relationship('VerificationQuestion', backref='item_report', cascade='all, delete-orphan', lazy=True)
    claims = db.relationship('Claim', backref='found_report', foreign_keys='Claim.found_report_id', cascade='all, delete-orphan', lazy=True)
    handovers = db.relationship('Handover', backref='report', cascade='all, delete-orphan', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'public_report_id': self.public_report_id,
            'report_type': self.report_type,
            'user_id': self.user_id,
            'category_id': self.category_id,
            'category_name': self.category.name if self.category else None,
            'item_name': self.item_name,
            'description': self.description,
            'color': self.color,
            'brand': self.brand,
            'distinguishing_features': self.distinguishing_features,
            'location': self.location,
            'date': self.date.strftime('%Y-%m-%d') if self.date else None,
            'time': self.time.strftime('%H:%M') if self.time else None,
            'status': self.status,
            'images': [img.file_path for img in self.images],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class ItemImage(db.Model):
    __tablename__ = 'item_images'

    id = db.Column(db.Integer, primary_key=True)
    item_report_id = db.Column(db.Integer, db.ForeignKey('item_reports.id'), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
