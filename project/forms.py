# Importing necessary libraries and modules for form handling and validation.
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectMultipleField
from wtforms.validators import DataRequired, Email, EqualTo, Length
from flask_wtf.file import FileField, FileRequired, FileAllowed
from .models import Category

# Definition of form classes used in the application.

class UploadForm(FlaskForm):
    """Form for uploading photos."""
    user = StringField('User', validators=[DataRequired(), Length(min=3, max=30)])
    caption = StringField('Caption', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[DataRequired(), Length(max=500)])
    categories = SelectMultipleField('Categories', coerce=int)
    fileToUpload = FileField('File', validators=[
        FileRequired(),
        FileAllowed(['jpeg', 'png', 'gif'], 'Image files only!')
    ])
    submit = SubmitField('Upload')

class EditForm(FlaskForm):
    """Form for editing photo details."""
    user = StringField('User', validators=[DataRequired(), Length(min=3, max=30)])
    caption = StringField('Caption', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[DataRequired(), Length(max=500)])
    categories = SelectMultipleField('Categories', coerce=int)
    submit = SubmitField('Save')

class CategoryForm(FlaskForm):
    """Form for adding new categories."""
    name = StringField('Category Name', validators=[DataRequired(), Length(min=1, max=50)])
    submit = SubmitField('Add Category')

class LoginForm(FlaskForm):
    """Form for user login."""
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=30)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    """Form for new user registration."""
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=30)])
    password = PasswordField('Password', validators=[DataRequired(), EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Repeat Password')
    submit = SubmitField('Register')

class CommentForm(FlaskForm):
    """Form for submitting comments on photos."""
    content = TextAreaField('Your Comment', validators=[DataRequired()])
    submit = SubmitField('Post Comment')