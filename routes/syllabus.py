from flask import Blueprint, render_template, request, redirect, url_for, abort
from flask_login import login_required, current_user
from models import db, Subject, Chapter, Topic
from syllabus_data import SYLLABUS_DATA

syllabus_bp = Blueprint('syllabus', __name__, url_prefix='/syllabus')

@syllabus_bp.route('/delete_subject/<int:subject_id>', methods=['POST'])
@login_required
def delete_subject(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    if subject.user_id != current_user.id:
        abort(403)
    db.session.delete(subject)
    db.session.commit()
    return redirect(url_for('syllabus.dashboard'))

@syllabus_bp.route('/delete_chapter/<int:chapter_id>', methods=['POST'])
@login_required
def delete_chapter(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    if chapter.subject.user_id != current_user.id:
        abort(403)
    subject_id = chapter.subject_id
    db.session.delete(chapter)
    db.session.commit()
    return redirect(url_for('syllabus.subject_detail', subject_id=subject_id))

@syllabus_bp.route('/delete_topic/<int:topic_id>', methods=['POST'])
@login_required
def delete_topic(topic_id):
    topic = Topic.query.get_or_404(topic_id)
    chapter = topic.chapter
    if chapter.subject.user_id != current_user.id:
        abort(403)
    subject_id = chapter.subject_id
    db.session.delete(topic)
    db.session.commit()
    return redirect(url_for('syllabus.subject_detail', subject_id=subject_id))


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

@syllabus_bp.route('/select_board_class', methods=['POST'])
@login_required
def select_board_class():
    board = request.form.get('board')
    class_ = request.form.get('class')
    # Check if user already has subjects to avoid duplicates
    existing_subjects = Subject.query.filter_by(user_id=current_user.id).all()
    if not existing_subjects and board in SYLLABUS_DATA and class_ in SYLLABUS_DATA[board]:
        for subject_name, chapters in SYLLABUS_DATA[board][class_].items():
            subject = Subject(name=subject_name, user_id=current_user.id)
            db.session.add(subject)
            db.session.flush()  # Get subject.id before commit
            for chapter in chapters:
                if isinstance(chapter, dict) and 'chapter_name' in chapter:
                    new_chapter = Chapter(title=chapter['chapter_name'], subject_id=subject.id)
                    db.session.add(new_chapter)
                    db.session.flush()  # Get chapter.id before adding topics
                    for topic in chapter.get('topics', []):
                        topic_name = topic['topic_name'] if isinstance(topic, dict) and 'topic_name' in topic else str(topic)
                        db.session.add(Topic(name=topic_name, chapter_id=new_chapter.id))
                else:
                    db.session.add(Chapter(title=chapter, subject_id=subject.id))
        db.session.commit()
    return redirect(url_for('syllabus.dashboard'))