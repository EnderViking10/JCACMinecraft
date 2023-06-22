from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField, StringField
from wtforms.validators import DataRequired, ValidationError

from models import User


class PortalForm(FlaskForm):
    username = StringField('Make Admin:', validators=[DataRequired()])
    submit = SubmitField('Submit')

    def __init__(self, *args, **kwargs):
        super(PortalForm, self).__init__(*args, **kwargs)

    def validate_username(self, username):
        user = User.query.filter_by(username=self.username.data).first()
        if user is None:
            raise ValidationError('That user does not exist')


class ExecuteForm(FlaskForm):
    body = TextAreaField('Enter some Code', validators=[DataRequired()])
    submit = SubmitField('Execute')
