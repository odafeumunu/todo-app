from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, EmailField, DateTimeLocalField, BooleanField, FileField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from flask_wtf.file import FileField, FileAllowed, FileRequired

class Registration(FlaskForm):
    name = StringField("Enter Name:", validators=[DataRequired()])
    email = EmailField("Enter Email:", validators=[DataRequired(), Email()])
    password = PasswordField("Enter Password:", validators=[DataRequired(), Length(min=8)])
    submit = SubmitField("Sign Up")


class Login(FlaskForm):
    email = EmailField("Enter Email:", validators=[DataRequired(), Email()])
    password = PasswordField("Enter Password:", validators=[DataRequired()])
    submit = SubmitField("Sign In")


class ResetPassword(FlaskForm):
    email = EmailField("Enter Your Registered Email:", validators=[DataRequired(), Email()])
    submit = SubmitField("Reset Password")


class NewPasswordForm(FlaskForm):
    password = PasswordField("New Password", validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password"), Length(min=8)])
    submit = SubmitField("Reset Password")


class AddTask(FlaskForm):
    add_task = StringField(validators=[DataRequired()] )
    due_date = DateTimeLocalField("Set due date and time:", format="%Y-%m-%dT%H:%M", validators=[DataRequired()])
    

class CompleteTaskForm(FlaskForm): 
    checkbox = BooleanField()


class ImageUploadForm(FlaskForm): 
    image = FileField(validators=[FileRequired(), FileAllowed(['jpg', 'png', 'jpeg', 'gif'])])