from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from app import db
from models import Task
from forms import TaskForm, CompleteTaskForm

home_bp = Blueprint('home', __name__)

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
    
    return render_template('index.html', 
                         title='Task Manager', 
                         tasks=tasks, 
                         completed_today=completed_today,
                         today_total_minutes=today_total_minutes,
                         today_total_points=today_total_points,
                         task_form=task_form,
                         complete_form=complete_form,
                         current_user=current_user)

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
        
        # Update task
        task.actual_minutes = int(form.actual_minutes.data)
        task.completed = True
        
        # Calculate points and update user score
        points_earned = task.calculate_points()
        current_user.total_score += points_earned
        
        db.session.commit()
        flash(f'Task completed! You earned {points_earned} points.')
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
