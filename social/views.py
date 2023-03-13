import os
import datetime
from flask import redirect, render_template, url_for, flash, request, Markup
from app import db, app
from . import social
from .forms import UserUpdateForm, NewPostForm, CommentForm
from flask_login import login_required, current_user
from auth.models import User
from sqlalchemy.exc import IntegrityError
from utils import admin_required, allow_extension
from werkzeug.utils import secure_filename
from .models import Follower, Post, SocialComment, SocialReply, SocialLike




@social.route('/<string:username>', methods=['POST', 'GET'])
@login_required
def index(username):
    form = UserUpdateForm()
    comment_form = CommentForm()
    user = User.query.filter_by(name=username).first()
    follower = Follower.query.filter_by(follow_to=user.id).all()
    following = Follower.query.filter_by(follow_from=user.id).all()
    user_post = Post.query.filter_by(user_id=user.id).all()
    social_comments = SocialComment.query.all()
    user_follow_post = []
    for usr in following:
        user_follow_post.append(Post.query.filter_by(id=usr.follow_to).first())

    print('*'*50)    
    print(user_follow_post)
    print('*'*50)
    if request.method == 'POST':
        if form.validate_on_submit():
            user.about_me = request.form.get('about_me')
            user.skills = f"{request.form.get('skill1')},{request.form.get('skill2')},{request.form.get('skill3')},{request.form.get('skill4')}"
            user.address = f"{request.form.get('province')},{request.form.get('city')}"
            user.education = f"{request.form.get('education_grade')},{request.form.get('education_field')},{request.form.get('education_subfield')}"
            try:
                db.session.add(user)
                db.session.commit()
                flash('your data is registered successfully', 'success')
                # message = Markup("<span style='direction:rtl> your data is  registerd successfully </span>")
                # flash(message, 'success')
            except IntegrityError as er:
                db.rolleback()
                flash(f'{er} is happened, your data is not registerd properly', 'danger')
            finally:
                return redirect(url_for('social.index' , form=form,
                                         user=user, username=user.name, follower=follower,
                                           following=following, user_post=user_post, 
                                           user_follow_post=user_follow_post, comment_form=comment_form, social_comments=social_comments))
    

    form.about_me.data = user.about_me
    return render_template('social/index.html', form=form,
                            user=user, username=user.name, follower=follower,
                            following=following, user_post=user_post, 
                            user_follow_post=user_follow_post, comment_form=comment_form, social_comments=social_comments)




@social.route('/follow/<int:user_id>/<string:username>', methods=['POST','GET'])
@login_required
def follow(user_id, username): # for another projet must create username field for working correctly 
    following = User.query.filter_by(id=user_id).one()
    followed = User.query.filter_by(name=username).first()
    followed_done = Follower.query.filter_by(follow_from=following.id, follow_to=followed.id).first()
    if followed_done:
        db.session.delete(followed_done)
        db.session.commit()
        return redirect(url_for('social.index', username=username))
    else:
        follow = Follower()
        follow.follow_from = following.id
        follow.follow_to = followed.id
        try:
            db.session.add(follow)
            db.session.commit()
            return redirect(url_for('social.index', username=username))
        except IntegrityError as error:
            db.session.rollback()
            flash(f'Error {error} is happened, please try again', 'warning')
            return redirect(url_for('social.index', username=username))



@social.route('/newpost/<string:username>', methods=['POST', 'GET'])
@login_required
def newpost(username):
    user = User.query.filter_by(name=username).first()
    form = NewPostForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            post = Post()
            post.text = request.form.get('text')
            post.user_id = user.id
            try:
                db.session.add(post)
                db.session.commit()
                flash('your post is created successfully', 'success')
                # return redirect(url_for('social.index', user=user, username=user.name))
            except IntegrityError as er:
                db.session.rollback()
                flash(f'your data is not register, {er} is happened', 'danger')
                # return redirect(url_for('social.index', user=user, username=user.name))
            finally:
                return redirect(url_for('social.index', user=user, username=user.name))
            
        flash('your form is not validate on submit, please try again', 'danger')

    return render_template('social/create-post.html', user=user, form=form)



@social.route('/comment/<int:post_id>', methods=['POST'])
def social_comment(post_id):
    form = CommentForm()
    if request.method == "POST":
        if form.validate_on_submit():
            text = request.form.get('text')
            comment = SocialComment()
            comment.post_id = post_id
            comment.user_id = current_user.id
            comment.text = text
            try:
                db.session.add(comment)
                db.session.commit()
                flash('your comment was sent successfully', 'success')
            except IntegrityError as er:
                db.session.rollback()
                flash('an error is occure, please try again', 'warning')
            finally:
                return redirect(url_for('social.index', username=current_user.name))
                # return True
            
        flash('your form is not send, please try again', 'warning')

    return redirect(url_for('social.index', username=current_user.name))


@social.route('/reply/<int:post_id>/<int:comment_id>', methods=['POST'])
def social_reply(post_id, comment_id):
    form = CommentForm()
    if request.method == 'POST' and form.validate_on_submit():
        text = request.form.get('text')
        reply = SocialReply()
        reply.text = text
        reply.user_id = current_user.id
        reply.post_id = post_id
        reply.comment_id = comment_id
        try:
            db.session.add(reply)
            db.session.commit()
            flash('your reply is sent successfully', 'success')
        except IntegrityError as er:
            db.session.rollback()
            flash(f'error {er} is happened, please try again', 'warning')
        finally:
            return redirect(url_for('social.index', username=current_user.name))
    
    flash('form is not response correctly', 'warning')
        
    return redirect(url_for('social.index', username=current_user.name))


    
@social.route('social-like/<int:user_id>/<int:post_id>', methods=['GET'])
def social_like(user_id, post_id):
    user_liked = SocialLike.query.filter_by(user_id=user_id, post_id=post_id).first()
    if user_liked:
        db.session.delete(user_liked)
        db.session.commit()
    else:
        user_like = SocialLike()
        user_like.user_id = user_id
        user_like.post_id = post_id
        db.session.add(user_like)
        db.session.commit()
    
    return redirect(url_for('social.index', username=current_user.name))


