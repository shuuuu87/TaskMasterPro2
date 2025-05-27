from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, HiddenField
from wtforms.validators import DataRequired, Email, EqualTo, NumberRange, Length
from models import User

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
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
