from datetime import datetime
from app.models import db
from app.models.item import ItemReport, ItemImage, Category
from app.models.claim import VerificationQuestion
from app.utils.id_generator import generate_report_id
from app.services.audit_service import log_audit_event
from app.services.matching_service import run_matching_for_report

def create_item_report(user_id, report_type, data, image_paths=None, verification_questions=None):
    report_id_str = generate_report_id()
    
    date_val = datetime.strptime(data['date'], '%Y-%m-%d').date() if isinstance(data['date'], str) else data['date']
    time_val = None
    if data.get('time'):
        if isinstance(data['time'], str):
            time_val = datetime.strptime(data['time'], '%H:%M').time()
        else:
            time_val = data['time']

    status_val = 'REPORTED_LOST' if report_type == 'LOST' else 'REPORTED_FOUND'

    report = ItemReport(
        public_report_id=report_id_str,
        report_type=report_type,
        user_id=user_id,
        category_id=int(data['category_id']),
        item_name=(data.get('item_name') or '').strip(),
        description=(data.get('description') or '').strip(),
        color=(data.get('color') or '').strip(),
        brand=(data.get('brand') or '').strip(),
        distinguishing_features=(data.get('distinguishing_features') or '').strip(),
        location=(data.get('location') or '').strip(),
        date=date_val,
        time=time_val,
        status=status_val
    )
    
    db.session.add(report)
    db.session.flush()  # Obtain report.id

    # Handle images
    if image_paths:
        for path in image_paths:
            img = ItemImage(item_report_id=report.id, file_path=path)
            db.session.add(img)

    # Handle private verification questions (for lost items)
    if verification_questions:
        for vq in verification_questions:
            q_text = vq.get('question', '').strip()
            a_text = vq.get('answer', '').strip()
            if q_text and a_text:
                q_record = VerificationQuestion(
                    item_report_id=report.id,
                    question=q_text,
                    private_expected_answer=a_text
                )
                db.session.add(q_record)

    db.session.commit()

    # Log Audit Event
    log_audit_event(
        user_id=user_id,
        action='REPORT_CREATED',
        entity_type='ItemReport',
        entity_id=report.id,
        description=f"Created {report_type} report {report.public_report_id} ('{report.item_name}')"
    )

    # Trigger matching engine
    run_matching_for_report(report)

    return report


def get_filtered_reports(report_type=None, category_id=None, query=None, location=None, status=None, user_id=None):
    q = ItemReport.query
    if report_type:
        q = q.filter(ItemReport.report_type == report_type)
    if category_id:
        q = q.filter(ItemReport.category_id == category_id)
    if status:
        q = q.filter(ItemReport.status == status)
    if user_id:
        q = q.filter(ItemReport.user_id == user_id)
    if location:
        q = q.filter(ItemReport.location.ilike(f"%{location}%"))
    if query:
        search_pattern = f"%{query}%"
        q = q.filter(
            (ItemReport.item_name.ilike(search_pattern)) |
            (ItemReport.description.ilike(search_pattern)) |
            (ItemReport.public_report_id.ilike(search_pattern)) |
            (ItemReport.brand.ilike(search_pattern))
        )
    return q.order_by(ItemReport.created_at.desc()).all()
