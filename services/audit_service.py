from models import db, AuditLog

class AuditService:
    """Service to log security and system actions for Member 3 administrative audit trail."""

    @staticmethod
    def log_action(user_id: int | None, action: str, details: str, ip_address: str = None) -> AuditLog:
        log = AuditLog(
            user_id=user_id,
            action=action,
            details=details,
            ip_address=ip_address
        )
        db.session.add(log)
        db.session.commit()
        return log

    @staticmethod
    def get_recent_logs(limit: int = 50) -> list[AuditLog]:
        return AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(limit).all()
