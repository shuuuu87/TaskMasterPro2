# routes/public.py
from flask import Blueprint, render_template

public_bp = Blueprint('public', __name__)

@public_bp.route('/')
def landing_page():
    return render_template('public/landing.html')

@public_bp.route('/about')
def about():
    return render_template('public/about.html')

@public_bp.route('/features')
def features():
    return render_template('public/features.html')

@public_bp.route('/demo')
def demo():
    return render_template('public/demo.html')

@public_bp.route('/why-us')
def why_us():
    return render_template('public/why_us.html')

@public_bp.route('/preview-tasks')
def preview_tasks():
    return render_template('public/preview_tasks.html')

@public_bp.app_context_processor
def inject_nav_items():
    return {
        'nav_links': [
            {'name': 'Home', 'url': '/'},
            {'name': 'About', 'url': '/about'},
            {'name': 'Features', 'url': '/features'},
            {'name': 'Demo', 'url': '/demo'},
            {'name': 'Why Us', 'url': '/why-us'},
            {'name': 'Preview Tasks', 'url': '/preview-tasks'},
            {'name': 'Login', 'url': '/login'},
            {'name': 'Register', 'url': '/register'},
        ]
    }
