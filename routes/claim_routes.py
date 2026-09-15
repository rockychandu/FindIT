from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from models import db, Claim, Match, VerificationQuestion, FoundReport
from verification.claim_service import ClaimService

claim_bp = Blueprint('claim', __name__)

@claim_bp.route('/api/claims/submit', methods=['POST'])
@login_required
def api_submit_claim():
    """
    REST API: Submit a claim for a match pair.
    """
    if request.is_json:
        data = request.get_json()
        match_id = data.get('match_id')
        remarks = data.get('remarks', '')
    else:
        match_id = request.form.get('match_id', type=int)
        remarks = request.form.get('remarks', '')

    if not match_id:
        return jsonify({'error': 'match_id is required.'}), 400

    service = ClaimService()

    try:
        claim = service.submit_claim(match_id=match_id, claimant_id=current_user.id, remarks=remarks)

        if request.is_json:
            return jsonify({
                'message': 'Claim submitted successfully.',
                'claim': claim.to_dict()
            }), 201

        flash("Claim submitted! Please complete the verification questions.", "success")
        return redirect(url_for('claim.verify_claim_view', claim_id=claim.id))

    except ValueError as e:
        if request.is_json:
            return jsonify({'error': str(e)}), 400
        flash(str(e), "danger")
        return redirect(url_for('match.match_details', match_id=match_id))
    except PermissionError as e:
        if request.is_json:
            return jsonify({'error': str(e)}), 403
        flash(str(e), "danger")
        return redirect(url_for('match.possible_matches'))


@claim_bp.route('/api/claims/<int:claim_id>', methods=['GET'])
@login_required
def api_get_claim(claim_id):
    """
    REST API: Fetch claim status and verification questions.
    CRITICAL SECURITY ENFORCEMENT: Expected answers are NEVER exposed in the JSON response!
    """
    claim = Claim.query.get_or_404(claim_id)

    # IDOR Check: Must be claimant or admin
    if not current_user.is_admin and claim.claimant_id != current_user.id:
        return jsonify({'error': 'Unauthorized access to claim.'}), 403

    questions = VerificationQuestion.query.filter_by(
        found_report_id=claim.found_report_id,
        is_active=True
    ).order_by(VerificationQuestion.question_order).all()

    # Public question dicts (NO expected_answer!)
    public_questions = [q.to_public_dict() for q in questions]

    return jsonify({
        'claim': claim.to_dict(),
        'verification_questions': public_questions
    }), 200


@claim_bp.route('/api/claims/<int:claim_id>/verify', methods=['POST'])
@login_required
def api_verify_claim(claim_id):
    """
    REST API: Submit answers to private verification questions.
    Calculates answer similarity and updates claim verification status.
    """
    if request.is_json:
        data = request.get_json()
        answers_dict = {int(k): str(v) for k, v in data.get('answers', {}).items()}
    else:
        # Form submission
        answers_dict = {}
        for key in request.form:
            if key.startswith('question_'):
                q_id = int(key.split('_')[1])
                answers_dict[q_id] = request.form.get(key)

    service = ClaimService()

    try:
        claim = service.submit_verification_answers(
            claim_id=claim_id,
            claimant_id=current_user.id,
            answers_dict=answers_dict
        )

        if request.is_json:
            return jsonify({
                'message': 'Verification answers evaluated and claim submitted for admin review.',
                'claim': claim.to_dict()
            }), 200

        flash(f"Verification submitted! Verification score: {claim.verification_score}% ({claim.verification_confidence}). Under admin review.", "success")
        return redirect(url_for('claim.claim_status_view', claim_id=claim.id))

    except ValueError as e:
        if request.is_json:
            return jsonify({'error': str(e)}), 400
        flash(str(e), "danger")
        return redirect(url_for('claim.verify_claim_view', claim_id=claim_id))
    except PermissionError as e:
        if request.is_json:
            return jsonify({'error': str(e)}), 403
        flash(str(e), "danger")
        return redirect(url_for('claim.my_claims_view'))


@claim_bp.route('/api/claims/my-claims', methods=['GET'])
@login_required
def api_my_claims():
    claims = Claim.query.filter_by(claimant_id=current_user.id).order_by(Claim.created_at.desc()).all()
    return jsonify({'claims': [c.to_dict() for c in claims]}), 200


# --- FRONTEND UI VIEWS ---

@claim_bp.route('/claims/verify/<int:claim_id>')
@login_required
def verify_claim_view(claim_id):
    """
    UI View: Verification form displaying owner-provided questions.
    SECURITY: Expected answers are NOT passed to template context.
    """
    claim = Claim.query.get_or_404(claim_id)

    if not current_user.is_admin and claim.claimant_id != current_user.id:
        flash("Unauthorized access.", "danger")
        return redirect(url_for('claim.my_claims_view'))

    questions = VerificationQuestion.query.filter_by(
        found_report_id=claim.found_report_id,
        is_active=True
    ).order_by(VerificationQuestion.question_order).all()

    # Create public list without expected_answer
    public_questions = [q.to_public_dict() for q in questions]

    return render_template('claims/verify.html', claim=claim, questions=public_questions)


@claim_bp.route('/claims/status/<int:claim_id>')
@login_required
def claim_status_view(claim_id):
    """
    UI View: Real-time claim status tracking.
    """
    claim = Claim.query.get_or_404(claim_id)

    if not current_user.is_admin and claim.claimant_id != current_user.id:
        flash("Unauthorized access.", "danger")
        return redirect(url_for('claim.my_claims_view'))

    return render_template('claims/status.html', claim=claim)


@claim_bp.route('/claims/my-claims')
@login_required
def my_claims_view():
    claims = Claim.query.filter_by(claimant_id=current_user.id).order_by(Claim.created_at.desc()).all()
    return render_template('claims/my_claims.html', claims=claims)
