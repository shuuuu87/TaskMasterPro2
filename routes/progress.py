from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from datetime import date, timedelta
from models import Task
from sqlalchemy import func
from app import db

progress_bp = Blueprint('progress', __name__)

@progress_bp.route('/progress')
@login_required
def progress():
    return render_template('progress.html', title='Progress')

@progress_bp.route('/progress_data')
@login_required
def progress_data():
    # Get last 7 days of data
    today = date.today()
    week_data = []
    labels = []
    
    for i in range(6, -1, -1):  # 6 days ago to today
        target_date = today - timedelta(days=i)
        daily_minutes = current_user.get_daily_minutes(target_date)
        
        week_data.append(daily_minutes)
        labels.append(target_date.strftime('%a %d'))
    
    return jsonify({
        'labels': labels,
        'data': week_data,
        'total_minutes': sum(week_data),
        'total_points': current_user.total_score
    })
