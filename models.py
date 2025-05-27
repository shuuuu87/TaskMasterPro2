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
        elif 201 <= score <= 250:
            return {'name': 'Silver 2', 'color': '#C0C0C0'}
        elif 251 <= score <= 300:
            return {'name': 'Silver 3', 'color': '#C0C0C0'}
        elif 301 <= score <= 400:
            return {'name': 'Gold', 'color': '#FFD700'}
        elif 401 <= score <= 500:
            return {'name': 'Gold 2', 'color': '#FFD700'}
        elif 501 <= score <= 600:
            return {'name': 'Gold 3', 'color': '#FFD700'}
        elif 601 <= score <= 700:
            return {'name': 'Gold 4', 'color': '#FFD700'}
        elif 701 <= score <= 850:
            return {'name': 'Platinum', 'color': '#c9aff8'}
        elif 851 <= score <= 1000:
            return {'name': 'Platinum 2', 'color': '#c9aff8'}
        elif 1001 <= score <= 1150:
            return {'name': 'Platinum 3', 'color': '#c9aff8'}
        elif 1151 <= score <= 1300:
            return {'name': 'Platinum 4', 'color': '#c9aff8'}
        elif 1301 <= score <= 1450:
            return {'name': 'Diamond', 'color': '#61e2ff'}
        elif 1451 <= score <= 1600:
            return {'name': 'Diamond 2', 'color': '#61e2ff'}
        elif 1601 <= score <= 1750:
            return {'name': 'Diamond 3', 'color': '#61e2ff'}
        elif 1751 <= score <= 1900:
            return {'name': 'Diamond 4', 'color': '#61e2ff'}
        elif 1901 <= score <= 2100:
            return {'name': 'Heroic', 'color': '#f32929'}
        elif 2101 <= score <= 2350:
            return {'name': 'Master', 'color': '#9932CC'}
        elif 2351 <= score <= 2650:
            return {'name': 'Elite Master', 'color': '#4B0082'}
        else:
            return {'name': 'Grand Master', 'color': "#ff9900"}
    
    def is_online(self):
        """Check if user is online (active within last 5 minutes)"""
        from datetime import timedelta
        if not self.last_active:
            return False
        return datetime.utcnow() - self.last_active < timedelta(minutes=5)
    
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
