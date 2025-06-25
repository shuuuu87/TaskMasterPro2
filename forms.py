from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, BooleanField, PasswordField, SubmitField, IntegerField, HiddenField, DateTimeField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, NumberRange, Length, ValidationError
from models import User
from wtforms import RadioField

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
        DataRequired(), NumberRange(min=1, max=480, message="Duration must be between 1 and 1000 minutes")])
    submit = SubmitField('Add Task')

class CompleteTaskForm(FlaskForm):
    task_id = HiddenField('Task ID', validators=[DataRequired()])
    actual_minutes = HiddenField('Actual Minutes', validators=[DataRequired()])
    submit = SubmitField('Complete Task')

from wtforms.validators import DataRequired, Email, EqualTo, NumberRange, Length, ValidationError, Optional

class ProfileForm(FlaskForm):
    username = StringField('New Username', validators=[DataRequired(), Length(min=4, max=20)])
    current_password = PasswordField('Current Password')  # No longer required unconditionally
    new_password = PasswordField('New Password', validators=[Length(min=6), Optional()])
    confirm_password = PasswordField('Confirm New Password', validators=[
        EqualTo('new_password', message='Passwords must match'), Optional()
    ])

    avatar_choice = RadioField('Choose an Avatar', choices=[
        ('avatar1.png', 'Avatar 1'),
        ('avatar2.png', 'Avatar 2'),
        ('avatar3.png', 'Avatar 3'),
        ('avatar4.png', 'Avatar 4'),
        ('avatar5.png', 'Avatar 5'),
        ('avatar6.png', 'Avatar 6'),
        ('avatar7.png', 'Avatar 7'),
        ('avatar8.png', 'Avatar 8'),
        ('avatar9.png', 'Avatar 9'),
        ('avatar10.png', 'Avatar 10'),
        ('avatar11.png', 'Avatar 11'),
        ('avatar12.png', 'Avatar 12'),
        ('avatar13.png', 'Avatar 13'),
        ('avatar14.png', 'Avatar 14'),
        ('avatar15.png', 'Avatar 15'),
        ('avatar16.png', 'Avatar 16'),
        ('avatar17.png', 'Avatar 17'),
        ('avatar18.png', 'Avatar 18'),
        ('avatar19.png', 'Avatar 19'),
        ('avatar20.png', 'Avatar 20'),
        ('avatar21.png', 'Avatar 21'),
        ('avatar22.png', 'Avatar 22'),
        ('avatar23.png', 'Avatar 23'),
        ('avatar24.png', 'Avatar 24')
    ])

    submit = SubmitField('Update Profile')

    def __init__(self, original_username, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=username.data).first()
            if user is not None:
                raise ValidationError('Username already taken. Please choose a different one.')

    def validate(self, extra_validators=None):
        if not super().validate(extra_validators=extra_validators):
            return False

        if self.new_password.data and not self.current_password.data:
            self.current_password.errors.append('Enter your current password to set a new one.')
            return False

        return True

