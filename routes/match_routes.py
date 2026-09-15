from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from models import db, Match, LostReport, FoundReport
from matching.match_service import MatchService
from matching.ranking import MatchRanker

match_bp = Blueprint('match', __name__)

@match_bp.route('/api/matches', methods=['GET'])
@login_required
def api_get_matches():
    """
    REST API: Fetch matches filtered by confidence, report ID, status, and sorted.
    Includes IDOR authorization check.
    """
    confidence = request.args.get('confidence')
    status = request.args.get('status', 'POSSIBLE')
    report_id = request.args.get('report_id', type=int)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    query = Match.query

    # Non-admin users can only view matches involving their own lost reports
    if not current_user.is_admin:
        my_lost_ids = [r.id for r in LostReport.query.filter_by(user_id=current_user.id).all()]
        query = query.filter(Match.lost_report_id.in_(my_lost_ids))

    if report_id:
        query = query.filter(Match.lost_report_id == report_id)

    if confidence:
        query = query.filter(Match.confidence_level == confidence.upper())

    if status:
        query = query.filter(Match.status == status.upper())

    pagination = query.order_by(Match.overall_score.desc()).paginate(page=page, per_page=per_page, error_out=False)

    matches_data = [m.to_dict() for m in pagination.items]

    return jsonify({
        'matches': matches_data,
        'total': pagination.total,
        'page': pagination.page,
        'pages': pagination.pages,
        'has_next': pagination.has_next,
        'has_prev': pagination.has_prev
    }), 200


@match_bp.route('/api/matches/<int:match_id>', methods=['GET'])
@login_required
def api_get_match_detail(match_id):
    """
    REST API: Get detailed score breakdown for a specific match.
    Enforces authorization to prevent IDOR.
    """
    match = Match.query.get_or_404(match_id)

    # IDOR Protection: User must own the lost report or be an admin
    if not current_user.is_admin and match.lost_report.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized access to match details.'}), 403

    return jsonify(match.to_dict()), 200


@match_bp.route('/api/matches/run', methods=['POST'])
@login_required
def api_run_matching():
    """
    REST API: Execute matching engine for a lost report or all active reports.
    """
    data = request.get_json() or {}
    report_id = data.get('lost_report_id')

    matcher = MatchService()

    if report_id:
        lost_report = LostReport.query.get(report_id)
        if not lost_report:
            return jsonify({'error': 'Lost report not found.'}), 404
        if not current_user.is_admin and lost_report.user_id != current_user.id:
            return jsonify({'error': 'Unauthorized.'}), 403

        matches = matcher.run_matches_for_lost_report(report_id)
        return jsonify({
            'message': f'Matching completed. Generated {len(matches)} match(es).',
            'count': len(matches)
        }), 200
    else:
        # Run across all
        count = matcher.run_all_matches()
        return jsonify({
            'message': f'Matching engine executed across all reports. {count} match(es) evaluated.',
            'count': count
        }), 200


@match_bp.route('/api/matches/<int:match_id>/refresh', methods=['POST'])
@login_required
def api_refresh_match(match_id):
    """
    REST API: Re-evaluates signal scores for a specific match pair.
    """
    match = Match.query.get_or_404(match_id)

    if not current_user.is_admin and match.lost_report.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized.'}), 403

    matcher = MatchService()
    res = matcher.evaluate_pair(match.lost_report, match.found_report)

    match.text_score = res['text_score']
    match.category_score = res['category_score']
    match.location_score = res['location_score']
    match.time_score = res['time_score']
    match.image_score = res['image_score']
    match.overall_score = res['overall_score']
    match.confidence_level = res['confidence_level']

    db.session.commit()

    return jsonify({
        'message': 'Match scores re-calculated successfully.',
        'match': match.to_dict()
    }), 200


# --- FRONTEND UI VIEWS ---

@match_bp.route('/matches/possible')
@login_required
def possible_matches():
    """
    UI View: Displays list of possible matches with score breakdown badges.
    """
    report_id = request.args.get('report_id', type=int)
    confidence = request.args.get('confidence')

    query = Match.query.filter(Match.status == 'POSSIBLE')

    if not current_user.is_admin:
        my_lost_ids = [r.id for r in LostReport.query.filter_by(user_id=current_user.id).all()]
        query = query.filter(Match.lost_report_id.in_(my_lost_ids))

    if report_id:
        query = query.filter(Match.lost_report_id == report_id)

    if confidence:
        query = query.filter(Match.confidence_level == confidence.upper())

    matches = query.order_by(Match.overall_score.desc()).all()

    return render_template('matches/possible_matches.html', matches=matches, filter_report_id=report_id)


@match_bp.route('/matches/<int:match_id>')
@login_required
def match_details(match_id):
    """
    UI View: Match Details page showing public info, score breakdown, and claim submit button.
    Does NOT leak private verification answers.
    """
    match = Match.query.get_or_404(match_id)

    # Authorization Check
    if not current_user.is_admin and match.lost_report.user_id != current_user.id:
        flash("You are not authorized to view this match.", "danger")
        return redirect(url_for('match.possible_matches'))

    return render_template('matches/match_details.html', match=match)
