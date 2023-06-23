import os
from functools import wraps

from flask import render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy import func

from admin import bp
from admin.forms import ExecuteForm
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


@bp.route('/make_admin/<username>', methods=['GET', 'POST'])
def make_admin(username):
    user = User.query.filter(func.lower(username) ==
                             func.loweR(User.username)).first()

    if user is None:
        flash(f'{username} does not exist')
        return redirect(url_for('main.user', username=username))
    user.admin = True
    db.session.commit()

    flash(f'{user.username} is now an admin')
    return redirect(url_for('main.user', username=username))


@bp.route('/remove_admin/<username>', methods=['GET', 'POST'])
def remove_admin(username):
    user = User.query.filter(func.lower(username) ==
                             func.loweR(User.username)).first()

    if user is None:
        flash(f'{username} does not exist')
        return redirect(url_for('main.user', username=username))
    user.admin = False
    db.session.commit()

    flash(f'{user.username} is no longer an admin')
    return redirect(url_for('main.user', username=username))


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
