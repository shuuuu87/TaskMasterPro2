from flask import Blueprint, render_template, request, redirect, url_for, abort
from flask_login import login_required, current_user
from models import db, Subject, Chapter, Topic

syllabus_bp = Blueprint('syllabus', __name__, url_prefix='/syllabus')

@syllabus_bp.route('/')
@login_required
def dashboard():
    subjects = Subject.query.filter_by(user_id=current_user.id).all()
    return render_template('syllabus/dashboard.html', subjects=subjects)

@syllabus_bp.route('/subject/<int:subject_id>')
@login_required
def subject_detail(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    if subject.user_id != current_user.id:
        abort(403)
    return render_template('syllabus/subject.html', subject=subject)

@syllabus_bp.route('/add_subject', methods=['POST'])
@login_required
def add_subject():
    name = request.form.get('name')
    if name:
        db.session.add(Subject(name=name, user_id=current_user.id))
        db.session.commit()
    return redirect(url_for('syllabus.dashboard'))

@syllabus_bp.route('/subject/<int:subject_id>/add_chapter', methods=['POST'])
@login_required
def add_chapter(subject_id):
    title = request.form.get('title')
    if title:
        db.session.add(Chapter(title=title, subject_id=subject_id))
        db.session.commit()
    return redirect(url_for('syllabus.subject_detail', subject_id=subject_id))

@syllabus_bp.route('/chapter/<int:chapter_id>/add_topic', methods=['POST'])
@login_required
def add_topic(chapter_id):
    name = request.form.get('name')
    if name:
        db.session.add(Topic(name=name, chapter_id=chapter_id))
        db.session.commit()
    chapter = Chapter.query.get_or_404(chapter_id)
    return redirect(url_for('syllabus.subject_detail', subject_id=chapter.subject_id))

@syllabus_bp.route('/topic/<int:topic_id>/toggle', methods=['POST'])
@login_required
def toggle_topic(topic_id):
    topic = Topic.query.get_or_404(topic_id)
    chapter = topic.chapter
    if chapter.subject.user_id != current_user.id:
        abort(403)
    topic.completed = not topic.completed
    db.session.commit()
    return redirect(url_for('syllabus.subject_detail', subject_id=chapter.subject_id))