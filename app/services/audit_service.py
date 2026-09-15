from app.models import db
from app.models.audit import AuditLog

def log_audit_event(user_id, action, entity_type, entity_id, description):
    try:
        log = AuditLog(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            description=description
        )
        db.session.add(log)
        db.session.commit()
        return log
    except Exception as e:
        db.session.rollback()
        # Log failure silently without breaking caller
        return None
