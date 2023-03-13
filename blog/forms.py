from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, EqualTo, Length, Email
from wtforms import PasswordField, StringField, EmailField, SelectField, FileField, TextAreaField, BooleanField
from flask_ckeditor import CKEditorField




class PostCreateForm(FlaskForm):
    title = StringField('Title')
    content = CKEditorField('Content')
    image = FileField('Image')
    publish = BooleanField('Publish', default=0)



class CommentForm(FlaskForm):
    body = StringField('Comment', validators=[DataRequired()])