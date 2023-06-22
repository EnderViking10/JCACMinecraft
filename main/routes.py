from flask import render_template, flash, url_for, redirect, request, \
    current_app
from flask_login import login_required, current_user
from sqlalchemy import func

from app import db
from main import bp
from main.forms import PostForm, EmptyForm
from models import Post, User


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        # Create the post
        post = Post()
        post.body = form.body.data
        post.user_id = current_user.id

        # Save post to database
        db.session.add(post)
        db.session.commit()

        flash('Your post is now live!')
        return redirect(url_for('main.index'))

    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(
        page=page, per_page=current_app.config['POSTS_PER_PAGE'],
        error_out=False)

    next_url = url_for('main.index', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.index', page=posts.prev_num) \
        if posts.has_prev else None

    return render_template('index.html', title='home', form=form,
                           posts=posts.items, next_url=next_url,
                           prev_url=prev_url)


@bp.route('/user/<username>', methods=['GET', 'POST'])
@login_required
def user(username):
    form = EmptyForm()
    _user = User.query.filter(
        func.lower(username) == func.loweR(User.username)).first_or_404()

    page = request.args.get('page', 1, type=int)
    posts = _user.posts.order_by(Post.timestamp.desc()).paginate(
        page=page, per_page=current_app.config['POSTS_PER_PAGE'],
        error_out=False)

    next_url = url_for('main.user', username=current_user.username,
                       page=posts.next_num) if posts.has_next else None
    prev_url = url_for('main.user', username=current_user.username,
                       page=posts.prev_num) if posts.has_prev else None

    return render_template('user.html', user=_user, form=form, posts=posts,
                           next_url=next_url, prev_url=prev_url)


@bp.route('/explore')
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page=page, per_page=current_app.config['POSTS_PER_PAGE'],
        error_out=False)

    next_url = url_for('main.explore', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.explore', page=posts.prev_num) \
        if posts.has_prev else None

    return render_template('index.html', title='Explore',
                           posts=posts.items, next_url=next_url,
                           prev_url=prev_url)


@bp.route('/follow/<username>', methods=['POST'])
def follow(username):
    form = EmptyForm()

    if form.validate_on_submit():
        _user = User.query.filter_by(username=username).first()
        if _user is None:
            flash(f'User {username} not found.')
            return redirect(url_for('main.index'))
        if _user == current_user:
            flash('You cannot follow yourself!')
            return redirect(url_for('main.user', username=username))
        current_user.follow(_user)
        db.session.commit()
        flash(f'You are following {username}!')
        return redirect(url_for('main.user', username=username))
    else:
        return redirect(url_for('main.index'))


@bp.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        _user = User.query.filter_by(username=username).first()
        if _user is None:
            flash(f'User {username} not found.')
            return redirect(url_for('main.index'))
        if _user == current_user:
            flash('You cannot unfollow yourself!')
            return redirect(url_for('main.user', username=username))
        current_user.unfollow(_user)
        db.session.commit()
        flash(f'You are not following {username}.')
        return redirect(url_for('main.user', username=username))
    else:
        return redirect(url_for('main.index'))
