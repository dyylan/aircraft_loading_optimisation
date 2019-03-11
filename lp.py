import pulp


def cargo_loading(blocks, params, solver='default'):
    a = pulp.LpVariable.dicts(name='cargo',
                              indexs=blocks.to_dict().keys(),
                              lowBound=0,
                              upBound=1,
                              cat=pulp.LpInteger)
    lp_problem = pulp.LpProblem('Cargo loading', pulp.LpMaximize)
    # Objective function added first
    lp_problem += sum([block.mass*a[block.short_name] for block in blocks.blocks]), "Total mass of cargo"
    # Constraints added next
    lp_problem += sum([block.mass*a[block.short_name] for block in blocks.blocks]) <= params['max_load'], "Total mass of cargo cannot exceed a maximum load"
    lp_problem += sum([block.size*a[block.short_name] for block in blocks.blocks]) <= params['fuselage_length'], "Total size of cargo cannot exceed fuselage length"
    lp_problem.writeLP("CargoLoad.lp")

    if solver.lower() == 'glpk':
        lp_problem.solve(pulp.GLPK_CMD(msg=1))
    elif solver.lower() == 'coin':
        lp_problem.solve(pulp.COIN_CMD(timeLimit=60))
    else: 
        lp_problem.solve(pulp.PULP_CBC_CMD(maxSeconds=60, msg=1, fracGap=0))
    
    lp_prob_response = [{'status'         : pulp.LpStatus[lp_problem.status],
                        'cargo_mass'      : pulp.value(lp_problem.objective),
                        'fuselage_length' : params['fuselage_length'],
                        'max_load'        : params['max_load']}]
    variables_result = {f'{variable.name}': variable.varValue for variable in lp_problem.variables()}
    lp_prob_response.append(variables_result)
    return lp_prob_response


def cargo_ordering(blocks, params, solver='default'):
    get_name = lambda cargo_string : cargo_string.rpartition('_')[0]
    get_position = lambda cargo_string : cargo_string.rpartition('_')[2] 

    fuselage_length = int(params['fuselage_length'])
    b = pulp.LpVariable.dicts(name='cargo',
                              indexs=(blocks.to_dict().keys(),range(fuselage_length)),
                              lowBound=0,
                              upBound=1,
                              cat=pulp.LpInteger)
    lp_problem = pulp.LpProblem('Cargo ordering', pulp.LpMinimize)
    # Objective function added first
    lp_problem += pulp.lpSum([b[block.short_name][j]*block.mass*(j-((fuselage_length-1)/2))*(1-((1/3)*(block.size-(1/2))*(block.size-1))) for block in blocks.blocks for j in range(fuselage_length)]), "Total torque around centre of fuselage"
    # Constraints added next
    lp_problem += pulp.lpSum([b[block.short_name][j]*block.mass*(j-((fuselage_length-1)/2))*(1-((1/3)*(block.size-(1/2))*(block.size-1))) for block in blocks.blocks for j in range(fuselage_length)]) >= 0, "Torque must be greater than or equal to 0"
    for j in range(fuselage_length):
        lp_problem += pulp.lpSum([b[block.short_name][j]*(block.size-((2/3)*(block.size-(1/2))*(block.size-1))) for block in blocks.blocks]) <= 1, f"Position {j} can only have one block, two half blocks or no blocks"
    for block in blocks.blocks:
        lp_problem += pulp.lpSum([b[block.short_name][j] for j in range(fuselage_length)]) == block.size+((2/3)*((1-block.size)*(2-block.size))), f"Each block {block.short_name} is in exactly one place"
    for block in blocks.blocks:
        if block.size == 2:
            lp_problem += pulp.lpSum([b[block.short_name][j]*((-1)**j)*j*(2/3)*(block.size-(1/2))*(block.size-1) for j in range(fuselage_length)]) <= 1, f"Difference in block {block.short_name} locations is less than or equal to 1"
            lp_problem += pulp.lpSum([b[block.short_name][j]*((-1)**j)*j*(2/3)*(block.size-(1/2))*(block.size-1) for j in range(fuselage_length)]) >= -1, f"Difference in block {block.short_name} locations is greater than or equal to -1"
    lp_problem.writeLP("CargoOrder.lp") 

    if solver.lower() == 'glpk':
        lp_problem.solve(pulp.GLPK_CMD(msg=1))
    elif solver.lower() == 'coin':
        lp_problem.solve(pulp.COIN_CMD(timeLimit=60))
    else: 
        lp_problem.solve(pulp.PULP_CBC_CMD(maxSeconds=60, msg=1, fracGap=0))

    variables_result = {f'{variable.name}': variable.varValue for variable in lp_problem.variables()}
    # using 'reversed' should ensure that we get the minimum position for each block
    cargo_positions = {f'{get_name(variable.name)}': int(get_position(variable.name)) for variable in reversed(lp_problem.variables()) if variable.varValue} 
    lp_prob_response = [{'status'          : pulp.LpStatus[lp_problem.status],
                         'turning_effect'  : pulp.value(lp_problem.objective),
                         'fuselage_length' : params['fuselage_length'],
                         'max_load'        : params['max_load']}]
    lp_prob_response.append(cargo_positions)
    lp_prob_response.append(variables_result)
    return lp_prob_response