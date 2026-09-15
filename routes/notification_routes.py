from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from services.notification_service import NotificationService

notification_bp = Blueprint('notification', __name__)

@notification_bp.route('/api/notifications', methods=['GET'])
@login_required
def get_notifications():
    unread_only = request.args.get('unread', 'false').lower() == 'true'
    notifications = NotificationService.get_user_notifications(current_user.id, unread_only=unread_only)
    return jsonify({
        'notifications': [n.to_dict() for n in notifications],
        'unread_count': len([n for n in notifications if not n.is_read])
    }), 200


@notification_bp.route('/api/notifications/<int:notif_id>/read', methods=['POST'])
@login_required
def mark_read(notif_id):
    success = NotificationService.mark_as_read(notif_id, current_user.id)
    if success:
        return jsonify({'message': 'Notification marked as read.'}), 200
    return jsonify({'error': 'Notification not found.'}), 404
