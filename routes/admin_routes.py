from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from models import db, Claim, AuditLog, Match
from verification.claim_service import ClaimService
from services.audit_service import AuditService

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            if request.is_json:
                return jsonify({'error': 'Admin privileges required.'}), 403
            flash("Admin privileges required.", "danger")
            return redirect(url_for('report.dashboard'))
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    pending_claims = Claim.query.filter(Claim.status.in_(['SUBMITTED', 'UNDER_VERIFICATION'])).order_by(Claim.created_at.desc()).all()
    recent_claims = Claim.query.order_by(Claim.created_at.desc()).limit(20).all()
    audit_logs = AuditService.get_recent_logs(30)

    return render_template('admin/dashboard.html', pending_claims=pending_claims, recent_claims=recent_claims, audit_logs=audit_logs)


@admin_bp.route('/admin/claims/<int:claim_id>/review', methods=['GET', 'POST'])
@login_required
@admin_required
def review_claim(claim_id):
    claim = Claim.query.get_or_404(claim_id)
    service = ClaimService()

    if request.method == 'POST':
        action = request.form.get('action') # 'approve' or 'reject'
        admin_notes = request.form.get('admin_notes', '')

        approved = (action == 'approve')
        service.review_claim_admin(claim_id=claim.id, admin_id=current_user.id, approved=approved, admin_notes=admin_notes)

        status_str = "APPROVED" if approved else "REJECTED"
        flash(f"Claim #{claim.id} has been {status_str}.", "success" if approved else "info")
        return redirect(url_for('admin.admin_dashboard'))

    # Admin view can inspect full question and answer breakdown
    answers_breakdown = []
    for ans in claim.answers:
        q = ans.question
        answers_breakdown.append({
            'question_text': q.question_text,
            'expected_answer': q.expected_answer,  # Privileged admin view
            'claimant_answer': ans.answer_text,
            'similarity_score': round(ans.similarity_score, 1)
        })

    return render_template('admin/review_claim.html', claim=claim, answers_breakdown=answers_breakdown)
