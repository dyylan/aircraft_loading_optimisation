import os
from flask import Flask, render_template, jsonify, request, flash, session
from blocks import Block, BlockList
from forms import CargoBlockForm, RemoveCargoBlockForm, ChangeParamsForm, UseSampleBlocks
from lp import cargo_loading, cargo_ordering


app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

solver = 'glpk'

sample_blocks = [(1.0, 2134), (1.0, 3455), (1.0, 1866), (1.0, 1699), (1.0, 3500), 
                 (1.0, 3332), (1.0, 2578), (1.0, 2315), (1.0, 1888), (1.0, 1786),
                 (1.0, 3277), (1.0, 2987), (1.0, 2534), (1.0, 2111), (1.0, 2607),
                 (1.0, 1566), (1.0, 1765), (1.0, 1946), (1.0, 1732), (1.0, 1641), 
                 (0.5, 1800), (0.5, 986),  (0.5, 873),  (0.5, 1764), (0.5, 1239),
                 (0.5, 1487), (0.5, 769),  (0.5, 836),  (0.5, 659),  (0.5, 765)]

simple_test_blocks = [(1.0, 500), (1.0, 600), (1.0, 400), (0.5, 500), (0.5, 500)]

harder_test_blocks = [(1.0, 500), (1.0, 600), (1.0, 400), (0.5, 500), (0.5, 500),
                      (1.0, 500), (1.0, 600), (1.0, 400), (0.5, 300), (0.5, 200),
                      (1.0, 500), (1.0, 600), (1.0, 400), (0.5, 400), (0.5, 100),
                      (2.0, 900), (2.0, 800), (2.0, 1200), (2.0, 1000)]

@app.route('/', methods=['GET','POST'])
def index():
    form = CargoBlockForm()
    remove_form = RemoveCargoBlockForm()
    params_form = ChangeParamsForm()
    samples_form = UseSampleBlocks()
    if 'step_one' not in session: 
        session['step_one'] = BlockList([]).to_json()
    if 'params' not in session:
        session['fuselage_length'] = 20
        session['max_load'] = 40000
    if form.errors:
        flash("Cargo block was not added.")
    if form.validate_on_submit():
        block = (float(form.blocksize.data),float(form.mass.data))
        blocks = BlockList(session['step_one'], as_json=True)
        blocks.add_block(block) 
        session['step_one'] = blocks.to_json()
        flash(f'Cargo block added with mass {form.mass.data}kg and size {form.blocksize.data}')
    if remove_form.validate_on_submit():
        blocks = BlockList(session['step_one'], as_json=True)
        removal = blocks.remove_block(str(remove_form.block_name.data))
        if removal:
            flash(f'Removed cargo block {str(remove_form.block_name.data)} and relabelled remaining cargo blocks')
        else:
            flash(f'Cargo block {str(remove_form.block_name.data)} not found')
        session['step_one'] = blocks.to_json()
    if params_form.validate_on_submit():
        session['fuselage_length'] = float(params_form.fuselage_length.data)            
        session['max_load'] = float(params_form.max_load.data)
        flash(f'Changed fuselage length to {params_form.fuselage_length.data}')
        flash(f'Changed max load to {params_form.max_load.data}')
    if samples_form.validate_on_submit():
        if samples_form.sample_blocks.data:
            session['step_one'] = BlockList(sample_blocks).to_json()
            session['fuselage_length'] = 20
            session['max_load'] = 40000
            flash(f'Sample problem blocks loaded')
            flash(f'Changed fuselage length to {session["fuselage_length"]}')
            flash(f'Changed max load to {session["max_load"]}')
        if samples_form.simple_test_blocks.data:
            session['step_one'] = BlockList(simple_test_blocks).to_json()
            session['fuselage_length'] = 3
            session['max_load'] = 2000
            flash(f'Test blocks loaded')
            flash(f'Changed fuselage length to {session["fuselage_length"]}')
            flash(f'Changed max load to {session["max_load"]}')
        if samples_form.harder_test_blocks.data:
            session['step_one'] = BlockList(harder_test_blocks).to_json()
            session['fuselage_length'] = 8
            session['max_load'] = 7000
            flash(f'Test blocks loaded')
            flash(f'Changed fuselage length to {session["fuselage_length"]}')
            flash(f'Changed max load to {session["max_load"]}')
    session.modified = True
    return render_template('index.html', form=form, remove_form=remove_form, params_form=params_form, samples_form=samples_form)


@app.route('/step-one/blocks', methods=['GET'])
def step_one_blocks():
    if 'step_one' not in session: 
        session['step_one'] = BlockList([]).to_json()
    return jsonify(session['step_one'])


@app.route('/step-one/optimisation', methods=['GET'])
def step_one_optimisation():
    blocks = BlockList(session['step_one'], as_json=True)
    params = {'fuselage_length' : session['fuselage_length'],
              'max_load'        : session['max_load']}
    lp_prob_response = cargo_loading(blocks, params, solver)
    solution_filter = [k for k, v in lp_prob_response[1].items() if v == 1]
    cargo_boxes_result = BlockList(session['step_one'], as_json=True).filter_to_json(solution_filter)
    blocks_two = BlockList(cargo_boxes_result, as_json=True, name_prefix='b')
    session['step_two'] = blocks_two.to_json()
    lp_prob_response.append(cargo_boxes_result)
    return jsonify(lp_prob_response)


@app.route('/step-two/blocks', methods=['GET'])
def step_two_blocks():
    if 'step_two' not in session: 
        session['step_two'] = BlockList([]).to_json()
    return jsonify(session['step_two'])


@app.route('/step-two/optimisation', methods=['GET'])
def step_two_optimisation():
    blocks = BlockList(session['step_two'], as_json=True, name_prefix='b')
    params = {'fuselage_length' : session['fuselage_length'],
              'max_load'        : session['max_load']}
    lp_prob_response = cargo_ordering(blocks, params, solver)
    blocks.add_positions(lp_prob_response[1])
    session['step_two'] = blocks.to_json()
    lp_prob_response.append(session['step_two'])    
    return jsonify(lp_prob_response)




