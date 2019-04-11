from flask_wtf import FlaskForm
from wtforms import TextField, DecimalField, SelectField, IntegerField, BooleanField, SubmitField
from wtforms.validators import DataRequired


class CargoBlockForm(FlaskForm):
    mass = DecimalField('Mass of cargo block')
    blocksize = SelectField('Size of cargo block', choices=[('0.5', '0.5'), ('1', '1'), ('2', '2')])


class RemoveCargoBlockForm(FlaskForm):
    block_name = TextField('Remove cargo block by name', validators=[DataRequired()])


class ChangeParamsForm(FlaskForm):
    fuselage_length = IntegerField('Change fuselage length')
    max_load = DecimalField('Change maximum load')
    

class SelectSampleBlocks(FlaskForm):
    sample_blocks = SelectField('Blocks', choices=[('sample', 'Load sample blocks and fuselage parameters'),
                                                          ('simple', 'Load simple test blocks and fuselage parameters'),
                                                          ('harder', 'Load harder test blocks and fuselage parameters')])

class QuboParametersForm(FlaskForm):
    penalty = DecimalField('Change penalty for QUBO')