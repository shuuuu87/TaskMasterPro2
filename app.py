import os
import logging
from datetime import datetime, timedelta
from flask import Flask, send_from_directory, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()

# create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///task_manager.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=365*100)

# initialize extensions
db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'

# update last active
@app.before_request
def update_last_active():
    if request.endpoint in ('static',) or request.path == '/favicon.ico':
        return
    if current_user.is_authenticated:
        current_user.last_active = datetime.utcnow()
        db.session.commit()
        logging.debug(f"Updated last_active for {current_user.username} at {current_user.last_active}")

# user loader
@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

# Register blueprints
from routes.public import public_bp
from routes.auth import auth_bp
from routes.home import home_bp
from routes.progress import progress_bp
from routes.syllabus import syllabus_bp
from routes.leaderboard import leaderboard_bp

load_dotenv()

app.register_blueprint(public_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(home_bp)
app.register_blueprint(progress_bp)
app.register_blueprint(leaderboard_bp)
app.register_blueprint(syllabus_bp)

# Create tables
with app.app_context():
    import models
    db.create_all()

@app.route('/sitemap.xml')
def sitemap_xml():
    return send_from_directory(os.path.abspath(os.path.dirname(__file__)), 'sitemap.xml', mimetype='application/xml')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
