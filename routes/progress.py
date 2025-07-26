from flask import Blueprint, render_template, jsonify, flash
from flask_login import login_required, current_user
from datetime import timedelta, datetime
from zoneinfo import ZoneInfo
from models import Task
from app import db

progress_bp = Blueprint('progress', __name__)

# ✅ Smart Streak Calculation with Forgiveness & Minute Difference Rule
from app import send_email
def send_streak_break_email(user):
    subject = "Your Productivity Streak Has Broken"
    body = (
        f"Hi {user.username},\n\n"
        "You have used all your consecutive streak savers. Your streak has now broken. "
        "Start a new streak by completing at least 2 minutes of activity today!\n\n"
        "Keep going!\n\n"
        "- ProductivityPilot Team"
    )
    send_email(subject, [user.email], body)

def calculate_streak_data(user, days_back=360):
    today = datetime.now(ZoneInfo("Asia/Kolkata")).date()
    calendar_minutes = {}
    streaks = {}
    forgiven_days = []

    streak = 0
    saved_streak = int(user.saved_streak or 0)
    current_streak = 0
    consecutive_forgives = 0
    previous_minutes = None
    streak_broken = False

    for i in range(days_back, -1, -1):
        target_date = today - timedelta(days=i)
        minutes = user.get_daily_minutes(target_date)
        calendar_minutes[str(target_date)] = minutes

        if previous_minutes is None:
            # First day, no previous to compare
            streak = 1 if minutes >= 2 else 0
            previous_minutes = minutes
            streaks[str(target_date)] = streak
            consecutive_forgives = 0 if minutes >= 2 else 1
            continue

        drop = previous_minutes - minutes

        if minutes >= 2 and drop <= 100:
            streak += 1
            consecutive_forgives = 0
        elif consecutive_forgives < 2:
            # Forgive, but do not increase streak
            consecutive_forgives += 1
            forgiven_days.append(str(target_date))
        else:
            # 3rd consecutive miss: break streak
            if streak > saved_streak:
                saved_streak = streak
            streak = 0
            consecutive_forgives = 0
            streak_broken = True
            send_streak_break_email(user)
        previous_minutes = minutes
        if i == 0:
            current_streak = streak
        streaks[str(target_date)] = streak

    if streak > saved_streak:
        saved_streak = streak

    return {
        "calendar_minutes": calendar_minutes,
        "calendar_streaks": streaks,
        "forgiven_days": forgiven_days,
        "current_streak": current_streak,
        "saved_streak": saved_streak
    }

@progress_bp.route('/progress')
@login_required
def progress():
    today = datetime.now(ZoneInfo("Asia/Kolkata")).date()
    yesterday = today - timedelta(days=1)

    streak_data = calculate_streak_data(current_user)
    current_streak = streak_data["current_streak"]
    saved_streak = streak_data["saved_streak"]

    # Save if streak improved
    if int(current_user.saved_streak or 0) != saved_streak:
        current_user.saved_streak = saved_streak
        db.session.commit()

    # Extra fallback
    if current_streak == 0:
        today_minutes = current_user.get_daily_minutes(today)
        current_streak = streak_data["calendar_streaks"].get(str(today), 0) if today_minutes > 0 else streak_data["calendar_streaks"].get(str(yesterday), 0)

    # Flash motivational messages
    if current_streak == 0:
        flash(f"😢 You lost your streak. Your best streak was {saved_streak} days. Start again today!")
    elif current_streak == 1:
        flash("👊 You're starting a new streak!")
    elif current_streak > 1:
        flash(f"🔥 You're on a {current_streak}-day streak! (Best: {saved_streak} days)")

    return render_template('progress.html', title='Progress', streak=current_streak, saved_streak=saved_streak)

@progress_bp.route('/progress_data')
@login_required
def progress_data():
    today = datetime.now(ZoneInfo("Asia/Kolkata")).date()
    first_task = Task.query.filter_by(user_id=current_user.id, completed=True).order_by(Task.date_created.asc()).first()
    first_date = first_task.date_created if first_task else datetime.now(ZoneInfo("Asia/Kolkata")).date()
    days_back = (today - first_date).days

    week_data = []
    labels = []
    for i in range(6, -1, -1):
        target_date = today - timedelta(days=i)
        daily_minutes = current_user.get_daily_minutes(target_date)
        week_data.append(daily_minutes)
        labels.append(target_date.strftime('%a %d'))

    # Use same consistent logic
    streak_data = calculate_streak_data(current_user, days_back)

    return jsonify({
        'labels': labels,
        'data': week_data,
        'total_minutes': sum(week_data),
        'total_points': current_user.total_score,
        'calendar_minutes': streak_data["calendar_minutes"],
        'calendar_streaks': streak_data["calendar_streaks"],
        'forgiven_days': streak_data["forgiven_days"]
    })
