from flask_login import login_required, current_user
from models import User, Race, RaceInvitation
from app import db
from datetime import datetime, timedelta


from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import User, Race, RaceInvitation
from app import db
from datetime import datetime, timedelta

# Define blueprint at the top before any usage
race_bp = Blueprint('race', __name__)

# Utility function to get the opponent user object for a race
def get_race_opponent(race, user_id):
    if race.user1_id == user_id:
        return User.query.get(race.user2_id)
    else:
        return User.query.get(race.user1_id)

@race_bp.route('/race/check', methods=['POST'])
@login_required
def check_race():
    # Check if race ended and process results
    active_race = Race.query.filter(
        ((Race.user1_id == current_user.id) | (Race.user2_id == current_user.id)) & (Race.status == 'active')
    ).first()
    if not active_race:
        flash('No active race.', 'info')
        return redirect(url_for('race.race_page'))
    now = datetime.utcnow()
    if active_race.end_time and now >= active_race.end_time:
        # Calculate points earned during race
        user1 = User.query.get(active_race.user1_id)
        user2 = User.query.get(active_race.user2_id)
        # Store scores at race start if not already
        if not hasattr(active_race, 'user1_score_start'):
            active_race.user1_score_start = user1.total_score
            active_race.user2_score_start = user2.total_score
        user1_points = user1.total_score - active_race.user1_score_start
        user2_points = user2.total_score - active_race.user2_score_start
        if user1_points > user2_points:
            winner, loser = user1, user2
            winner_points = user1_points - user2_points
            loser_points = 2
        elif user2_points > user1_points:
            winner, loser = user2, user1
            winner_points = user2_points - user1_points
            loser_points = 2
        else:
            winner = loser = None
            winner_points = loser_points = 0
        # Award points
        if winner:
            winner.total_score += winner_points
            active_race.winner_id = winner.id
            active_race.loser_id = loser.id
            active_race.winner_points = winner_points
            active_race.loser_points = loser_points
            flash(f'Congratulations {winner.username}, you have won this race and earned {winner_points} points!', 'success')
            flash(f"Don't worry {loser.username}, you get 2 points for your try!", 'info')
            loser.total_score += loser_points
        else:
            flash('It was a tie! No extra points awarded.', 'info')
        active_race.status = 'finished'
        db.session.commit()
    else:
        flash('Race is still ongoing.', 'info')
    return redirect(url_for('race.race_page'))

@race_bp.route('/race/invite', methods=['POST'])
@login_required
def send_invite():
    user_id = request.form.get('user_id')
    duration = int(request.form.get('duration', 1))
    if not user_id:
        flash('No user selected.', 'error')
        return redirect(url_for('race.race_page'))
    invitee = User.query.get(user_id)
    if not invitee:
        flash('User not found.', 'error')
        return redirect(url_for('race.race_page'))
    # Check if either user is already in a race
    active_race = Race.query.filter(
        ((Race.user1_id == current_user.id) | (Race.user2_id == current_user.id) |
         (Race.user1_id == invitee.id) | (Race.user2_id == invitee.id)) & (Race.status == 'active')
    ).first()
    if active_race:
        flash('One of the users is already in a race.', 'error')
        return redirect(url_for('race.race_page'))
    # Check for existing pending invite
    existing_invite = RaceInvitation.query.filter_by(inviter_id=current_user.id, invitee_id=invitee.id, status='pending').first()
    if existing_invite:
        flash('You have already invited this user.', 'info')
        return redirect(url_for('race.race_page'))
    invitation = RaceInvitation(inviter_id=current_user.id, invitee_id=invitee.id, duration_days=duration)
    db.session.add(invitation)
    db.session.commit()
    flash('Invitation sent!', 'success')
    return redirect(url_for('race.race_page'))

@race_bp.route('/race/accept/<int:invite_id>', methods=['POST'])
@login_required
def accept_invite(invite_id):
    invitation = RaceInvitation.query.get(invite_id)
    if not invitation or invitation.invitee_id != current_user.id or invitation.status != 'pending':
        flash('Invalid invitation.', 'error')
        return redirect(url_for('race.race_page'))
    # Start race
    now = datetime.utcnow()
    end_time = now + timedelta(days=invitation.duration_days)
    race = Race(user1_id=invitation.inviter_id, user2_id=invitation.invitee_id, start_time=now, end_time=end_time, duration_days=invitation.duration_days, status='active')
    db.session.add(race)
    db.session.commit()
    invitation.status = 'accepted'
    invitation.race_id = race.id
    db.session.commit()
    flash('Race started!', 'success')
    return redirect(url_for('race.race_page'))


@race_bp.route('/race/reject/<int:invite_id>', methods=['POST'])
@login_required
def reject_invite(invite_id):
    invitation = RaceInvitation.query.get(invite_id)
    if not invitation or invitation.invitee_id != current_user.id or invitation.status != 'pending':
        flash('Invalid invitation.', 'error')
        return redirect(url_for('race.race_page'))
    invitation.status = 'rejected'
    db.session.commit()
    flash('Invitation rejected.', 'info')
    return redirect(url_for('race.race_page'))

@race_bp.route('/race')
@login_required
def race_page():
    users = User.query.filter(User.id != current_user.id).all()
    invitations = RaceInvitation.query.filter_by(invitee_id=current_user.id, status='pending').all()
    active_races = Race.query.filter(Race.status == 'active').all()
    users_in_race = set()
    for race in active_races:
        users_in_race.add(race.user1_id)
        users_in_race.add(race.user2_id)
    for user in users:
        user.in_race = user.id in users_in_race
    active_race = next((r for r in active_races if r.user1_id == current_user.id or r.user2_id == current_user.id), None)

    # Ensure starting scores are set for all active races (legacy-safe)
    for race in active_races:
        updated = False
        user1 = User.query.get(race.user1_id)
        user2 = User.query.get(race.user2_id)
        if not hasattr(race, 'user1_score_start') or race.user1_score_start is None:
            race.user1_score_start = user1.total_score
            updated = True
        if not hasattr(race, 'user2_score_start') or race.user2_score_start is None:
            race.user2_score_start = user2.total_score
            updated = True
        if updated:
            db.session.commit()

    # Calculate race progress if user is in a race
    user_points = opponent_points = None
    opponent = None
    if active_race:
        user1 = User.query.get(active_race.user1_id)
        user2 = User.query.get(active_race.user2_id)
        user1_start = getattr(active_race, 'user1_score_start', user1.total_score)
        user2_start = getattr(active_race, 'user2_score_start', user2.total_score)
        if current_user.id == user1.id:
            user_points = user1.total_score - user1_start
            opponent_points = user2.total_score - user2_start
            opponent = user2
        else:
            user_points = user2.total_score - user2_start
            opponent_points = user1.total_score - user1_start
            opponent = user1

    # Prepare all current races for display at the bottom (for all users)
    all_live_races = []
    for race in active_races:
        user_a = User.query.get(race.user1_id)
        user_b = User.query.get(race.user2_id)
        user_a_start = getattr(race, 'user1_score_start', user_a.total_score)
        user_b_start = getattr(race, 'user2_score_start', user_b.total_score)
        user_a_points = user_a.total_score - user_a_start
        user_b_points = user_b.total_score - user_b_start
        if user_a_points > user_b_points:
            leader = user_a.username
        elif user_b_points > user_a_points:
            leader = user_b.username
        else:
            leader = 'Tie'
        all_live_races.append({
            'user_a': user_a,
            'user_b': user_b,
            'user_a_points': user_a_points,
            'user_b_points': user_b_points,
            'leader': leader,
            'end_time': race.end_time,
            'duration_days': race.duration_days
        })
    return render_template('race.html', users=users, invitations=invitations, active_race=active_race, user_points=user_points, opponent_points=opponent_points, opponent=opponent, all_live_races=all_live_races)
