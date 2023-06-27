from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField
from wtforms.validators import DataRequired


class ExecuteForm(FlaskForm):
    body = TextAreaField('Enter some Code', validators=[DataRequired()])
    submit = SubmitField('Execute')


class EmptyForm(FlaskForm):
    submit = SubmitField('Submit')
