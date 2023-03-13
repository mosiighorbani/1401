from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, EqualTo, Length, Email
from wtforms import PasswordField, StringField, EmailField, SelectField, FileField





class UserCreateForm(FlaskForm):
    name = StringField('FullName')
    email = EmailField('Email', validators=[DataRequired('پر کردن فیلد الزامی است'), Email('ایمیل معتبر نیست')])
    password = PasswordField('Password', validators=[DataRequired('گذرواژه خود را وارد نمایید'), Length(min=8, message='گذرواژه نباید کمتر از 8 کاراکتر باشد')])
    role = SelectField('Role', choices=[('3', 'کاربر عادی '), ('1', 'کاربر درجه 1'), ('2', 'کاربر درجه 2'), ('0', 'کاربر ادمین')])



class UserEditForm(FlaskForm):
    name = StringField('FullName')
    phone = StringField('Phone')
    avatar = FileField('Avatar')
