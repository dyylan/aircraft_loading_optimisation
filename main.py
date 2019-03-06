import os
from flask import Flask, render_template, jsonify, request, flash
from blocks import Block, BlockList
from forms import CargoBlockForm, RemoveCargoBlockForm, ChangeParamsForm
import pulp

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

params = {'fuselage_length'  : 20,
          'max_load'         : 40000,
          'blocks'           : [(1.0, 2134), 
                                (1.0, 3455),
                                (1.0, 1866), 
                                (1.0, 1699),
                                (1.0, 3500), 
                                (1.0, 3332),
                                (1.0, 2578), 
                                (1.0, 2315),
                                (1.0, 1888), 
                                (1.0, 1786),
                                (1.0, 3277), 
                                (1.0, 2987),
                                (1.0, 2534), 
                                (1.0, 2111),
                                (1.0, 2607),
                                (1.0, 1566), 
                                (1.0, 1765),
                                (1.0, 1946), 
                                (1.0, 1732),
                                (1.0, 1641), 
                                (0.5, 1800),
                                (0.5, 986), 
                                (0.5, 873),
                                (0.5, 1764), 
                                (0.5, 1239),
                                (0.5, 1487), 
                                (0.5, 769),
                                (0.5, 836), 
                                (0.5, 659),
                                (0.5, 765)]}

blocks = BlockList(params['blocks'])


@app.route('/', methods=['GET','POST'])
def index():
    form = CargoBlockForm()
    remove_form = RemoveCargoBlockForm()
    params_form = ChangeParamsForm()
    print(blocks.to_dict())
    if form.errors:
        flash("Cargo block was not added.")
    if form.validate_on_submit():
        block = (float(form.blocksize.data),float(form.mass.data))
        blocks.add_block(block) 
        flash(f'Cargo block added with mass {form.mass.data}kg and size {form.blocksize.data}')
    if remove_form.validate_on_submit():
        removal = blocks.remove_block(str(remove_form.block_name.data))
        print(removal)
        if removal:
            flash(f'Removed cargo block {str(remove_form.block_name.data)} and relabelled remaining cargo blocks')
        else:
            flash(f'Cargo block {str(remove_form.block_name.data)} not found')
    if params_form.validate_on_submit():
        params['fuselage_length'] = float(params_form.fuselage_length.data)            
        params['max_load'] = float(params_form.max_load.data)
        flash(f'Changed fuselage length to {params_form.fuselage_length.data}')
        flash(f'Changed max load to {params_form.max_load.data}')
    return render_template('index.html', form=form, remove_form=remove_form, params_form=params_form)


@app.route('/blocks', methods=['GET'])
def get_blocks():
    return jsonify(blocks.to_json())


@app.route('/optimisation', methods=['GET'])
def optimisation_calculation():
    x = pulp.LpVariable.dicts(name='cargo',
                              indexs=blocks.to_dict().keys(),
                              lowBound=0,
                              upBound=1,
                              cat=pulp.LpInteger)
    lp_problem = pulp.LpProblem('Cargo loading', pulp.LpMaximize)
    # Objective function added first
    lp_problem += sum([block.mass*x[block.short_name] for block in blocks.blocks]), "Total mass of cargo"
    # Constraints added next
    lp_problem += sum([block.mass*x[block.short_name] for block in blocks.blocks]) <= params['max_load'], "Total mass of cargo cannot exceed a maximum load"
    lp_problem += sum([block.size*x[block.short_name] for block in blocks.blocks]) <= params['fuselage_length'], "Total size of cargo cannot exceed fuselage length"
    lp_problem.writeLP("CargoLoad.lp")
    lp_problem.solve()
    lp_prob_response = [{'status'         : pulp.LpStatus[lp_problem.status],
                        'cargo_mass'      : pulp.value(lp_problem.objective),
                        'fuselage_length' : params['fuselage_length'],
                        'max_load'        : params['max_load']}]
    variables_result = {f'{variable.name}': variable.varValue for variable in lp_problem.variables()}
    solution_filter = [k for k, v in variables_result.items() if v == 1]
    cargo_boxes_result = blocks.filter_to_json(solution_filter)
    lp_prob_response.append(variables_result)
    lp_prob_response.append(cargo_boxes_result)
    return jsonify(lp_prob_response)

