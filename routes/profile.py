from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
import os, time
from flask_login import login_required, current_user
from forms import ProfileForm
from app import db
from models import User

profile_bp = Blueprint('profile', __name__)

# ✅ Allowed image extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@profile_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def view_profile():
    form = ProfileForm(original_username=current_user.username)

    if form.validate_on_submit():
        changed = False

        # Username update
        if current_user.username != form.username.data:
            current_user.username = form.username.data
            changed = True

        # Custom image upload (wins over avatar)
        # Set selected avatar only
        avatar_choice = request.form.get('avatar_choice')
        if avatar_choice and avatar_choice != current_user.profile_image:
            current_user.profile_image = avatar_choice
            changed = True


        # Password update
        if form.new_password.data:
            current_user.set_password(form.new_password.data)
            changed = True

        if changed:
            db.session.commit()
            flash('✅ Profile updated successfully!', 'success')
        else:
            flash('⚠️ No changes detected.', 'info')

        return redirect(url_for('profile.view_profile'))

    # Pass badge info and cache-busting timestamp
    badge = current_user.get_badge()
    return render_template('profile.html', form=form, badge=badge, cache_id=str(time.time()))
