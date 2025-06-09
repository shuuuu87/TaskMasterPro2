from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from datetime import date, timedelta
from models import Task
from sqlalchemy import func
from app import db
from collections import Counter

progress_bp = Blueprint('progress', __name__)

def get_current_streak(user):
    today = date.today()
    streak = 0
    day = today
    while True:
        completed = Task.query.filter(
            Task.user_id == user.id,
            func.date(Task.completed_at) == day
        ).first()
        if completed:
            streak += 1
            day -= timedelta(days=1)
        else:
            break
    return streak

@progress_bp.route('/progress')
@login_required
def progress():
    streak = get_current_streak(current_user)
    return render_template('progress.html', title='Progress', streak=streak)

@progress_bp.route('/progress_data')
@login_required
def progress_data():
    today = date.today()
    week_data = []
    labels = []

    for i in range(6, -1, -1):
        target_date = today - timedelta(days=i)
        daily_minutes = current_user.get_daily_minutes(target_date)
        week_data.append(daily_minutes)
        labels.append(target_date.strftime('%a %d'))

    # Calendar heatmap data (last 60 days, by minutes)
    days_back = 60
    calendar_minutes = {}
    for i in range(days_back, -1, -1):
        target_date = today - timedelta(days=i)
        minutes = current_user.get_daily_minutes(target_date)
        calendar_minutes[str(target_date)] = minutes

    return jsonify({
        'labels': labels,
        'data': week_data,
        'total_minutes': sum(week_data),
        'total_points': current_user.total_score,
        'calendar_minutes': calendar_minutes  # <-- use this in frontend
    })