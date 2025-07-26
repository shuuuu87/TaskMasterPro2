from flask import Blueprint, jsonify
from flask_login import login_required, current_user
from models import Race, User

def get_user_img(user):
    return f"/static/images/{user.profile_image or 'avatar1.png'}"

get_unclaimed_race_bp = Blueprint('get_unclaimed_race', __name__)

@get_unclaimed_race_bp.route('/get_unclaimed_race')
@login_required
def get_unclaimed_race():
    race = Race.query.filter(
        Race.status == 'finished',
        ((Race.winner_id == current_user.id) & (Race.winner_claimed == False)) |
        ((Race.loser_id == current_user.id) & (Race.loser_claimed == False))
    ).order_by(Race.end_time.desc()).first()
    if not race:
        return jsonify({'show': False})
    user_img = get_user_img(current_user)
    username = current_user.username
    if current_user.id == race.winner_id:
        message = f"You won the race! Now you should take treat from loser and you won {race.winner_points} points!"
    else:
        message = f"You lost this race but don't give up—next time is your turn to take treat. You got {race.loser_points} points."
    return jsonify({
        'show': True,
        'race_id': race.id,
        'user_img': user_img,
        'username': username,
        'message': message
    })
