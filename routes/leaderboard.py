from flask import Blueprint, render_template
from flask_login import login_required
from models import User
from sqlalchemy import desc

leaderboard_bp = Blueprint('leaderboard', __name__)

@leaderboard_bp.route('/leaderboard')
@login_required
def leaderboard():
    # Get all users ordered by total score (descending)
    users = User.query.filter(User.total_score > 0).order_by(desc(User.total_score)).all()
    
    # Add users with 0 score at the end
    zero_score_users = User.query.filter(User.total_score == 0).order_by(User.username).all()
    all_users = users + zero_score_users
    
    return render_template('leaderboard.html', 
                         title='Leaderboard', 
                         users=all_users)
