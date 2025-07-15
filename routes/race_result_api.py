from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required
from models import Race
from app import db

race_result_api = Blueprint('race_result_api', __name__)

@race_result_api.route('/race/result_status')
@login_required
def race_result_status():
    race = Race.query.filter(
        ((Race.user1_id == current_user.id) | (Race.user2_id == current_user.id)) & (Race.status == 'finished')
    ).order_by(Race.end_time.desc()).first()
    if not race:
        return jsonify({'show_modal': False})
    # Only show once per race
    if getattr(race, 'result_claimed_by_' + str(current_user.id), False):
        return jsonify({'show_modal': False})
    # Determine result
    if race.winner_id == current_user.id:
        result_text = 'You won!'
        points_text = f'You earned {race.winner_points} points.'
    elif race.loser_id == current_user.id:
        result_text = 'You lose!'
        points_text = f'You earned {race.loser_points} points.'
    else:
        result_text = 'It was a tie!'
        points_text = 'No extra points.'
    return jsonify({'show_modal': True, 'result_text': result_text, 'points_text': points_text})

@race_result_api.route('/race/claim_result', methods=['POST'])
@login_required
def claim_race_result():
    race = Race.query.filter(
        ((Race.user1_id == current_user.id) | (Race.user2_id == current_user.id)) & (Race.status == 'finished')
    ).order_by(Race.end_time.desc()).first()
    if not race:
        return ('', 204)
    # Award points only on claim
    from models import User
    if race.winner_id == current_user.id and race.winner_points:
        winner = User.query.get(current_user.id)
        winner.total_score += race.winner_points
        db.session.commit()
    elif race.loser_id == current_user.id and race.loser_points:
        loser = User.query.get(current_user.id)
        loser.total_score += race.loser_points
        db.session.commit()
    setattr(race, 'result_claimed_by_' + str(current_user.id), True)
    db.session.commit()
    return ('', 204)
