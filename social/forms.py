from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, EqualTo, Length, Email
from wtforms import PasswordField, StringField, EmailField, SelectField, FileField, TextAreaField





class UserUpdateForm(FlaskForm):
    about_me = TextAreaField('About Me')
    skill1 = StringField('Skill 1')
    skill2 = StringField('Skill 2')
    skill3 = StringField('Skill 3')
    skill4 = StringField('Skill 4')
    education_grade = StringField('Education Grade')
    education_field = StringField('Education Field')
    education_subfield = StringField('Education Sub Field')
    province = StringField('Province')
    city = StringField('City')
    

class NewPostForm(FlaskForm):
    text = TextAreaField('New Post')


class CommentForm(FlaskForm):
    text = StringField('Comment')