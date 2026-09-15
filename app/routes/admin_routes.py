import csv
import io
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, Response
from app.auth.decorators import admin_required, get_current_user
from app.models import db
from app.models.user import User
from app.models.item import ItemReport, Category
from app.models.match import Match
from app.models.claim import Claim, VerificationQuestion, VerificationResponse
from app.models.handover import Handover
from app.models.audit import AuditLog
from app.services.claim_service import (
    process_claim_decision,
    complete_handover,
    authority_receive_item
)
from app.services.audit_service import log_audit_event

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    # Calculated real metrics from database
    total_lost = ItemReport.query.filter_by(report_type='LOST').count()
    total_found = ItemReport.query.filter_by(report_type='FOUND').count()
    total_matches = Match.query.count()
    pending_claims = Claim.query.filter(Claim.status.in_(['SUBMITTED', 'UNDER_VERIFICATION', 'AWAITING_AUTHORITY_DECISION'])).count()
    pending_handovers = Handover.query.filter(Handover.status.in_(['PENDING', 'FOUND_SUBMITTED', 'RECEIVED_BY_AUTHORITY'])).count()
    returned_items = ItemReport.query.filter_by(status='RETURNED').count()
    approved_cases = Claim.query.filter_by(status='CLAIM_APPROVED').count()
    rejected_cases = Claim.query.filter_by(status='CLAIM_REJECTED').count()
    closed_cases = Claim.query.filter_by(status='CLOSED').count()

    recent_claims = Claim.query.order_by(Claim.submitted_at.desc()).limit(5).all()
    recent_audit = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(10).all()

    return render_template(
        'admin/dashboard.html',
        total_lost=total_lost,
        total_found=total_found,
        total_matches=total_matches,
        pending_claims=pending_claims,
        pending_handovers=pending_handovers,
        returned_items=returned_items,
        approved_cases=approved_cases,
        rejected_cases=rejected_cases,
        closed_cases=closed_cases,
        recent_claims=recent_claims,
        recent_audit=recent_audit
    )


@admin_bp.route('/reports')
@admin_required
def reports():
    report_type = request.args.get('type')
    status = request.args.get('status')
    query = request.args.get('q')

    q = ItemReport.query
    if report_type:
        q = q.filter_by(report_type=report_type)
    if status:
        q = q.filter_by(status=status)
    if query:
        search_pattern = f"%{query}%"
        q = q.filter(
            (ItemReport.item_name.ilike(search_pattern)) |
            (ItemReport.public_report_id.ilike(search_pattern)) |
            (ItemReport.location.ilike(search_pattern))
        )
    
    all_reports = q.order_by(ItemReport.created_at.desc()).all()
    return render_template('admin/reports.html', reports=all_reports, selected_type=report_type, selected_status=status, query=query)


@admin_bp.route('/export/reports')
@admin_required
def export_reports_csv():
    reports = ItemReport.query.order_by(ItemReport.created_at.desc()).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Public Report ID', 'Type', 'Item Name', 'Category', 'Reporter Name', 'Location', 'Date', 'Status'])
    
    for r in reports:
        writer.writerow([
            r.public_report_id,
            r.report_type,
            r.item_name,
            r.category.name if r.category else '',
            r.reporter.name if r.reporter else '',
            r.location,
            r.date.strftime('%Y-%m-%d') if r.date else '',
            r.status
        ])
    
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment;filename=findit_campus_reports.csv'}
    )


@admin_bp.route('/export/audit')
@admin_required
def export_audit_csv():
    logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Timestamp', 'User', 'Action', 'Entity Type', 'Entity ID', 'Description'])
    
    for l in logs:
        writer.writerow([
            l.timestamp.strftime('%Y-%m-%d %H:%M:%S') if l.timestamp else '',
            l.user.name if l.user else 'System',
            l.action,
            l.entity_type,
            l.entity_id or '',
            l.description
        ])

    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment;filename=findit_audit_logs.csv'}
    )


@admin_bp.route('/matches')
@admin_required
def matches():
    all_matches = Match.query.order_by(Match.overall_score.desc()).all()
    return render_template('admin/matches.html', matches=all_matches)


@admin_bp.route('/claims')
@admin_required
def claims():
    status_filter = request.args.get('status')
    q = Claim.query
    if status_filter:
        q = q.filter_by(status=status_filter)
    all_claims = q.order_by(Claim.submitted_at.desc()).all()
    return render_template('admin/claims.html', claims=all_claims, status_filter=status_filter)


@admin_bp.route('/claim/<int:claim_id>', methods=['GET', 'POST'])
@admin_required
def claim_review(claim_id):
    admin_user = get_current_user()
    claim = Claim.query.get_or_404(claim_id)

    found_report = claim.found_report
    lost_report = ItemReport.query.get(claim.lost_report_id) if claim.lost_report_id else None

    # Fetch Match score breakdown if available
    match_record = None
    if lost_report and found_report:
        match_record = Match.query.filter_by(
            lost_report_id=lost_report.id,
            found_report_id=found_report.id
        ).first()

    # Fetch verification responses paired with private expected answers for admin inspection
    responses = VerificationResponse.query.filter_by(claim_id=claim.id).all()
    qa_review_data = []
    for resp in responses:
        vq = VerificationQuestion.query.get(resp.question_id)
        qa_review_data.append({
            'question': vq.question if vq else 'Verification Question',
            'expected_answer': vq.private_expected_answer if vq else 'N/A',
            'claimant_response': resp.response,
            'similarity_score': round(resp.similarity_score * 100, 1)
        })

    # Fetch existing handover object if any
    handover = Handover.query.filter_by(claim_id=claim.id).first()

    # Timeline audit events for this case
    audit_events = AuditLog.query.filter(
        (AuditLog.entity_id == claim.id) |
        (AuditLog.entity_id == found_report.id) |
        (lost_report and (AuditLog.entity_id == lost_report.id))
    ).order_by(AuditLog.timestamp.asc()).all()

    if request.method == 'POST':
        action = request.form.get('action')
        reason = request.form.get('decision_reason', '')
        location = request.form.get('location', 'College Lost & Found Office')
        scheduled_date = request.form.get('scheduled_date', 'Next Working Day')
        scheduled_time = request.form.get('scheduled_time', '10:00 AM - 4:00 PM')
        notes = request.form.get('notes', '')

        try:
            if action in ['approve', 'reject']:
                if not reason.strip() and action == 'reject':
                    flash('Please provide a decision reason for rejection.', 'warning')
                    return redirect(url_for('admin.claim_review', claim_id=claim.id))
                
                approved = (action == 'approve')
                process_claim_decision(
                    claim_id=claim.id,
                    admin_id=admin_user.id,
                    approved=approved,
                    decision_reason=reason or ("Verified by Authority." if approved else "Rejection rationale provided."),
                    location=location,
                    scheduled_date=scheduled_date,
                    scheduled_time=scheduled_time
                )
                status_text = 'APPROVED' if approved else 'REJECTED'
                flash(f"Claim #{claim.id} successfully marked as {status_text}.", 'success')
                return redirect(url_for('admin.claim_review', claim_id=claim.id))

            elif action == 'receive_item':
                if not handover:
                    flash('No active handover record found for this claim.', 'danger')
                    return redirect(url_for('admin.claim_review', claim_id=claim.id))
                authority_receive_item(handover.id, admin_user.id, condition_notes=notes or "Received in good condition")
                flash('Item physically received by authority! Lost person has been notified for collection.', 'success')
                return redirect(url_for('admin.claim_review', claim_id=claim.id))

            elif action == 'finalize_handover':
                if not handover:
                    flash('No active handover record found for this claim.', 'danger')
                    return redirect(url_for('admin.claim_review', claim_id=claim.id))
                complete_handover(handover.id, admin_user.id, notes=notes or "Final physical handover confirmed by authority.")
                flash('Final handover completed! Case is now RETURNED and CLOSED.', 'success')
                return redirect(url_for('admin.claim_review', claim_id=claim.id))

            else:
                flash('Invalid action requested.', 'danger')

        except Exception as e:
            flash(f"Error processing decision: {str(e)}", 'danger')

    return render_template(
        'admin/claim_review.html',
        claim=claim,
        lost_report=lost_report,
        found_report=found_report,
        match_record=match_record,
        qa_review_data=qa_review_data,
        handover=handover,
        audit_events=audit_events
    )



@admin_bp.route('/handover', methods=['GET', 'POST'])
@admin_required
def handover():
    admin_user = get_current_user()
    pending_handovers = Handover.query.filter_by(status='PENDING').order_by(Handover.handover_date.desc()).all()
    completed_handovers = Handover.query.filter_by(status='COMPLETED').order_by(Handover.handover_date.desc()).all()

    if request.method == 'POST':
        handover_id = request.form.get('handover_id', type=int)
        notes = request.form.get('notes', '')

        if not handover_id:
            flash('Please select a valid handover record.', 'danger')
            return redirect(url_for('admin.handover'))

        try:
            complete_handover(handover_id, admin_user.id, notes)
            flash('Physical item handover recorded successfully! Case is now closed and marked RETURNED.', 'success')
            return redirect(url_for('admin.handover'))
        except Exception as e:
            flash(f"Error processing handover: {str(e)}", 'danger')

    return render_template('admin/handover.html', pending_handovers=pending_handovers, completed_handovers=completed_handovers)


@admin_bp.route('/audit')
@admin_required
def audit():
    logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(100).all()
    return render_template('admin/audit.html', logs=logs)
