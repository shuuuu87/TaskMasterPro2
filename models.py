# Fix: import datetime before using it in models
from datetime import datetime, date
from app import db
# Race Invitation and Race Models
class RaceInvitation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    inviter_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    invitee_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    duration_days = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, accepted, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    race_id = db.Column(db.Integer, db.ForeignKey('race.id'))

class Race(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user1_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user2_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    duration_days = db.Column(db.Integer, nullable=False)
    winner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    loser_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    winner_points = db.Column(db.Integer, default=0)
    loser_points = db.Column(db.Integer, default=0)
    user1_score_start = db.Column(db.Integer, default=0)
    user2_score_start = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default='pending')  # pending, active, finished
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
from app import db
from flask_login import UserMixin
from datetime import datetime, date
from sqlalchemy import func
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    total_score = db.Column(db.Integer, default=0)
    last_active = db.Column(db.DateTime, default=datetime.utcnow)
    profile_image = db.Column(db.String(256), default='default.png')
    tasks = db.relationship('Task', backref='owner', lazy='dynamic')
    saved_streak = db.Column(db.Integer, default=0)
    
    def get_badge(self):
        """Get user's badge based on total score"""
        score = self.total_score
        # Each badge now has a unique icon (FontAwesome)
        if score == 0:
            return {'name': 'Wood', 'color': '#8B4513', 'icon': 'fa-tree'}
        elif 1 <= score <= 50:
            return {'name': 'Bronze', 'color': '#CD7F32', 'icon': 'fa-seedling'}
        elif 51 <= score <= 100:
            return {'name': 'Bronze 2', 'color': '#B87333', 'icon': 'fa-leaf'}
        elif 101 <= score <= 150:
            return {'name': 'Bronze 3', 'color': '#A97142', 'icon': 'fa-leaf'}
        elif 151 <= score <= 200:
            return {'name': 'Silver', 'color': '#C0C0C0', 'icon': 'fa-gem'}
        elif 201 <= score <= 300:
            return {'name': 'Silver 2', 'color': '#BFC1C2', 'icon': 'fa-gem'}
        elif 301 <= score <= 400:
            return {'name': 'Silver 3', 'color': '#AFAFAF', 'icon': 'fa-gem'}
        elif 401 <= score <= 500:
            return {'name': 'Gold', 'color': '#FFD700', 'icon': 'fa-star'}
        elif 501 <= score <= 600:
            return {'name': 'Gold 2', 'color': '#FFC300', 'icon': 'fa-star-half-alt'}
        elif 601 <= score <= 700:
            return {'name': 'Gold 3', 'color': '#FFB300', 'icon': 'fa-star-half-alt'}
        elif 701 <= score <= 800:
            return {'name': 'Gold 4', 'color': '#FFA500', 'icon': 'fa-star-half-alt'}
        elif 801 <= score <= 950:
            return {'name': 'Platinum', 'color': '#E5E4E2', 'icon': 'fa-diamond'}
        elif 951 <= score <= 1100:
            return {'name': 'Platinum 2', 'color': '#D4D4D4', 'icon': 'fa-diamond'}
        elif 1101 <= score <= 1250:
            return {'name': 'Platinum 3', 'color': '#B0B0B0', 'icon': 'fa-diamond'}
        elif 1251 <= score <= 1400:
            return {'name': 'Platinum 4', 'color': '#A9A9A9', 'icon': 'fa-diamond'}
        elif 1401 <= score <= 1550:
            return {'name': 'Diamond', 'color': '#61e2ff', 'icon': 'fa-gem'}
        elif 1551 <= score <= 1750:
            return {'name': 'Diamond 2', 'color': '#00BFFF', 'icon': 'fa-gem'}
        elif 1751 <= score <= 1950:
            return {'name': 'Diamond 3', 'color': '#1E90FF', 'icon': 'fa-gem'}
        elif 1951 <= score <= 2200:
            return {'name': 'Diamond 4', 'color': '#4682B4', 'icon': 'fa-gem'}
        elif 2201 <= score <= 2450:
            return {'name': 'Heroic', 'color': "#ff1e00", 'icon': 'fa-fire'}
        elif 2451 <= score <= 2850:
            return {'name': 'Master', 'color': '#9932CC', 'icon': 'fa-chess-king'}
        elif 2851 <= score <= 3200:
            return {'name': 'Elite Master', 'color': '#4B0082', 'icon': 'fa-chess-queen'}
        elif 3201 <= score <= 3600:
            return {'name': 'Grand Master', 'color': '#ff9900', 'icon': 'fa-crown'}
        elif 3601 <= score <= 4000:
            return {'name': 'Ascendant', 'color': "#796AFF", 'icon': 'fa-arrow-up'}
        elif 4001 <= score <= 4500:
            return {'name': 'Mythic', 'color': '#2F00FF', 'icon': 'fa-magic'}
        elif 4501 <= score <= 5000:
            return {'name': 'Immortal', 'color': '#0C004D', 'icon': 'fa-infinity'}
        elif 5001 <= score <= 5500:
            return {'name': 'Celestial', 'color': '#010016', 'icon': 'fa-moon'}
        elif 5501 <= score <= 6000:
            return {'name': 'Supreme', 'color': '#00F2FF', 'icon': 'fa-trophy'}
        elif 6001 <= score <= 6500:
            return {'name': 'Infinity', 'color': '#4587E3', 'icon': 'fa-infinity'}
        elif 6501 <= score <= 7000:
            return {'name': 'GrandmasterII', 'color': '#ff6200', 'icon': 'fa-chess-knight'}
        elif 7001 <= score <= 7500:
            return {'name': 'Hall of Fame', 'color': '#FFD700', 'icon': 'fa-medal'}
        elif 7501 <= score <= 8000:
            return {'name': 'Titan', 'color': '#B8860B', 'icon': 'fa-mountain'}
        elif 8001 <= score:
            return {'name': 'Legend ⚜🔱⚜', 'color': '#F0E054', 'icon': 'fa-crown'}
    def is_online(self):
        """Check if user is online (active within last 10 minutes)"""
        from datetime import timedelta
        if not self.last_active:
            return False
        return datetime.utcnow() - self.last_active < timedelta(minutes=10)
    def get_weekly_minutes(self):
        """Get total minutes completed in the last 7 days"""
        from datetime import timedelta
        week_ago = date.today() - timedelta(days=7)
        return db.session.query(func.sum(Task.actual_minutes)).filter(
            Task.user_id == self.id,
            Task.completed == True,
            Task.date_created >= week_ago
        ).scalar() or 0
    def get_daily_minutes(self, target_date):
        """Get total minutes completed on a specific date"""
        return db.session.query(func.sum(Task.actual_minutes)).filter(
            Task.user_id == self.id,
            Task.completed == True,
            Task.date_created == target_date
        ).scalar() or 0
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
class Task(db.Model):
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False, default=0)
    actual_minutes = db.Column(db.Integer, default=0)
    completed = db.Column(db.Boolean, default=False)
    title = db.Column(db.String(100))
    date_created = db.Column(db.Date, default=date.today)
    completed_at = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    reminder_sent = db.Column(db.Boolean, default=False)
    def calculate_points(self):
        """Calculate points for this task (1 point per 12 minutes)"""
        return int(self.actual_minutes / 12) if self.actual_minutes else 0
class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    chapters = db.relationship('Chapter', backref='subject', cascade="all, delete-orphan", lazy='dynamic')
    def progress(self):
        chapters = self.chapters.all()
        if not chapters:
            return 0
        return int(sum([c.progress() for c in chapters]) / len(chapters))
class Chapter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    topics = db.relationship('Topic', backref='chapter', cascade="all, delete-orphan", lazy='dynamic')
    def progress(self):
        topics = self.topics.all()
        if not topics:
            return 0
        return int(100 * sum([1 for t in topics if t.completed]) / len(topics))
class Topic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id'), nullable=False)
