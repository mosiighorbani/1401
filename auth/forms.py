from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, EqualTo, Length, Email, ValidationError
from wtforms import PasswordField, StringField, EmailField, SelectField



class RegisterForm(FlaskForm):
    name = StringField('FullName')
    email = EmailField('Email', validators=[DataRequired('پر کردن فیلد الزامی است'), Email('ایمیل معتبر نیست')])
    password = PasswordField('Password', validators=[DataRequired('گذرواژه خود را وارد نمایید'), Length(min=8, message='گذرواژه نباید کمتر از 8 کاراکتر باشد')])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired('تکرار گذرواژه با گذرواژه یکسان نیست'), EqualTo('password')])
    

    
class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired('پر کردن فیلد الزامی است'), Email('ایمیل معتبر نیست')])
    password = PasswordField('Password', validators=[DataRequired('گذرواژه خود را وارد نمایید'), Length(min=8, message='گذرواژه نباید کمتر از 8 کاراکتر باشد')])
    


class PhoneRegisterForm(FlaskForm):
        phone = StringField('Phone', validators=[DataRequired(), Length(min=11, max=11)])

        def validate_phone(form, field):
            if len(field.data) != 11:
                raise ValidationError('Invalid phone number.')



class ForgotPassForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired('پر کردن فیلد الزامی است'), Email('ایمیل معتبر نیست')])



class ResetPassForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired('گذرواژه خود را وارد نمایید'), Length(min=8, message='گذرواژه نباید کمتر از 8 کاراکتر باشد')])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired('تکرار گذرواژه با گذرواژه یکسان نیست'), EqualTo('password')])
