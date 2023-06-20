from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user, logout_user, login_user, login_required
from sqlalchemy import func
from werkzeug.urls import url_parse

from app import db
from auth import bp
from auth.forms import LoginForm, RegistrationForm, EditProfileForm
from models import User


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@bp.route('/login', methods=['GET', 'POST'])
def login():
    # If user is already logged in
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        # Attempt to find the user
        user = User.query.filter(func.lower(form.username.data) ==
                                 func.loweR(User.username)).first()

        # If the user doesn't exist or the password is wrong
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))

        # Log in the user then redirect them to either index or prev page
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)

    return render_template('login.html', form=form, title='Login')


@bp.route('/register', methods=['GET', 'POST'])
def register():
    # If user is already logged in
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        # Create the user
        user = User()
        user.username = form.username.data
        user.email = form.email.data
        user.set_password(form.password.data)

        # Add user to database
        db.session.add(user)
        db.session.commit()

        # Redirect to login page
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('auth.login'))
    return render_template('register.html', title='Register', form=form)


@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)

    if form.validate_on_submit():
        # Change data
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data

        # Save changes
        db.session.commit()

        # Redirect after
        flash('Your changes have been saved.')
        return redirect(url_for('main.user', username=current_user.username))
    # Fill the form with current data
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me

    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)
