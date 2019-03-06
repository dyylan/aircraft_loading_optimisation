from flask_wtf import FlaskForm
from wtforms import TextField, DecimalField, SelectField, IntegerField, SubmitField
from wtforms.validators import DataRequired


class CargoBlockForm(FlaskForm):
    mass = DecimalField('Mass of cargo block', validators=[DataRequired()])
    blocksize = SelectField('Size of cargo block', choices=[('0.5', '0.5'), ('1', '1'), ('2', '2')])
    submit = SubmitField('Submit')


class RemoveCargoBlockForm(FlaskForm):
    block_name = TextField('Remove cargo block by name', validators=[DataRequired()])
    submit = SubmitField('Submit')


class ChangeParamsForm(FlaskForm):
    fuselage_length = IntegerField('Change fuselage length', validators=[DataRequired()])
    max_load = DecimalField('Change maximum load', validators=[DataRequired()])
    submit = SubmitField('Submit')