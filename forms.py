from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, PasswordField, SubmitField, IntegerField, HiddenField
from wtforms.validators import DataRequired, Email, EqualTo, NumberRange, Length, ValidationError
from models import User

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Repeat Password', validators=[
        DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class TaskForm(FlaskForm):
    name = StringField('Task Name', validators=[DataRequired(), Length(max=100)])
    duration_minutes = IntegerField('Duration (minutes)', validators=[
        DataRequired(), NumberRange(min=1, max=480, message="Duration must be between 1 and 480 minutes")])
    submit = SubmitField('Add Task')

class CompleteTaskForm(FlaskForm):
    task_id = HiddenField('Task ID', validators=[DataRequired()])
    actual_minutes = HiddenField('Actual Minutes', validators=[DataRequired()])
    submit = SubmitField('Complete Task')

class ProfileForm(FlaskForm):
    username = StringField('New Username', validators=[DataRequired(), Length(min=4, max=20)])
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[Length(min=6)])
    confirm_password = PasswordField('Confirm New Password', validators=[
        EqualTo('new_password', message='Passwords must match')])
    submit = SubmitField('Update Profile')

    def __init__(self, original_username, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=username.data).first()
            if user is not None:
                raise ValidationError('Username already taken. Please choose a different one.')
