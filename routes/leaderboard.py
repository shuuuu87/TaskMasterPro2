from flask import Blueprint, render_template, jsonify
from flask_login import login_required
from models import User
from sqlalchemy import desc
from datetime import datetime
from app import socketio

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

    # Attach "last_active_display" to each user
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
    leaderboard_data = [
        {
            'username': u.username,
            'total_score': u.total_score,
            'badge': u.get_badge()['name'],
            'last_active': u.last_active_display if hasattr(u, 'last_active_display') else time_since(u.last_active)
        } for u in all_users
    ]
    return jsonify(leaderboard_data)

def emit_leaderboard_update():
    from flask import current_app
    with current_app.app_context():
        users = User.query.filter(User.total_score > 0).order_by(desc(User.total_score)).all()
        zero_score_users = User.query.filter(User.total_score == 0).order_by(User.username).all()
        all_users = users + zero_score_users
        leaderboard_data = [
            {
                'username': u.username,
                'total_score': u.total_score,
                'badge': u.get_badge()['name'],
                'last_active': time_since(u.last_active),
                'is_online': u.is_online()
            } for u in all_users
        ]
        socketio.emit('leaderboard_update', leaderboard_data, broadcast=True)
