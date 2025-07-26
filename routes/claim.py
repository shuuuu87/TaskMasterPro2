from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app import db
from models import Race, User

claim_bp = Blueprint('claim', __name__)

@claim_bp.route('/claim_race_points', methods=['POST'])
@login_required
def claim_race_points():
    race_id = request.json.get('race_id')
    race = Race.query.get(race_id)
    if not race or race.status != 'finished':
        return jsonify({'success': False, 'message': 'Invalid or unfinished race.'}), 400

    if current_user.id == race.winner_id and not race.winner_claimed:
        current_user.total_score += race.winner_points
        race.winner_claimed = True
        db.session.commit()
        return jsonify({'success': True, 'points': race.winner_points, 'role': 'winner'})
    elif current_user.id == race.loser_id and not race.loser_claimed:
        current_user.total_score += race.loser_points
        race.loser_claimed = True
        db.session.commit()
        return jsonify({'success': True, 'points': race.loser_points, 'role': 'loser'})
    else:
        return jsonify({'success': False, 'message': 'Points already claimed or not a participant.'}), 400
