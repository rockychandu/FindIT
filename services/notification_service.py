from models import db, Notification

class NotificationService:
    """Service to create and manage system notifications."""

    @staticmethod
    def create_notification(user_id: int, title: str, message: str, type_: str = "INFO", report_id: int = None, claim_id: int = None) -> Notification:
        notif = Notification(
            user_id=user_id,
            title=title,
            message=message,
            type=type_,
            related_report_id=report_id,
            related_claim_id=claim_id
        )
        db.session.add(notif)
        db.session.commit()
        return notif

    @staticmethod
    def get_user_notifications(user_id: int, unread_only: bool = False) -> list[Notification]:
        query = Notification.query.filter_by(user_id=user_id)
        if unread_only:
            query = query.filter_by(is_read=False)
        return query.order_by(Notification.created_at.desc()).all()

    @staticmethod
    def mark_as_read(notification_id: int, user_id: int) -> bool:
        notif = Notification.query.filter_by(id=notification_id, user_id=user_id).first()
        if notif:
            notif.is_read = True
            db.session.commit()
            return True
        return False
