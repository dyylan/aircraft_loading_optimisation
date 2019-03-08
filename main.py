import os
from flask import Flask, render_template, jsonify, request, flash
from blocks import Block, BlockList
from forms import CargoBlockForm, RemoveCargoBlockForm, ChangeParamsForm, UseSampleBlocks
from lp import cargo_loading, cargo_ordering


app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

params = {'fuselage_length'  : 20,
          'max_load'         : 40000}

sample_blocks = [(1.0, 2134), (1.0, 3455), (1.0, 1866), (1.0, 1699), (1.0, 3500), 
                 (1.0, 3332), (1.0, 2578), (1.0, 2315), (1.0, 1888), (1.0, 1786),
                 (1.0, 3277), (1.0, 2987), (1.0, 2534), (1.0, 2111), (1.0, 2607),
                 (1.0, 1566), (1.0, 1765), (1.0, 1946), (1.0, 1732), (1.0, 1641), 
                 (0.5, 1800), (0.5, 986),  (0.5, 873),  (0.5, 1764), (0.5, 1239),
                 (0.5, 1487), (0.5, 769),  (0.5, 836),  (0.5, 659),  (0.5, 765)]

simple_test_blocks = [(1.0, 500), (1.0, 600), (1.0, 400), (0.5, 500), (0.5, 500)]

harder_test_blocks = [(1.0, 500), (1.0, 600), (1.0, 400), (0.5, 500), (0.5, 500),
                      (1.0, 500), (1.0, 600), (1.0, 400), (0.5, 300), (0.5, 200),
                      (1.0, 500), (1.0, 600), (1.0, 400), (0.5, 400), (0.5, 100)]

blocks = {'step_one' : BlockList([])}


@app.route('/', methods=['GET','POST'])
def index():
    form = CargoBlockForm()
    remove_form = RemoveCargoBlockForm()
    params_form = ChangeParamsForm()
    sample_form = UseSampleBlocks()
    if form.errors:
        flash("Cargo block was not added.")
    if form.validate_on_submit():
        block = (float(form.blocksize.data),float(form.mass.data))
        blocks['step_one'].add_block(block) 
        flash(f'Cargo block added with mass {form.mass.data}kg and size {form.blocksize.data}')
    if remove_form.validate_on_submit():
        removal = blocks['step_one'].remove_block(str(remove_form.block_name.data))
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
    if sample_form.validate_on_submit():
        if sample_form.sample_blocks.data:
            blocks['step_one'] = BlockList(sample_blocks)
            params['fuselage_length'] = 20
            params['max_load'] = 40000
            flash(f'Sample problem blocks loaded')
            flash(f'Changed fuselage length to {params["fuselage_length"]}')
            flash(f'Changed max load to {params["max_load"]}')
        if sample_form.simple_test_blocks.data:
            blocks['step_one'] = BlockList(simple_test_blocks)
            params['fuselage_length'] = 3
            params['max_load'] = 2000
            flash(f'Test blocks loaded')
            flash(f'Changed fuselage length to {params["fuselage_length"]}')
            flash(f'Changed max load to {params["max_load"]}')
        if sample_form.harder_test_blocks.data:
            blocks['step_one'] = BlockList(harder_test_blocks)
            params['fuselage_length'] = 7
            params['max_load'] = 5000
            flash(f'Test blocks loaded')
            flash(f'Changed fuselage length to {params["fuselage_length"]}')
            flash(f'Changed max load to {params["max_load"]}')
    return render_template('index.html', form=form, remove_form=remove_form, params_form=params_form, sample_form=sample_form)


@app.route('/step-one/blocks', methods=['GET'])
def step_one_blocks():
    return jsonify(blocks['step_one'].to_json())


@app.route('/step-one/optimisation', methods=['GET'])
def step_one_optimisation():
    lp_prob_response = cargo_loading(blocks['step_one'], params)
    solution_filter = [k for k, v in lp_prob_response[1].items() if v == 1]
    cargo_boxes_result = blocks['step_one'].filter_to_json(solution_filter)
    blocks['step_two'] = BlockList(blocks['step_one'].filtered_block_list(solution_filter), 'b')
    lp_prob_response.append(cargo_boxes_result)
    return jsonify(lp_prob_response)


@app.route('/step-two/blocks', methods=['GET'])
def step_two_blocks():
    return jsonify(blocks['step_two'].to_json())


@app.route('/step-two/optimisation', methods=['GET'])
def step_two_optimisation():
    lp_prob_response = cargo_ordering(blocks['step_two'], params)
    blocks['step_two'].add_positions(lp_prob_response[1])
    lp_prob_response.append(blocks['step_two'].to_json())    
    return jsonify(lp_prob_response)




