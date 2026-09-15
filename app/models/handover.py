from datetime import datetime
from app.models import db

class Handover(db.Model):
    __tablename__ = 'handovers'

    id = db.Column(db.Integer, primary_key=True)
    report_id = db.Column(db.Integer, db.ForeignKey('item_reports.id'), nullable=False)
    claim_id = db.Column(db.Integer, db.ForeignKey('claims.id'), nullable=False)
    claimant_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    authorized_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    location = db.Column(db.String(255), nullable=True, default='College Lost & Found Office')
    scheduled_date = db.Column(db.String(50), nullable=True)
    scheduled_time = db.Column(db.String(50), nullable=True)

    found_person_submitted = db.Column(db.Boolean, default=False)
    authority_received = db.Column(db.Boolean, default=False)
    lost_person_collected = db.Column(db.Boolean, default=False)

    handover_date = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text, nullable=True)
    
    # Status: PENDING, FOUND_SUBMITTED, RECEIVED_BY_AUTHORITY, READY_FOR_COLLECTION, COMPLETED
    status = db.Column(db.String(30), nullable=False, default='PENDING')

    # Relationships
    authorizer = db.relationship('User', foreign_keys=[authorized_by], backref='authorized_handovers')
    claimant = db.relationship('User', foreign_keys=[claimant_id], backref='received_handovers')

    def to_dict(self):
        return {
            'id': self.id,
            'report_id': self.report_id,
            'claim_id': self.claim_id,
            'claimant_id': self.claimant_id,
            'claimant_name': self.claimant.name if self.claimant else None,
            'authorized_by_name': self.authorizer.name if self.authorizer else None,
            'location': self.location,
            'scheduled_date': self.scheduled_date,
            'scheduled_time': self.scheduled_time,
            'found_person_submitted': self.found_person_submitted,
            'authority_received': self.authority_received,
            'lost_person_collected': self.lost_person_collected,
            'handover_date': self.handover_date.isoformat() if self.handover_date else None,
            'notes': self.notes,
            'status': self.status
        }
