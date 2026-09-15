import os
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models import db, Category, LostReport, FoundReport, VerificationQuestion, Match
from matching.match_service import MatchService
from services.audit_service import AuditService

report_bp = Blueprint('report', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_file(file):
    if file and allowed_file(file.filename):
        filename = secure_filename(f"{int(datetime.utcnow().timestamp())}_{file.filename}")
        os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        return filepath
    return None


@report_bp.route('/dashboard')
@login_required
def dashboard():
    my_lost = LostReport.query.filter_by(user_id=current_user.id).order_by(LostReport.created_at.desc()).all()
    my_found = FoundReport.query.filter_by(user_id=current_user.id).order_by(FoundReport.created_at.desc()).all()
    
    # Matches associated with user's lost reports
    lost_ids = [r.id for r in my_lost]
    my_matches = Match.query.filter(Match.lost_report_id.in_(lost_ids)).order_by(Match.overall_score.desc()).all() if lost_ids else []

    return render_template('reports/dashboard.html', lost_reports=my_lost, found_reports=my_found, matches=my_matches)


@report_bp.route('/lost/create', methods=['GET', 'POST'])
@login_required
def create_lost():
    categories = Category.query.all()

    if request.method == 'POST':
        item_name = request.form.get('item_name')
        category_id = request.form.get('category_id')
        description = request.form.get('description')
        brand = request.form.get('brand')
        color = request.form.get('color')
        distinguishing_features = request.form.get('distinguishing_features')
        location_text = request.form.get('location_text')
        lost_date_str = request.form.get('lost_date')
        lost_time_str = request.form.get('lost_time')

        lat = request.form.get('latitude', type=float)
        lon = request.form.get('longitude', type=float)

        file = request.files.get('image')
        image_path = save_uploaded_file(file)

        lost_date = datetime.strptime(lost_date_str, '%Y-%m-%d').date() if lost_date_str else datetime.utcnow().date()
        lost_time = datetime.strptime(lost_time_str, '%H:%M').time() if lost_time_str else None

        report = LostReport(
            user_id=current_user.id,
            category_id=category_id,
            item_name=item_name,
            description=description,
            brand=brand,
            color=color,
            distinguishing_features=distinguishing_features,
            location_text=location_text,
            latitude=lat,
            longitude=lon,
            lost_date=lost_date,
            lost_time=lost_time,
            image_path=image_path,
            status='ACTIVE'
        )

        db.session.add(report)
        db.session.commit()

        AuditService.log_action(current_user.id, "CREATE_LOST_REPORT", f"Created Lost Report #{report.id}: {item_name}")

        # Automatically trigger matching engine for this new report
        matcher = MatchService()
        matches = matcher.run_matches_for_lost_report(report.id)

        flash(f"Lost report created successfully! Found {len(matches)} potential match(es).", "success")
        return redirect(url_for('match.possible_matches', report_id=report.id))

    return render_template('reports/create_lost.html', categories=categories)


@report_bp.route('/found/create', methods=['GET', 'POST'])
@login_required
def create_found():
    categories = Category.query.all()

    if request.method == 'POST':
        item_name = request.form.get('item_name')
        category_id = request.form.get('category_id')
        description = request.form.get('description')
        brand = request.form.get('brand')
        color = request.form.get('color')
        distinguishing_features = request.form.get('distinguishing_features')
        location_text = request.form.get('location_text')
        storage_location = request.form.get('storage_location')
        found_date_str = request.form.get('found_date')
        found_time_str = request.form.get('found_time')

        lat = request.form.get('latitude', type=float)
        lon = request.form.get('longitude', type=float)

        file = request.files.get('image')
        image_path = save_uploaded_file(file)

        found_date = datetime.strptime(found_date_str, '%Y-%m-%d').date() if found_date_str else datetime.utcnow().date()
        found_time = datetime.strptime(found_time_str, '%H:%M').time() if found_time_str else None

        report = FoundReport(
            user_id=current_user.id,
            category_id=category_id,
            item_name=item_name,
            description=description,
            brand=brand,
            color=color,
            distinguishing_features=distinguishing_features,
            location_text=location_text,
            storage_location=storage_location,
            latitude=lat,
            longitude=lon,
            found_date=found_date,
            found_time=found_time,
            image_path=image_path,
            status='ACTIVE'
        )

        db.session.add(report)
        db.session.commit()

        # Add optional verification questions if provided by finder
        q1 = request.form.get('verification_q1')
        a1 = request.form.get('verification_a1')
        q2 = request.form.get('verification_q2')
        a2 = request.form.get('verification_a2')

        if q1 and a1:
            vq1 = VerificationQuestion(found_report_id=report.id, question_text=q1.strip(), expected_answer=a1.strip(), question_order=1)
            db.session.add(vq1)
        if q2 and a2:
            vq2 = VerificationQuestion(found_report_id=report.id, question_text=q2.strip(), expected_answer=a2.strip(), question_order=2)
            db.session.add(vq2)

        db.session.commit()

        AuditService.log_action(current_user.id, "CREATE_FOUND_REPORT", f"Created Found Report #{report.id}: {item_name}")

        # Automatically run matching engine for found report
        matcher = MatchService()
        matches = matcher.run_matches_for_found_report(report.id)

        flash(f"Found report created successfully! {len(matches)} lost report(s) matched.", "success")
        return redirect(url_for('report.dashboard'))

    return render_template('reports/create_found.html', categories=categories)
