import os
import datetime
from queue import Empty
from flask import redirect, render_template, url_for, flash, request
from app import db, app
from . import admin
from flask_login import login_required, current_user
from auth.models import User
from sqlalchemy.exc import IntegrityError
from utils import admin_required, allow_extension
from .forms import UserCreateForm, UserEditForm
from werkzeug.utils import secure_filename





@admin.route('', methods=['POST', 'GET'])
@login_required
def index():
    users = User.query.all()
    
    return render_template('admin/dashboard.html', users=users)


@admin.route('users', methods=['POST','GET'])
@login_required
@admin_required
def users():
    page = request.args.get('page', default=1, type=int)
    # users = User.query.all()
    users = User.query.paginate(page=page, per_page=4)

    return render_template('admin/users.html', users=users)


@admin.route('user-create', methods=['POST', 'GET'])
@login_required
@admin_required
def user_create():
    form = UserCreateForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            old_user = User.query.filter_by(email=request.form.get('email')).first()
            if old_user:
                flash(f'the email {old_user.email} is registered prevoiusly, please try again by another email', 'warning')
                return redirect(url_for('admin.user_create', form=form))
            user = User()
            user.name = request.form.get('name')
            user.email = request.form.get('email')
            user.password = request.form.get('password')
            user.role = int(request.form.get('role'))
            # user.role = [User.query.get(role) for role in form.role.data]
            try:
                db.session.add(user)
                db.session.commit()
                flash(f'new user {user.name} is created successfully', 'success')
                return redirect(url_for('admin.user_create', form=form))
            except IntegrityError():
                db.session.rollback()
                flash('Unfortunatly, user does not created', 'warning')
                return redirect(url_for('admin.user_create', form=form))
            
        flash('your form data is not valid', 'danger')
    return render_template('/admin/user-create.html', form=form)


@admin.route('user-delete/<int:user_id>', methods=['GET'])
def user_delete(user_id):
    User.query.filter_by(id=user_id).delete()
    db.session.commit()
    return redirect(url_for('admin.users'))


@admin.route('user-edit/<int:user_id>', methods=['POST', 'GET'])
@login_required
def user_edit(user_id):
    form = UserEditForm()
    user = User.query.filter_by(id=user_id).first()
    page = request.args.get('page')
    address = request.args.get('address')
    print('current page is :', page)
    print('current address is :', address)
    print(type(page))
    print(type(address))
    if request.method == 'POST':
        if form.validate_on_submit():
            phone_exist = request.form.get('phone')
            user_has_phone = User.query.filter_by(phone=phone_exist).first()
            if user_has_phone and user_has_phone != user and user_has_phone != '':
                flash(f'the phone of {user_has_phone.phone} is registered by someone, please try again by another phone number', 'warning')
                return redirect(url_for('admin.user_edit', user_id=user.id, form=form))

            user.name = request.form.get('name')
            user.phone = request.form.get('phone')
            
            if 'avatar' not in request.files:
                flash('image is not selected properly. if you wanna a profile image, please try again', 'warning')
                # return redirect(url_for('admin.user_edit', user_id=user.id, form=form))
            avatar = request.files.get('avatar')
            if avatar:
                filename = avatar.filename
                file_secure = secure_filename(filename) 
                if not allow_extension(file_secure):
                    flash('extension file is not allowed', 'warning')
                    return redirect(url_for('admin.user_edit', user_id=user.id, form=form))
                today = datetime.date.today()
                folder = os.path.join(app.config['UPLOAD_DIR'], f'{user.name}', f'{today}')
                try:
                    os.makedirs(folder)
                except:
                    pass
                file = os.path.join(folder, file_secure)
                avatar.save(file)
                # avatar.save(os.path.join(app.config['UPLOAD_DIR'], file_secure))
                
                user.avatar = f'uploads/{user.name}/{today}/{filename}'
            # end of if statement
            try:
                db.session.add(user)
                db.session.commit()
                flash(f'user {user.name} is editted successfully', 'success')
                if address == 'users':
                    return redirect(url_for('admin.users, page=page'))
                return redirect(url_for('admin.index'))
            except IntegrityError():
                db.session.rollback()
                flash('Unfortunatly, user does not edit', 'warning')
                return redirect(url_for('admin.user_edit', user=user, form=form))
            # end of if
        # end of if form validate
        flash('your form data is not valid', 'danger')
        return redirect(url_for('admin.user_edit', user_id=user.id, form=form))
    # end of post request
    return render_template('/admin/user-edit.html', user=user, form=form)


@admin.route('user-status/<int:user_id>', methods=['POST','GET'])
@login_required
@admin_required
def user_status(user_id):
    user = User.query.filter_by(id=user_id).first()
    user.active = not(user.active)
    db.session.add(user)
    db.session.commit()
    # flash(f'user {user.name} is {user.active}', 'info')
    return redirect(url_for('admin.users'))


@admin.route('change-role/<int:user_id>/<int:role>', methods=['POST', 'GET'])
@login_required
@admin_required
def change_role(user_id, role):
    user = User.query.filter_by(id=user_id).first()
    user.role = int(role)
    try:
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('admin.users'))
    except Exception as error:
        flash(f"error {error} is happend", 'danger')
        return redirect(url_for('admin.users'))




