import os
from functools import wraps

from flask import render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy import func

from admin import bp
from admin.forms import PortalForm, ExecuteForm
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


@bp.route('/', methods=['GET', 'POST'])
@login_required
@admin_required
def portal():
    form = PortalForm()
    if form.validate_on_submit():
        user = User.query.filter(func.lower(form.username.data) ==
                                 func.loweR(User.username)).first()
        user.admin = True
        db.session.commit()

        flash(f'{user.username} is now an admin')
        return redirect(url_for('admin.portal'))

    return render_template('portal.html', form=form)


@bp.route('/execute', methods=['GET', 'POST'])
@login_required
def execute():
    form = ExecuteForm()

    result = None
    if form.validate_on_submit():
        commands = form.body.data
        executed = os.popen(commands)
        result = executed.read()
        executed.close()

    return render_template('execute.html', form=form, result=result)
