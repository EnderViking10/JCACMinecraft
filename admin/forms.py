from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField, StringField
from wtforms.validators import DataRequired


class PortalForm(FlaskForm):
    username = StringField('Make Admin:', validators=[DataRequired()])
    submit = SubmitField('Submit')


class ExecuteForm(FlaskForm):
    body = TextAreaField('Enter some Code', validators=[DataRequired()])
    submit = SubmitField('Execute')


class EmptyForm(FlaskForm):
    submit = SubmitField('Submit')
