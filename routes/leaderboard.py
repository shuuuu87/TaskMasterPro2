from flask import Blueprint, render_template, jsonify
from flask_login import login_required
from models import User
from sqlalchemy import desc
from datetime import datetime

leaderboard_bp = Blueprint('leaderboard', __name__)

def time_since(dt):
    if not dt:
        return "Never"
    now = datetime.utcnow()
    diff = now - dt
    seconds = int(diff.total_seconds())
    minutes = seconds // 60
    hours = minutes // 60
    days = diff.days

    if seconds < 60:
        return f"{seconds} seconds ago"
    elif minutes < 60:
        return f"{minutes} minutes ago"
    elif hours < 24:
        return f"{hours} hours ago"
    else:
        return f"{days} days ago"

@leaderboard_bp.route('/leaderboard')
@login_required
def leaderboard():
    users = User.query.filter(User.total_score > 0).order_by(desc(User.total_score)).all()
    zero_score_users = User.query.filter(User.total_score == 0).order_by(User.username).all()
    all_users = users + zero_score_users

    for user in all_users:
        user.last_active_display = time_since(user.last_active)

    return render_template('leaderboard.html', 
                           title='Leaderboard', 
                           users=all_users)

@leaderboard_bp.route('/api/leaderboard')
@login_required
def api_leaderboard():
    users = User.query.filter(User.total_score > 0).order_by(desc(User.total_score)).all()
    zero_score_users = User.query.filter(User.total_score == 0).order_by(User.username).all()
    all_users = users + zero_score_users
    leaderboard = []
    for user in all_users:
        leaderboard.append({
            'id': user.id,
            'username': user.username,
            'score': user.total_score,
            'last_active': user.last_active.isoformat() if user.last_active else None,
            'last_active_display': time_since(user.last_active),
        })
    return jsonify(leaderboard)
