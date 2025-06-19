from app import socketio
from flask import request
from models import User
from sqlalchemy import desc
from flask_login import current_user

def emit_leaderboard_update():
    users = User.query.filter(User.total_score > 0).order_by(desc(User.total_score)).all()
    zero_score_users = User.query.filter(User.total_score == 0).order_by(User.username).all()
    all_users = users + zero_score_users
    leaderboard = []
    for user in all_users:
        badge = user.get_badge()
        leaderboard.append({
            'id': user.id,
            'username': user.username,
            'score': user.total_score,
            'last_active': user.last_active.isoformat() if user.last_active else None,
            'last_active_display': user.last_active.strftime('%Y-%m-%d %H:%M') if user.last_active else '',
            'badge_name': badge['name'],
            'badge_color': badge['color'],
            'badge_icon': badge['icon'],
            'is_online': user.is_online(),
            'streak': user.saved_streak,
        })
    socketio.emit('leaderboard_update', leaderboard)
