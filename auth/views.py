import random
from flask import redirect, render_template, request, url_for, flash, session
from app import db, mail
from . import auth
from flask_login import current_user, login_user, logout_user, login_required
from .forms import RegisterForm, LoginForm, PhoneRegisterForm, ForgotPassForm, ResetPassForm
from .models import User
from sqlalchemy.exc import IntegrityError
from utils import isvalid_email_admin
from utils import admin_required
from flask_mail import Message
from uuid import uuid4






@auth.route('register', methods=['POST', 'GET'])
def register():
    if current_user.is_authenticated:
        flash('user is logged previously', 'warning')
        # return redirect(url_for('admin.index'))
        return 'user is logged previously' # TODO   must change to dashboard page

    form = RegisterForm()

    if request.method == 'POST':
        if form.validate_on_submit():
            name = request.form.get('name')
            email = request.form.get('email')
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')
            if name == 'admin' or isvalid_email_admin(email) is False:
                flash('you dont permission to  regiser new user with admin name or admin email', 'danger')
                flash('please, dont repeat this action again', 'danger')
                return redirect(url_for('auth.register'))
            if password == confirm_password:
                new_user = User()
                new_user.name = name
                new_user.email = email
                new_user.set_password(password)
                try:
                    db.session.add(new_user)
                    db.session.commit()
                    flash(f'user {new_user.name} is created successfully', 'success')
                    return redirect(url_for('auth.login')) # TODO : must change to login page !!
                except IntegrityError:
                    db.session.rollback()
                    flash('Unfortunatly, new user is not registered !')
                    return redirect(url_for('auth.register', form=form))
            else:
                flash('your password and conform password is not equal', 'danger')
                return redirect(url_for('auth.register', form=form))
        else:
            flash('your form data is not valid', 'danger')
            return redirect(url_for('auth.register', form=form))
                    

    return render_template('auth/register.html', form=form)



@auth.route('login', methods=['POST','GET'])
def login():
    if current_user.is_authenticated:
        return 'user is logged previously' # TODO    must changed to dashboard page
    
    form = LoginForm()

    if request.method == 'POST':
        if form.validate_on_submit():
            email = request.form.get('email')
            password = request.form.get('password')
            user = User.query.filter_by(email=email).first()
            print('user is --->', user)
            if not user:
                flash(f'this email {email} does not registered', 'warning')
                return redirect(url_for('auth.register'))
            if user.check_password(password):
                flash(f'welcome {user.name}', 'info')
                # login_user(user, remember=form.remember.data) # TODO insert checkbox field in login-form
                login_user(user)
                return redirect(url_for('admin.index'))
            else:
                flash('your password is incorrect', 'danger')
                return redirect(url_for('auth.login', form=form))


    return render_template('auth/login.html', form=form)



@auth.route('logout', methods=['GET'])
@login_required
def logout():
    # user = current_user
    # flash(f'{user.name} is log out', 'warning')
    logout_user()
    return redirect(url_for('auth.login'))

    

@auth.route('createsuperuser', methods=['GET'])
def createsuperuser():
    if current_user.is_authenticated:
        return redirect(url_for('auth.logout'))
    old_superuser = User.query.filter_by(role=0).first()
    print('old super user is : ', old_superuser)
    if not old_superuser:
        superuser = User()
        superuser.name = 'admin'
        superuser.email = 'admin@email.com'
        superuser.set_password('iamsuperuser')
        superuser.role = 0
        try:
            db.session.add(superuser)
            db.session.commit()
            flash('the super user is created successfully', 'success')
            return redirect(url_for('auth.login'))
        except IntegrityError as error:
            print('error is : ', error)
            db.session.rollback()
            flash('Unfortunatly, super user is not registered !', 'warning')
            return redirect(url_for('auth.register'))

    flash('the super user is created previously, dont repaet this action', 'danger')
    return redirect(url_for('auth.register'))



# TODO must register phone number by ajax even design by popup
@auth.route('phone-register', methods=['GET', 'POST'])
@login_required
def phone_register():
    form = PhoneRegisterForm()
    if request.method == 'POST':
        if form.validate_on_submit:
            phone_number = request.form.get('phone')
            user_phone = User.query.filter_by(phone=phone_number).first()
            if current_user != user_phone:
                flash('this phone number is register by another user, please try by different phone number', 'warning')
                return redirect(url_for('auth.phone_register', form=form))
            code = str(random.randint(10000, 99999))
            print('phone_number is :', phone_number) # TODO must send code to this number by kavenegar
            print('='*40)
            print('verify code for mobile is : ', code)
            print('='*40)
            session['verify_code'] = code
            session['phone_number'] = phone_number
            return redirect(url_for('auth.phone_auth'))

    return render_template('admin/phone-register.html', form=form)



@auth.route('phone-auth', methods=['GET', 'POST'])
@login_required
def phone_auth():
    if request.method == 'POST':
        code = request.form.get('code')
        print('verify code is : ',session.get('verify_code'))
        phone_number = str(session.get('phone_number'))
        user_phone = User.query.filter_by(phone=phone_number).first()
        if code == str(session.get('verify_code')):
            try:
                user_phone.phone_auth = True
                db.session.add(user_phone)
                db.session.commit()
            except:
                pass
            flash(f'your mobile number {user_phone.phone} is authenticated', 'success')
            del session['verify_code']
            del session['phone_number']
            return redirect(url_for('admin.index'))
        else:
            flash('your code is wrong and your mobile number is not authenticated,', 'danger')
            del session['verify_code']
            del session['phone_number']
            return redirect(url_for('auth.phone_register'))

    return render_template('admin/phone-auth.html')



@auth.route('forgot-pass', methods=['POST', 'GET'])
def forgot_pass():
    print('*'*30)
    print(request.url_root)
    print('*'*30)
    form = ForgotPassForm()
    if request.method == 'POST':
        if form.validate_on_submit:
            email = request.form.get('email')
            token = str(uuid4())
            user = User.query.filter_by(email=email).first()
            if user:
                user.token = token
                try:
                    db.session.add(user)
                    db.session.commit()
                except IntegrityError:
                    flash(IntegrityError, 'warning')
                    return redirect(url_for('auth.forget_pass'))
                # ============== Message Config ======================================
                msg = Message('Reset Password From Dashboad Page', sender = 'peter@mailtrap.io', recipients = [f'{email}'])
                msg.body = f"""<a href='{request.url_root}auth/reset-pass/{user.id}/{token}'>Reset Password</a>"""
                # mail.send(msg)
                # =====================================================================
                return msg.body # TODO we must active email sender for send emailinstead return link. we can use https://mailtrap.io for this work
            else:
                flash(f'this email {email} is not registered yet', 'danger')
                return redirect(url_for('auth.forgot_pass'))

    return render_template('auth/forgot-pass.html', form=form)



@auth.route('reset-pass/<int:user_id>/<string:token>', methods=['POST', 'GET'])
def reset_pass(user_id, token):
    form = ResetPassForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')
            if password == confirm_password:
                user = User.query.filter_by(id=user_id, token=token).first()
                user.set_password(password)
                user.token = ''
                try:
                    db.session.add(user)
                    db.session.commit()
                    flash('your Password is changed successfully', 'success')
                    return redirect(url_for('auth.login'))
                except IntegrityError:
                    flash(IntegrityError, 'warning')
                    return redirect(url_for('auth.forgot_pass'))
    
    return render_template('auth/reset-pass.html', form=form, user_id=user_id, token=token)

