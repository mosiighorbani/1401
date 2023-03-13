import os
import jdatetime
import json
from flask import redirect, url_for, render_template, flash, request
from flask_login import login_required, current_user
from app import db, app
from . import blog
from auth.models import User
from .forms import PostCreateForm, CommentForm
from .models import Post, Comment, PostLikes, Reply
from werkzeug.utils import secure_filename
from utils import allow_extension
from sqlalchemy.exc import IntegrityError
from sqlalchemy import desc






@blog.route('post-create', methods=['POST', 'GET'])
@login_required
def post_create():
    form = PostCreateForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            new_post = Post()
            new_post.title = request.form.get('title')
            new_post.content = request.form.get('content')
            new_post.publish = 1 if request.form.get('publish') == 'y' else 0
            new_post.user_id = current_user.id
            print('image is ',request.files.get('image'))
            image = request.files.get('image')
            if image.filename == '':
                flash('image file is not selected properly', 'warning')
                return redirect(url_for('blog.post_create', form=form))
            if image:
                filename = image.filename
                file_secure = secure_filename(filename)
                if not allow_extension(file_secure):
                    flash('this extension for image file is not allowed', 'warning')
                    return redirect(url_for('blog.post_create', form=form))
                today = jdatetime.date.today()
                folder = os.path.join(app.config['UPLOAD_DIR'], 'blog', f'{today}')
                try:
                    os.makedirs(folder)
                except:
                    pass
                file = os.path.join(folder, file_secure)
                image.save(file)
                new_post.image = f'uploads/blog/{today}/{filename}'
            try:
                db.session.add(new_post)
                db.session.commit()
                flash(f'the Post {new_post.title} is created successfully', 'success')
                return redirect(url_for('blog.post_create', form=form))
            except IntegrityError():
                db.session.rollback()
                flash(IntegrityError, 'error')
                return redirect(url_for('blog.post_create', form=form))
            
    return render_template('blog/post-create.html', form=form)



@blog.route('posts', methods=['POST', 'GET'])
def posts():
    # posts = Post.query.all()
    page = request.args.get('page', default=1, type=int)
    # posts = Post.query.order_by(desc(Post.created_at)).paginate(page=page, per_page=4)
    posts = Post.query.order_by(Post.id.desc()).paginate(page=page, per_page=4)
    
    return render_template('blog/posts.html', posts=posts)



@blog.route('post-publish/<int:post_id>', methods=['GET']) # TODO this function must be ajax
@login_required
def post_publish(post_id):
    post = Post.query.filter_by(id=post_id).first()
    post.publish = not(post.publish)
    db.session.add(post)
    db.session.commit()
    return redirect(url_for('blog.posts'))



@blog.route('post-edit/<int:post_id>', methods=['POST', 'GET'])
@login_required
def post_edit(post_id):
    form = PostCreateForm()
    post = Post.query.filter_by(id=post_id).first()
    form.content.data = post.content
    if request.method == 'POST':
        post.title = request.form.get('title')
        post.content = request.form.get('content')
        post.publish = 1 if request.form.get('publish') == 'y' else 0
        image = request.files.get('image')
        print('image is : ', image)
        if image.filename == '':
            flash('your image is not modified properly', 'warning')
        else:
            filename = image.filename
            file_secure = secure_filename(filename)
            if not allow_extension(file_secure):
                flash('this extension for image file is not allowed', 'warning')
                return redirect(url_for('blog.post_create', form=form))
            folder = os.path.join(app.config['UPLOAD_DIR'], 'blog', f'{jdatetime.date.today()}')
            try:
                os.makedirs(folder)
            except:
                pass
            file = os.path.join(folder, file_secure)
            image.save(file)
            post.image = f'uploads/blog/{jdatetime.date.today()}/{filename}'
        try:
            db.session.add(post)
            db.session.commit()
            flash(f'the Post {post.title} is modified successfully', 'success')
            return redirect(url_for('blog.posts'))
        except IntegrityError():
            db.session.rollback()
            flash(IntegrityError, 'error')
            return redirect(url_for('blog.post_edit', form=form, post=post))
        
    return render_template('/blog/post_edit.html', form=form, post=post)



@blog.route('post-detail/<int:post_id>', methods=['POST', 'GET'])
@login_required
def post_detail(post_id):
    comment_form = CommentForm()
    post = Post.query.filter_by(id=post_id).first()
    post.views += 1
    db.session.add(post)
    db.session.commit()
    # comments = Comment.query.filter_by(post_id=post_id).all()
    comments = post.comments

    return render_template('/blog/post-detail.html', post=post, comments=comments, comment_form=comment_form)



@blog.route('post-writer/<int:user_id>', methods=['POST', 'GET'])
@login_required
def post_writer(user_id):
    post_user = Post.query.filter_by(user_id=user_id).all()
    # user = post_user[0].getWriter(user_id)
    user = User.query.filter_by(id=user_id).first()
    comment_form = CommentForm()

    return render_template('/blog/post-writer.html', post_user=post_user, user=user, comment_form=comment_form)



@blog.route('post-delete/<int:post_id>', methods=['GET'])
@login_required
def post_delete(post_id):
    Post.query.filter_by(id=post_id).delete()
    db.session.commit()

    return redirect(url_for('blog.posts'))




@blog.route('comment-send/<int:post_id>', methods=['POST', 'GET'])
@login_required
def comment_send(post_id):
    comment_form = CommentForm()

    comment = Comment()
    comment.body = request.form.get('body')
    comment.post_id = post_id
    comment.user_id = current_user.id

    try:
        db.session.add(comment)
        db.session.commit()
        flash('your comment is sent successfully', 'success')
        return redirect(url_for('blog.post_detail', post_id=post_id, comment_form=comment_form))
    except IntegrityError:
        db.session.rollback()
        flash(IntegrityError, 'danger')
        flash('your comment not sent properly', 'warning')
        return redirect(url_for('blog.post_detail', post_id=post_id, comment_form=comment_form))



@blog.route('reply-comment/<int:post_id>/<int:comment_id>', methods=['POST'])
@login_required
def reply_comment(post_id, comment_id):
    new_reply = Reply()
    new_reply.body = request.form.get('reply')
    new_reply.comment_id = comment_id
    new_reply.user_id = current_user.id
    db.session.add(new_reply)
    db.session.commit()
    return redirect(url_for('blog.post_detail', post_id=post_id))



@blog.route('post-like/<int:post_id>/<int:user_id>', methods=['POST', 'GET'])
@login_required
def post_like(post_id, user_id):
    user_liked = PostLikes.query.filter_by(user_id=user_id, post_id=post_id).first()
    # dislike
    if user_liked: 
        PostLikes.query.filter_by(post_id=post_id, user_id=user_id).delete()
        db.session.commit()
        return redirect(url_for('blog.post_detail', post_id=post_id))

    post_like = PostLikes()
    post_like.user_id = user_id
    post_like.post_id = post_id
    # post = Post.query.get_or_404(post_id)
    # user = User.query.get_or_404(user_id)
    try:
        db.session.add(post_like)
        db.session.commit()
        # flash(f'you {user.name} likes post {post.title}.', 'info')
        return redirect(url_for('blog.post_detail', post_id=post_id))
    except IntegrityError:
        db.session.rollback()
        # flash(f'your like not saved properly', 'warning')
        return redirect(url_for('blog.post_detail', post_id=post_id))




# ajax request
@blog.route('ajax-post', methods=['POST', 'GET'])
@login_required
def ajax_post():
    flash('you are clicked the ajax button', 'warning')
    return json.dumps({'status':'OK'});