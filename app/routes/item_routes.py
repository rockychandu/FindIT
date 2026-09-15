from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.auth.decorators import login_required, get_current_user
from app.models import db
from app.models.item import ItemReport, Category
from app.models.match import Match
from app.validators.report_validator import validate_report_data
from app.utils.file_handler import save_uploaded_file
from app.services.item_service import create_item_report

item_bp = Blueprint('item', __name__)

@item_bp.route('/report-lost', methods=['GET', 'POST'])
@login_required
def report_lost():
    user = get_current_user()
    categories = Category.query.all()

    if request.method == 'POST':
        form_data = {
            'item_name': request.form.get('item_name'),
            'category_id': request.form.get('category_id'),
            'description': request.form.get('description'),
            'color': request.form.get('color'),
            'brand': request.form.get('brand'),
            'distinguishing_features': request.form.get('distinguishing_features'),
            'location': request.form.get('location'),
            'date': request.form.get('date'),
            'time': request.form.get('time')
        }

        errors = validate_report_data(form_data, is_lost=True)
        if errors:
            for err in errors:
                flash(err, 'danger')
            return render_template('user/report_lost.html', categories=categories, form=form_data)

        # Handle image upload
        image_paths = []
        file_obj = request.files.get('image')
        if file_obj and file_obj.filename != '':
            try:
                saved_path = save_uploaded_file(file_obj)
                if saved_path:
                    image_paths.append(saved_path)
            except ValueError as ve:
                flash(str(ve), 'danger')
                return render_template('user/report_lost.html', categories=categories, form=form_data)

        # Handle Private Verification Questions & Answers
        questions = request.form.getlist('question[]') or request.form.getlist('question')
        answers = request.form.getlist('answer[]') or request.form.getlist('answer')
        verification_questions = []
        for q, a in zip(questions, answers):
            if q.strip() and a.strip():
                verification_questions.append({'question': q, 'answer': a})

        try:
            report = create_item_report(
                user_id=user.id,
                report_type='LOST',
                data=form_data,
                image_paths=image_paths,
                verification_questions=verification_questions
            )
            flash(f"Lost item report created successfully! Report ID: {report.public_report_id}", 'success')
            return redirect(url_for('item.view_report', report_id=report.id))
        except Exception as e:
            flash(f"Error creating report: {str(e)}", 'danger')

    return render_template('user/report_lost.html', categories=categories, form={})


@item_bp.route('/report-found', methods=['GET', 'POST'])
@login_required
def report_found():
    user = get_current_user()
    categories = Category.query.all()

    if request.method == 'POST':
        form_data = {
            'item_name': request.form.get('item_name'),
            'category_id': request.form.get('category_id'),
            'description': request.form.get('description'),
            'color': request.form.get('color'),
            'brand': request.form.get('brand'),
            'distinguishing_features': request.form.get('distinguishing_features'),
            'location': request.form.get('location'),
            'date': request.form.get('date'),
            'time': request.form.get('time')
        }

        errors = validate_report_data(form_data, is_lost=False)
        if errors:
            for err in errors:
                flash(err, 'danger')
            return render_template('user/report_found.html', categories=categories, form=form_data)

        # Handle image upload
        image_paths = []
        file_obj = request.files.get('image')
        if file_obj and file_obj.filename != '':
            try:
                saved_path = save_uploaded_file(file_obj)
                if saved_path:
                    image_paths.append(saved_path)
            except ValueError as ve:
                flash(str(ve), 'danger')
                return render_template('user/report_found.html', categories=categories, form=form_data)

        try:
            report = create_item_report(
                user_id=user.id,
                report_type='FOUND',
                data=form_data,
                image_paths=image_paths
            )
            flash(f"Found item report registered successfully! Report ID: {report.public_report_id}", 'success')
            return redirect(url_for('item.view_report', report_id=report.id))
        except Exception as e:
            flash(f"Error creating report: {str(e)}", 'danger')

    return render_template('user/report_found.html', categories=categories, form={})


@item_bp.route('/report/<int:report_id>')
@login_required
def view_report(report_id):
    user = get_current_user()
    report = ItemReport.query.get_or_404(report_id)

    # Authorization check: Normal user can view public found items or their own items
    is_owner = (report.user_id == user.id)
    if not is_owner and not user.is_admin and report.report_type == 'LOST':
        flash('You are not authorized to view private lost item details of another user.', 'warning')
        return redirect(url_for('main.reports'))

    matches = []
    if is_owner or user.is_admin:
        if report.report_type == 'LOST':
            matches = Match.query.filter_by(lost_report_id=report.id).order_by(Match.overall_score.desc()).all()
        else:
            matches = Match.query.filter_by(found_report_id=report.id).order_by(Match.overall_score.desc()).all()

    return render_template('user/report_detail.html', report=report, is_owner=is_owner, matches=matches, user=user)


@item_bp.route('/matches')
@login_required
def matches():
    user = get_current_user()
    user_lost_reports = ItemReport.query.filter_by(user_id=user.id, report_type='LOST').all()
    lost_ids = [r.id for r in user_lost_reports]

    user_matches = []
    if lost_ids:
        user_matches = Match.query.filter(Match.lost_report_id.in_(lost_ids)).order_by(Match.overall_score.desc()).all()

    return render_template('user/matches.html', matches=user_matches, user_reports=user_lost_reports)
