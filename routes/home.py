from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash
from app import db
from models import Task, User
from forms import TaskForm, CompleteTaskForm, ProfileForm
from flask import send_from_directory

home_bp = Blueprint('home', __name__)

@home_bp.route('/google24c6dec42ac4918a.html')
def google_verify():
    return send_from_directory('static', 'google24c6dec42ac4918a.html')

@home_bp.route('/')

@home_bp.route('/index')
@login_required
def index():
    # Update user's last active time
    current_user.last_active = datetime.utcnow()
    db.session.commit()

    # Get incomplete tasks for current user
    tasks = Task.query.filter_by(user_id=current_user.id, completed=False).all()

    # Get today's completed tasks
    from datetime import date
    today = date.today()
    completed_today = Task.query.filter_by(
        user_id=current_user.id, 
        completed=True, 
        date_created=today
    ).order_by(Task.id.desc()).all()

    # Calculate today's totals
    today_total_minutes = sum(task.actual_minutes for task in completed_today)
    today_total_points = sum(task.calculate_points() for task in completed_today)

    task_form = TaskForm()
    complete_form = CompleteTaskForm()
    profile_form = ProfileForm(original_username=current_user.username)

    from models import Notification, NotificationRead
    # Only show active notifications the user hasn't seen
    seen_ids = [nr.notification_id for nr in NotificationRead.query.filter_by(user_id=current_user.id).all()]
    global_notifications = Notification.query.filter(
        Notification.is_active==True,
        ~Notification.id.in_(seen_ids)
    ).order_by(Notification.created_at.desc()).all()

    # Mark these notifications as read for this user
    for notif in global_notifications:
        nr = NotificationRead(user_id=current_user.id, notification_id=notif.id)
        db.session.add(nr)
    db.session.commit()

    return render_template('index.html', 
                     title='Task Manager', 
                     tasks=tasks, 
                     completed_today=completed_today,
                     today_total_minutes=today_total_minutes,
                     today_total_points=today_total_points,
                     task_form=task_form,
                     complete_form=complete_form,
                     profile_form=profile_form,
                     current_user=current_user,
                     global_notifications=global_notifications)

@home_bp.route('/add_task', methods=['POST'])
@login_required
def add_task():
    form = TaskForm()
    if form.validate_on_submit():
        task = Task(
            name=form.name.data,
            duration_minutes=form.duration_minutes.data,
            user_id=current_user.id
        )
        db.session.add(task)
        db.session.commit()
        flash('Task added successfully!')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{field}: {error}')
    
    return redirect(url_for('home.index'))

@home_bp.route('/complete_task', methods=['POST'])
@login_required
def complete_task():
    form = CompleteTaskForm()
    if form.validate_on_submit():
        task = Task.query.get_or_404(form.task_id.data)
        
        # Verify task belongs to current user
        if task.user_id != current_user.id:
            flash('Unauthorized access to task.')
            return redirect(url_for('home.index'))
        
        # Calculate user's rank before completing the task
        users = User.query.filter(User.total_score > 0).order_by(User.total_score.desc()).all()
        prev_rank = [u.id for u in users].index(current_user.id) + 1 if current_user.id in [u.id for u in users] else len(users) + 1

        # Update task
        task.actual_minutes = int(form.actual_minutes.data)
        task.completed = True
        task.completed_at = datetime.utcnow()

        # Calculate points and update user score
        points_earned = task.calculate_points()
        current_user.total_score += points_earned
        db.session.commit()
        flash(f'Task completed! You earned {points_earned} points.')

        # Calculate user's rank after completing the task
        users = User.query.filter(User.total_score > 0).order_by(User.total_score.desc()).all()
        new_rank = [u.id for u in users].index(current_user.id) + 1 if current_user.id in [u.id for u in users] else len(users) + 1

        if new_rank < prev_rank:
            flash(f'🎉 Congratulations! You climbed to rank #{new_rank} on the leaderboard!')
        # If user reaches rank 1, deactivate previous #1 notifications and create a new one
        if new_rank == 1 and prev_rank != 1:
            from models import Notification
            # Deactivate all previous #1 notifications
            Notification.query.filter(Notification.message.like('%#1 on the leaderboard!'), Notification.is_active==True).update({Notification.is_active: False})
            db.session.commit()
            # Create new notification
            notif = Notification(message=f'🏆 {current_user.username} is now #1 on the leaderboard!')
            db.session.add(notif)
            db.session.commit()
    else:
        flash('Error completing task.')
    
    return redirect(url_for('home.index'))

@home_bp.route('/delete_task/<int:task_id>')
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    
    # Verify task belongs to current user
    if task.user_id != current_user.id:
        flash('Unauthorized access to task.')
        return redirect(url_for('home.index'))
    
    db.session.delete(task)
    db.session.commit()
    flash('Task deleted successfully!')
    
    return redirect(url_for('home.index'))

@home_bp.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    form = ProfileForm(original_username=current_user.username)
    if form.validate_on_submit():
        # Verify current password
        if not check_password_hash(current_user.password_hash, form.current_password.data):
            flash('Current password is incorrect.')
            return redirect(url_for('home.index'))
        
        # Update username if changed
        if form.username.data != current_user.username:
            current_user.username = form.username.data
        
        # Update password if provided
        if form.new_password.data:
            current_user.password_hash = generate_password_hash(form.new_password.data)
        
        # Update last active time
        current_user.last_active = datetime.utcnow()
        
        db.session.commit()
        flash('Profile updated successfully!')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{field}: {error}')
    
    return redirect(url_for('home.index'))
