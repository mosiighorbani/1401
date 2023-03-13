from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Length
from wtforms import StringField, FileField, SelectField, IntegerField, ValidationError
from .models import Category, Product
from flask import flash

class ProductForm(FlaskForm):
    name = StringField('Product Name')
    price = StringField('Price', validators=[Length(min=0)])
    # category = SelectField('Category', choices=[(index+1, cat) for index,cat in enumerate(Category.query.all())])
    category = SelectField('Category', choices=[(cat.id, cat.title) for cat in Category.query.all()])
    number = StringField('Number', validators=[Length(min=0)])
    image = FileField('Image')
    rating = StringField('Rating', validators=[Length(min=0, max=5)])
    # role = SelectField('Role', choices=[('3', 'کاربر عادی '), ('1', 'کاربر درجه 1'), ('2', 'کاربر درجه 2'), ('0', 'کاربر ادمین')])



class CategoryForm(FlaskForm):
    title = StringField('Category Name')


class UserInfoForm(FlaskForm):
    phone = StringField('Phone', validators=[DataRequired(), Length(min=11, max=11)])
    province = StringField('Province')
    city = StringField('City')
    street = StringField('Street')
    post_code = StringField('Post Code', validators=[DataRequired(), Length(min=10, max=10)])

    def validate_phone(form, field):
        if len(field.data) != 11:
            flash('your mobile number is incorrect, please try again', 'warning')
            raise ValidationError('شماره همراه نامعتبر است')
        
    def validate_post_code(form, field):
        if len(field.data) != 10:
            raise ValidationError('کد پستی غیرمعتبر است')

