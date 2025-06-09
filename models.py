from app import db
from flask_login import UserMixin
from datetime import datetime, date
from sqlalchemy import func

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    total_score = db.Column(db.Integer, default=0)
    last_active = db.Column(db.DateTime, default=datetime.utcnow)
    tasks = db.relationship('Task', backref='owner', lazy='dynamic')
    
    def get_badge(self):
        """Get user's badge based on total score"""
        score = self.total_score
        if score == 0:
            return {'name': 'Wood', 'color': '#8B4513'}
        elif 1 <= score <= 50:
            return {'name': 'Bronze', 'color': '#CD7F32'}
        elif 51 <= score <= 100:
            return {'name': 'Bronze 2', 'color': '#CD7F32'}
        elif 101 <= score <= 150:
            return {'name': 'Bronze 3', 'color': '#CD7F32'}
        elif 151 <= score <= 200:
            return {'name': 'Silver', 'color': '#C0C0C0'}
        elif 201 <= score <= 300:
            return {'name': 'Silver 2', 'color': '#C0C0C0'}
        elif 301 <= score <= 400:
            return {'name': 'Silver 3', 'color': '#C0C0C0'}
        elif 401 <= score <= 500:
            return {'name': 'Gold', 'color': '#FFD700'}
        elif 501 <= score <= 600:
            return {'name': 'Gold 2', 'color': '#FFD700'}
        elif 601 <= score <= 700:
            return {'name': 'Gold 3', 'color': '#FFD700'}
        elif 701 <= score <= 800:
            return {'name': 'Gold 4', 'color': '#FFD700'}
        elif 801 <= score <= 950:
            return {'name': 'Platinum', 'color': "#d6d6d6"}
        elif 951 <= score <= 1100:
            return {'name': 'Platinum 2', 'color': '#d6d6d6'}
        elif 1101 <= score <= 1250:
            return {'name': 'Platinum 3', 'color': '#d6d6d6'}
        elif 1251 <= score <= 1400:
            return {'name': 'Platinum 4', 'color': '#d6d6d6'}
        elif 1401 <= score <= 1550:
            return {'name': 'Diamond', 'color': '#61e2ff'}
        elif 1551 <= score <= 1750:
            return {'name': 'Diamond 2', 'color': '#61e2ff'}
        elif 1751 <= score <= 1950:
            return {'name': 'Diamond 3', 'color': '#61e2ff'}
        elif 1951 <= score <= 2200:
            return {'name': 'Diamond 4', 'color': '#61e2ff'}
        elif 2201 <= score <= 2450:
            return {'name': 'Heroic', 'color': "#f34129"}
        elif 2451 <= score <= 2850:
            return {'name': 'Master', 'color': '#9932CC'}
        elif 2851 <= score <= 3500:
            return {'name': 'Elite Master', 'color': '#4B0082'}
        elif 3501 <= score <= 4500:
            return {'name': 'Grand Master', 'color': '#ff9900'}
        else:
            return {'name': 'legend⚜🔱⚜', 'color': "#F0E054FF"}
    
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

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False)
    actual_minutes = db.Column(db.Integer, default=0)
    completed = db.Column(db.Boolean, default=False)
    date_created = db.Column(db.Date, default=date.today)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    def calculate_points(self):
        """Calculate points for this task (1 point per 12 minutes)"""
        return int(self.actual_minutes / 12) if self.actual_minutes else 0
