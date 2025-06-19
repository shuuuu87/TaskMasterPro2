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
    today = date.today()
    yesterday = today - timedelta(days=1)

    days_back = 360
    streaks = {}
    streak = 0
    prev_minutes = None
    missed_days = 0
    saved_streak = current_user.saved_streak or 0
    for i in range(days_back, -1, -1):
        target_date = today - timedelta(days=i)
        minutes = current_user.get_daily_minutes(target_date)
        # --- Custom streak rule: difference between days should not exceed 100 ---
        if prev_minutes is not None and minutes > 0 and abs(prev_minutes - minutes) > 100:
            # If the difference between today and yesterday is more than 100, streak breaks
            if streak > saved_streak:
                saved_streak = streak
            streak = 1
            missed_days = 0
        elif minutes > 0:
            if missed_days == 1:
                # Forgive one missed day, continue streak
                missed_days = 0
            elif missed_days > 1:
                # Streak is broken after two missed days
                if streak > saved_streak:
                    saved_streak = streak
                streak = 1
                missed_days = 0
            else:
                streak += 1 if prev_minutes is not None else 1
        else:
            missed_days += 1
            if missed_days == 2:
                if streak > saved_streak:
                    saved_streak = streak
                streak = 0
        streaks[str(target_date)] = streak
        prev_minutes = minutes

    # Save the best streak if needed
    if streak > saved_streak:
        saved_streak = streak
    if current_user.saved_streak != saved_streak:
        current_user.saved_streak = saved_streak
        db.session.commit()

    today_minutes = current_user.get_daily_minutes(today)
    yesterday_minutes = current_user.get_daily_minutes(yesterday)
    if today_minutes > 0:
        current_streak = streaks[str(today)]
    else:
        current_streak = streaks[str(yesterday)]

    # 💬 Flash messages
    if current_streak == 0:
        flash(f"😢 You lost your streak. Your last saved streak was {saved_streak} days. Start again today!")
    elif current_streak == 1:
        flash("👊 You're starting a new streak!")
    elif current_streak > 1:
        flash(f"🔥 You're on a {current_streak}-day streak! (Best: {saved_streak} days)")

    return render_template('progress.html', title='Progress', streak=current_streak, saved_streak=saved_streak)

@progress_bp.route('/progress_data')
@login_required
def progress_data():
    today = date.today()
    # Find the first day the user has a completed task
    first_task = Task.query.filter_by(user_id=current_user.id, completed=True).order_by(Task.date_created.asc()).first()
    if first_task:
        first_date = first_task.date_created
    else:
        first_date = today
    days_back = (today - first_date).days
    week_data = []
    labels = []
    for i in range(6, -1, -1):  # Last 7 days
        target_date = today - timedelta(days=i)
        daily_minutes = current_user.get_daily_minutes(target_date)
        week_data.append(daily_minutes)
        labels.append(target_date.strftime('%a %d'))
    # Calendar heatmap data (from first_date to today)
    calendar_minutes = {}
    streaks = {}
    streak = 0
    prev_minutes = None
    for i in range(days_back, -1, -1):
        target_date = today - timedelta(days=i)
        minutes = current_user.get_daily_minutes(target_date)
        calendar_minutes[str(target_date)] = minutes
        if minutes > 0:
            if prev_minutes is None or minutes >= prev_minutes:
                streak += 1
            else:
                streak = 1
            streaks[str(target_date)] = streak
        else:
            if prev_minutes is not None and prev_minutes > 0:
                streak = 0
            streaks[str(target_date)] = streak
        prev_minutes = minutes
    return jsonify({
        'labels': labels,
        'data': week_data,
        'total_minutes': sum(week_data),
        'total_points': current_user.total_score,
        'calendar_minutes': calendar_minutes,
        'calendar_streaks': streaks
    })
