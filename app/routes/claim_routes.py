from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.auth.decorators import login_required, get_current_user
from app.models.item import ItemReport
from app.models.claim import Claim, VerificationQuestion
from app.models.handover import Handover
from app.models.match import Match
from app.services.claim_service import (
    submit_claim,
    finder_confirm_submission,
    claimant_confirm_collection
)

claim_bp = Blueprint('claim', __name__)

@claim_bp.route('/claim/<int:found_report_id>', methods=['GET', 'POST'])
@login_required
def submit_claim_page(found_report_id):
    user = get_current_user()
    found_item = ItemReport.query.get_or_404(found_report_id)

    if found_item.report_type != 'FOUND':
        flash('Claims can only be submitted for reported found items.', 'danger')
        return redirect(url_for('main.reports'))

    if found_item.user_id == user.id:
        flash('You cannot claim an item you reported as found.', 'warning')
        return redirect(url_for('item.view_report', report_id=found_item.id))

    # Identify user's matching lost report if any
    match_record = Match.query.filter_by(
        found_report_id=found_item.id
    ).filter(Match.lost_report.has(user_id=user.id)).first()

    lost_report_id = match_record.lost_report_id if match_record else None
    
    # Retrieve private verification questions associated with lost item (if match exists) or general questions
    verification_questions = []
    if lost_report_id:
        vqs = VerificationQuestion.query.filter_by(item_report_id=lost_report_id).all()
        # Strictly call to_public_dict() so private expected answers are NEVER sent to the view
        verification_questions = [q.to_public_dict() for q in vqs]

    if request.method == 'POST':
        responses_data = []
        for q in verification_questions:
            answer_text = request.form.get(f"question_{q['id']}", '')
            responses_data.append({
                'question_id': q['id'],
                'answer': answer_text
            })

        try:
            claim = submit_claim(
                claimant_id=user.id,
                found_report_id=found_item.id,
                lost_report_id=lost_report_id,
                responses_data=responses_data
            )
            flash('Your verification has been submitted to the college authority!', 'success')
            return redirect(url_for('claim.case_status', claim_id=claim.id))
        except ValueError as ve:
            flash(str(ve), 'danger')
        except Exception as e:
            flash(f"Error submitting claim: {str(e)}", 'danger')

    return render_template(
        'user/claim_form.html',
        found_item=found_item,
        questions=verification_questions,
        match_record=match_record
    )


@claim_bp.route('/claims')
@login_required
def my_claims():
    user = get_current_user()
    claims_list = Claim.query.filter_by(claimant_id=user.id).order_by(Claim.submitted_at.desc()).all()
    return render_template('user/claims.html', claims=claims_list)


@claim_bp.route('/claim/status/<int:claim_id>')
@login_required
def case_status(claim_id):
    user = get_current_user()
    claim = Claim.query.get_or_404(claim_id)

    # Security check: User must be claimant, reporter of found item, or admin
    is_claimant = (claim.claimant_id == user.id)
    is_finder = (claim.found_report and claim.found_report.user_id == user.id)

    if not is_claimant and not is_finder and not user.is_admin:
        flash('You are not authorized to view this case status.', 'danger')
        return redirect(url_for('main.dashboard'))

    handover = Handover.query.filter_by(claim_id=claim.id).first()

    return render_template(
        'user/case_status.html',
        claim=claim,
        handover=handover,
        is_claimant=is_claimant,
        is_finder=is_finder,
        user=user
    )


@claim_bp.route('/claim/confirm-finder-submission/<int:handover_id>', methods=['POST'])
@login_required
def confirm_finder_submission(handover_id):
    user = get_current_user()
    try:
        handover = finder_confirm_submission(handover_id, user.id)
        flash('Thank you! Your confirmation to submit the item to the college authority has been recorded.', 'success')
        return redirect(url_for('claim.case_status', claim_id=handover.claim_id))
    except Exception as e:
        flash(f"Error confirming submission: {str(e)}", 'danger')
        return redirect(url_for('main.dashboard'))


@claim_bp.route('/claim/confirm-claimant-collection/<int:handover_id>', methods=['POST'])
@login_required
def confirm_claimant_collection(handover_id):
    user = get_current_user()
    try:
        handover = claimant_confirm_collection(handover_id, user.id)
        flash('Collection request confirmed! Please visit the college authority office to receive your item.', 'success')
        return redirect(url_for('claim.case_status', claim_id=handover.claim_id))
    except Exception as e:
        flash(f"Error confirming collection: {str(e)}", 'danger')
        return redirect(url_for('main.dashboard'))

