
# -------------------- IMPORTS --------------------
import os
import logging
import random
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from flask import Flask, send_from_directory, request
from extensions import db
from flask_login import LoginManager, current_user
from flask_mail import Mail, Message
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

# -------------------- CONFIG & LOGGING --------------------
logging.basicConfig(level=logging.DEBUG)
load_dotenv()

# -------------------- APP & EXTENSIONS INIT --------------------
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

import pathlib
# Database config: Neon on Render, instance/task_manager.db locally
db_url = os.environ.get('DATABASE_URL')
if db_url:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
else:
    # Ensure the instance directory exists before using it for SQLite
    pathlib.Path('instance').mkdir(exist_ok=True)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./instance/task_manager.db'
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=365*100)

# Flask-Mail SMTP configuration
app.config['MAIL_SERVER'] = 'taskmaster.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'taskmasterpro37@gmail.com'
app.config['MAIL_PASSWORD'] = 'shreyash@123'
app.config['MAIL_DEFAULT_SENDER'] = 'taskmasterpro37@gmail.com'

# -------------------- EXTENSIONS --------------------
class Base(DeclarativeBase):
    pass
db.model_class = Base
login_manager = LoginManager()
mail = Mail(app)
db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'

# -------------------- MOTIVATIONAL QUOTES --------------------
MOTIVATIONAL_QUOTES = {
    'morning': [
        ("Good morning! ☀️", "Rise and shine! Every day is a new opportunity to grow. 🌱"),
        ("Start your day strong! 💪", "Success is the sum of small efforts, repeated day in and day out. ✨"),
        ("Hello, Achiever! 🚀", "The secret of getting ahead is getting started. Let's do this! 🏁")
    ],
    'afternoon': [
        ("Keep Going! 🌞", "The difference between ordinary and extraordinary is that little extra. Keep pushing! 🔥"),
        ("Midday Motivation! 🕑", "Don’t watch the clock; do what it does. Keep going. ⏰"),
        ("Stay Focused! 🎯", "Your only limit is your mind. Believe in yourself! 💡")
    ],
    'evening': [
        ("Well Done! 🌙", "Every accomplishment starts with the decision to try. Reflect and recharge! 🌌"),
        ("Evening Reflection ✨", "Success is not final, failure is not fatal: It is the courage to continue that counts. 💫"),
        ("You Did Great Today! 🏆", "Small steps every day lead to big results. Rest well! 😴")
    ]
}

# -------------------- EMAIL HELPERS --------------------
def send_email(subject, recipients, body):
    try:
        msg = Message(subject, recipients=recipients, body=body)
        mail.send(msg)
    except Exception as e:
        logging.error(f"Failed to send email: {e}")

def send_motivational_email_to_all(time_of_day):
    from models import User
    quotes = MOTIVATIONAL_QUOTES[time_of_day]
    subject, body = random.choice(quotes)
    with app.app_context():
        users = User.query.all()
        for user in users:
            personalized_body = f"Hi {user.username},\n\n{body}\n\n- ProductivityPilot Team"
            send_email(subject, [user.email], personalized_body)

# -------------------- USER SESSION --------------------
@app.before_request
def update_last_active():
    if request.endpoint in ('static',) or request.path == '/favicon.ico':
        return
    if current_user.is_authenticated:
        current_user.last_active = datetime.now(ZoneInfo("Asia/Kolkata"))
        db.session.commit()
        logging.debug(f"Updated last_active for {current_user.username} at {current_user.last_active}")

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

# -------------------- BLUEPRINTS --------------------
from routes.public import public_bp
from routes.auth import auth_bp
from routes.home import home_bp
from routes.progress import progress_bp
from routes.syllabus import syllabus_bp
from routes.leaderboard import leaderboard_bp
from routes.profile import profile_bp
from routes.race import race_bp
from routes.race_result_api import race_result_api
from routes.claim import claim_bp
from routes.get_unclaimed_race import get_unclaimed_race_bp

app.register_blueprint(public_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(home_bp)
app.register_blueprint(progress_bp)
app.register_blueprint(leaderboard_bp)
app.register_blueprint(syllabus_bp)
app.register_blueprint(profile_bp)
app.register_blueprint(race_bp)
app.register_blueprint(race_result_api)
app.register_blueprint(claim_bp)
app.register_blueprint(get_unclaimed_race_bp)

# -------------------- DB & SCHEDULER INIT --------------------
with app.app_context():
    import models
    db.create_all()

    scheduler = BackgroundScheduler(timezone=ZoneInfo("Asia/Kolkata"))
    def send_morning_emails():
        send_motivational_email_to_all('morning')
    def send_afternoon_emails():
        send_motivational_email_to_all('afternoon')
    def send_evening_emails():
        send_motivational_email_to_all('evening')

    scheduler.add_job(
        func=send_morning_emails,
        trigger='cron', hour=8, minute=0, id='motivation_morning', replace_existing=True
    )
    scheduler.add_job(
        func=send_afternoon_emails,
        trigger='cron', hour=13, minute=0, id='motivation_afternoon', replace_existing=True
    )
    scheduler.add_job(
        func=send_evening_emails,
        trigger='cron', hour=19, minute=0, id='motivation_evening', replace_existing=True
    )
    scheduler.add_jobstore(SQLAlchemyJobStore(url=app.config["SQLALCHEMY_DATABASE_URI"]), 'default')
    scheduler.start()

    from models import Race
    def finish_race(race_id):
        race = Race.query.get(race_id)
        if race and race.status != 'finished' and datetime.utcnow() >= race.end_time:
            race.status = 'finished'
            db.session.commit()
            logging.info(f"Race {race.id} marked as finished at {datetime.utcnow()}")

    for race in Race.query.filter_by(status='ongoing').all():
        if race.end_time > datetime.utcnow():
            scheduler.add_job(
                func=finish_race,
                trigger=DateTrigger(run_date=race.end_time),
                args=[race.id],
                id=f'finish_race_{race.id}',
                replace_existing=True
            )

    def send_race_result_emails(race):
        from models import User
        if race.winner_id and race.loser_id:
            winner = User.query.get(race.winner_id)
            loser = User.query.get(race.loser_id)
            winner_subject = "🏆 Congratulations! You Won the Race!"
            winner_body = (
                f"Hi {winner.username},\n\n"
                f"The race has ended and you are the winner!\n"
                f"You scored {race.winner_points} points more than your opponent.\n\n"
                "Keep up the great work and keep racing!\n\n"
                "- ProductivityPilot Team"
            )
            send_email(winner_subject, [winner.email], winner_body)
            loser_subject = "Race Finished - Don't Give Up!"
            loser_body = (
                f"Hi {loser.username},\n\n"
                "The race has ended. You gave your best effort!\n"
                f"You scored {race.loser_points} points.\n\n"
                "Remember, every setback is a setup for a comeback. Keep pushing and join another race soon!\n\n"
                "- ProductivityPilot Team"
            )
            send_email(loser_subject, [loser.email], loser_body)

    def finish_expired_races():
        now = datetime.now(ZoneInfo("Asia/Kolkata"))
        from models import Race
        expired_races = Race.query.filter(
            Race.end_time <= now,
            Race.status != 'finished'
        ).all()
        for race in expired_races:
            race.status = 'finished'
            send_race_result_emails(race)
        db.session.commit()
        if expired_races:
            logging.info(f"Marked {len(expired_races)} races as finished at {now}")

    scheduler.add_job(
        func=finish_expired_races,
        trigger='interval',
        hours=3,
        id='finish_expired_races',
        replace_existing=True
    )

# -------------------- ROUTES --------------------
@app.route('/sitemap.xml')
def sitemap_xml():
    return send_from_directory(os.path.abspath(os.path.dirname(__file__)), 'sitemap.xml', mimetype='application/xml')

# -------------------- MAIN --------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
