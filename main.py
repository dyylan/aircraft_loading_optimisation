import os
from flask import Flask, render_template, jsonify, request, session
from app.blocks import Block, BlockList
from app.forms import CargoBlockForm, RemoveCargoBlockForm, ChangeParamsForm, UseSampleBlocks
from app.lp import cargo_loading, cargo_ordering


app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

solver = os.getenv('SOLVER')

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


@app.route('/', methods=['GET'])
def index():
    samples_form = UseSampleBlocks()
    cargo_form = CargoBlockForm()    
    remove_form = RemoveCargoBlockForm()
    params_form = ChangeParamsForm()
    if 'step_one' not in session: 
        session['step_one'] = BlockList([]).to_json()
    if 'params' not in session:
        session['fuselage_length'] = 20
        session['max_load'] = 40000
    if 'messages' not in session:
        session['messages'] = []
    session.modified = True
    return render_template('index.html', samples_form=samples_form, cargo_form=cargo_form, remove_form=remove_form, params_form=params_form)


@app.route('/messages', methods=['GET'])
def messages_reset():
    if 'messages' not in session:
        session['messages'] = []
    return jsonify(session['messages'])


@app.route('/messages-reset', methods=['GET'])
def messages():
    session['messages'] = []
    return jsonify({'messages_reset': 1})


@app.route('/step-one/blocks', methods=['GET'])
def step_one_blocks():
    if 'step_one' not in session: 
        session['step_one'] = BlockList([]).to_json()
    return jsonify(session['step_one'])


@app.route('/step-two/blocks', methods=['GET'])
def step_two_blocks():
    if 'step_two' not in session: 
        session['step_two'] = BlockList([]).to_json()
    return jsonify(session['step_two'])


@app.route('/forms/samples', methods=['GET', 'POST'])
def samples_form():
    form = UseSampleBlocks()
    sample = form.sample_blocks.data
    simple = form.simple_test_blocks.data
    harder = form.harder_test_blocks.data
    if form.validate_on_submit():        
        if not sample and not simple and not harder:
            return jsonify({'samples_form_update': 0})
        if sample:
            session['step_one'] = BlockList(sample_blocks).to_json()
            session['fuselage_length'] = 20
            session['max_load'] = 40000
            session['messages'].extend([f'Sample problem blocks loaded',
                                        f'Changed fuselage length to {session["fuselage_length"]}',
                                        f'Changed max load to {session["max_load"]}'])
        if simple:
            session['step_one'] = BlockList(simple_test_blocks).to_json()
            session['fuselage_length'] = 3
            session['max_load'] = 2000
            session['messages'].extend([f'Test blocks loaded',
                                        f'Changed fuselage length to {session["fuselage_length"]}',
                                        f'Changed max load to {session["max_load"]}'])
        if harder:
            session['step_one'] = BlockList(harder_test_blocks).to_json()
            session['fuselage_length'] = 8
            session['max_load'] = 7000
            session['messages'].extend([f'Test blocks loaded',
                                        f'Changed fuselage length to {session["fuselage_length"]}',
                                        f'Changed max load to {session["max_load"]}'])
        session.modified = True
        return jsonify({'samples_form_update': 1})
    return jsonify({'samples_form_update': 0})


@app.route('/forms/add-cargo', methods=['GET', 'POST'])
def add_cargo_form():
    form = CargoBlockForm()
    if form.validate_on_submit():
        block = (float(form.blocksize.data),float(form.mass.data))
        blocks = BlockList(session['step_one'], as_json=True)
        blocks.add_block(block) 
        session['step_one'] = blocks.to_json()
        session['messages'].append(f'Cargo block added with mass {form.mass.data}kg and size {form.blocksize.data}')
        session.modified = True
        return jsonify({'add_cargo_form_update': 1})
    return jsonify({'add_cargo_form_update': 0})


@app.route('/forms/remove-cargo', methods=['GET', 'POST'])
def remove_cargo_form():
    form = RemoveCargoBlockForm()
    blocks = BlockList(session['step_one'], as_json=True)
    if form.validate_on_submit():
        removal = blocks.remove_block(str(form.block_name.data))
        if removal:
            session['messages'].append(f'Removed cargo block {str(form.block_name.data)} and relabelled remaining cargo blocks')
        else:
            session['messages'].append(f'Cargo block {str(form.block_name.data)} not found')
        session['step_one'] = blocks.to_json()
        session.modified = True
        return jsonify({'remove_cargo_form_update': 1})
    return jsonify({'remove_cargo_form_update': 0})


@app.route('/forms/params', methods=['GET', 'POST'])
def params_form():
    form = ChangeParamsForm()
    if form.validate_on_submit():
        if float(form.fuselage_length.data) > 0:
            session['fuselage_length'] = float(form.fuselage_length.data)        
            session['messages'].append(f'Changed fuselage length to {form.fuselage_length.data}')
        if float(form.max_load.data) > 0:
            session['max_load'] = float(form.max_load.data)
            session['messages'].append(f'Changed max load to {form.max_load.data}')
        session.modified = True
        return jsonify({'params_form_update': 1})
    return jsonify({'params_form_update': 0})


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




