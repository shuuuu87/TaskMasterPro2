from flask import Blueprint, render_template, jsonify, flash
from flask_login import login_required, current_user
from datetime import date, timedelta
from models import Task
from sqlalchemy import func
from app import db
from collections import defaultdict

progress_bp = Blueprint('progress', __name__)

def get_current_streak(user):
    today = date.today()
    day = today

    # Get total actual_minutes for today and yesterday
    today_minutes = db.session.query(
        func.sum(Task.actual_minutes)
    ).filter(
        Task.user_id == user.id,
        func.date(Task.completed_at) == today
    ).scalar() or 0

    if today_minutes == 0:
        return 0  # No work today = no streak

    yesterday = today - timedelta(days=1)
    yesterday_minutes = db.session.query(
        func.sum(Task.actual_minutes)
    ).filter(
        Task.user_id == user.id,
        func.date(Task.completed_at) == yesterday
    ).scalar() or 0

    if today_minutes < yesterday_minutes:
        return 0  # Today's work is less than yesterday, streak broken

    # Continue streak as long as each day >= next day
    streak = 1
    prev_minutes = today_minutes
    day = today - timedelta(days=1)
    while True:
        current_minutes = db.session.query(
            func.sum(Task.actual_minutes)
        ).filter(
            Task.user_id == user.id,
            func.date(Task.completed_at) == day
        ).scalar() or 0

        next_day = day + timedelta(days=1)
        next_day_minutes = db.session.query(
            func.sum(Task.actual_minutes)
        ).filter(
            Task.user_id == user.id,
            func.date(Task.completed_at) == next_day
        ).scalar() or 0

        if current_minutes >= next_day_minutes and current_minutes > 0:
            streak += 1
            day -= timedelta(days=1)
        else:
            break

    return streak

@progress_bp.route('/progress')
@login_required
def progress():
    streak = get_current_streak(current_user)

    # 💬 Flash messages
    if streak == 0:
        flash("😢 You lost your streak. Start again today!")
    elif streak == 1:
        flash("👊 You're starting a new streak!")
    elif streak > 1:
        flash(f"🔥 You're on a {streak}-day streak!")

    return render_template('progress.html', title='Progress', streak=streak)


@progress_bp.route('/progress_data')
@login_required
def progress_data():
    today = date.today()
    week_data = []
    labels = []

    for i in range(6, -1, -1):  # Last 7 days
        target_date = today - timedelta(days=i)
        daily_minutes = current_user.get_daily_minutes(target_date)
        week_data.append(daily_minutes)
        labels.append(target_date.strftime('%a %d'))

    # Calendar heatmap data (last 60 days)
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
        'calendar_minutes': calendar_minutes
    })
