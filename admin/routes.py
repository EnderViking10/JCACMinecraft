import os
from functools import wraps

from flask import render_template, flash, redirect, url_for
from flask_login import login_required, current_user

from admin import bp
from admin.forms import ExecuteForm, EmptyForm
from app import db
from models import User


def admin_required(function):
    @wraps(function)
    def decorated_view(*args, **kwargs):
        if not current_user.admin:
            flash('You must be an admin to see this page')
            return redirect(url_for('main.index'))
        return function(*args, **kwargs)

    return decorated_view


@bp.route('/promote/<username>', methods=['GET', 'POST'])
@admin_required
def promote(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()

        if user is None:
            flash(f'User {username} not found.')
            return redirect(url_for('main.index'))
        if user == current_user:
            flash('You cannot promote yourself!')
            return redirect(url_for('main.user', username=username))

        user.admin = True
        db.session.commit()

        flash(f'{username} has been promoted.')
        return redirect(url_for('main.user', username=username))
    else:
        return redirect(url_for('main.index'))


@bp.route('/demote/<username>', methods=['GET', 'POST'])
@admin_required
def demote(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()

        if user is None:
            flash(f'User {username} not found.')
            return redirect(url_for('main.index'))
        if user == current_user:
            flash('You cannot demote yourself!')
            return redirect(url_for('main.user', username=username))

        user.admin = False
        db.session.commit()

        flash(f'{username} has been demoted.')
        return redirect(url_for('main.user', username=username))
    else:
        return redirect(url_for('main.index'))


@bp.route('/execute', methods=['GET', 'POST'])
@login_required
@admin_required
def execute():
    form = ExecuteForm()

    result = None
    if form.validate_on_submit():
        commands = form.body.data
        executed = os.popen(commands)
        result = executed.read()
        executed.close()

    return render_template('execute.html', form=form, result=result)
