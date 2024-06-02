from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectMultipleField
from wtforms.validators import DataRequired, Email, EqualTo, Length
from flask_wtf.file import FileField, FileRequired, FileAllowed
from .models import Category


from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectMultipleField, SubmitField
from wtforms.validators import DataRequired, Length
from flask_wtf.file import FileField, FileRequired, FileAllowed

class UploadForm(FlaskForm):
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
    user = StringField('User', validators=[DataRequired(), Length(min=3, max=30)])
    caption = StringField('Caption', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[DataRequired(), Length(max=500)])
    categories = SelectMultipleField('Categories', coerce=int)
    submit = SubmitField('Save')

class CategoryForm(FlaskForm):
    name = StringField('Category Name', validators=[DataRequired(), Length(min=1, max=50)])
    submit = SubmitField('Add Category')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=30)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=30)])
    password = PasswordField('Password', validators=[DataRequired(), EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Repeat Password')
    submit = SubmitField('Register')

class CommentForm(FlaskForm):
    content = TextAreaField('Your Comment', validators=[DataRequired()])
    submit = SubmitField('Post Comment')