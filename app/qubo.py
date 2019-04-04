import numpy as np
import neal
from dwave_qbsolv import QBSolv


class CargoQubo:
    """QUBO class to generate and solve a qubo problem from specific cargo blocks."""
    scaling = 1

    def __init__(self, params, from_json=False):
        if from_json:
            self.from_json(params)
        else:
            self.blocks = params['block_list'].to_json()
            self.max_load = params['max_load']*self.scaling
            self.fuselage_length = params['fuselage_length']*self.scaling
            self.penalty = params['penalty']*self.scaling
            self.vars = {block['long_name']: f'x{i+1}' for i, block in enumerate(self.blocks)}
            self.slacks = {}
            self.masses = [(self.vars[block['long_name']], block['mass']*self.scaling) for block in self.blocks]
            self.sizes = [(self.vars[block['long_name']], block['size']*self.scaling) for block in self.blocks]
            self._generate_slack_vars('mass', self.max_load)
            self._generate_slack_vars('size', self.fuselage_length)
            self.a = self._a_matrix()
            self.q = self._q_matrix()
            self._qubo()
            self.samples = []
            self.solution = {}
            self.solution_block_dict = {}
            self.solution_blocks = []

    def from_json(self, params):
        self.max_load = params['max_load']  
        self.fuselage_length = params['fuselage_length']
        self.vars = params['vars']
        self.slacks = params['slack_vars']
        self.masses = params['masses']
        self.sizes = params['sizes']
        self.a = params['A_matrix']
        self.q = params['Q_matrix']
        self.q_dict_json = params['q']
        self.q_dict = self._from_jsonable(self.q_dict_json)
        self.h = params['h']
        self.j_json = params['J']
        self.j = self._from_jsonable(self.j_json)
        self.samples = params['samples']
        self.solution = params['solution']
        self.solution_block_dict = params['solution_cargo']
        self.solution_blocks = params['solution_blocks']

    def to_json(self):
        json = {
            'blocks'            : self.blocks,
            'max_load'          : self.max_load,
            'fuselage_length'   : self.fuselage_length,
            'vars'              : self.vars,
            'slack_vars'        : self.slacks,
            'masses'            : self.masses,
            'sizes'             : self.sizes,
            'A_matrix'          : self.a,
            'Q_matrix'          : self.q,
            'q'                 : self.q_dict_json,
            'h'                 : self.h,
            'J'                 : self.j_json,
            'samples'           : self.samples,
            'solution'          : self.solution,
            'solution_cargo'    : self.solution_block_dict,
            'solution_blocks'   : self.solution_blocks
            } 
        return json
    
    def solution_json(self):
        solution = [
            {
                'cargo_mass'            : sum([block['mass'] for block in self.solution_blocks]),
                'fuselage_length'       : self.fuselage_length / self.scaling,
                'max_load'              : self.max_load / self.scaling,
                'samples'               : len(self.samples)
            },
            self.solution_block_dict,
            self.solution_blocks
        ]
        return solution   

    def solver(self, ising=True):
        sampler = neal.SimulatedAnnealingSampler()
        if ising:
            response = QBSolv().sample_ising(self.h, self.j) 
        else:
            response = QBSolv().sample_qubo(self.q_dict, solver=sampler)
        min_energy = 0
        for sample in response.data(['sample', 'energy']):
            sample_dict = {'sample' : {k: int((1+sample[0][k])/2) for k in sample[0]}}
            sample_dict.update({'energy' : sample[1]})            
            self.samples.append(sample_dict)
            min_energy = min(sample[1], min_energy)
            print(sample)
            self.solution = {f'x{k+1}':v for k,v in sample_dict['sample'].items() if k<len(self.masses)} if min_energy == sample[1] else self.solution 
        self._solution_blocks()
        return response
    
    @property
    def num_vars(self):
        return len(self.vars)

    @staticmethod
    def num_slack_vars(x):
        return int(np.log2(x))  
        
    def _generate_slack_vars(self, name, max_value):
        slacks = {f'slack_{name}{i+1}': f'x{self.num_vars+1+i}' for i in range(self.num_slack_vars(max_value))}    
        self.vars.update(slacks)
        self.slacks.update({name: [(self.vars[f'slack_{name}{i+1}'], 2**i) for i in range(len(slacks))]})
        
    def _a_matrix(self):
        row_one = [mass[1] for mass in self.masses]
        row_two = [size[1] for size in self.sizes]
        row_one.extend([smass[1] for smass in self.slacks['mass']])
        row_one.extend([0 for _ in self.slacks['size']])
        row_two.extend([0 for _ in self.slacks['mass']])
        row_two.extend([ssize[1] for ssize in self.slacks['size']])
        a = np.array([row_one, row_two])
        return a.tolist()

    def _q_matrix(self):
        a_T = np.array(self.a).transpose()
        q_W_L_diag = np.matmul(a_T, np.array([[self.max_load],[self.fuselage_length]])) 
        q_W_L_diag = np.diag(q_W_L_diag.transpose()[0])
        q_asym = np.matmul(a_T, self.a)
        np.fill_diagonal(q_asym, 0)
        q_sym = np.add(q_asym, np.add(q_asym.transpose(), q_W_L_diag))
        q_sym = self.penalty * q_sym
        masses = [mass[1] for mass in self.masses]
        for i, mass in enumerate(masses):
            q_sym[i][i] = q_sym[i][i] - mass
        return q_sym.tolist()

    def _qubo(self):
        self.q_dict = {(i, j): self.q[i][j] for i in range(len(self.q)) for j in range(len(self.q[0])) if j>=i}
        self.q_dict_json = self._to_jsonable(self.q_dict)
        self.h = np.array(self.q).diagonal().tolist()
        self.j = {(i, j): self.q[i][j] for i in range(len(self.q)) for j in range(len(self.q[0])) if j>i}
        #h = np.array(self.q).diagonal().tolist()
        #self.h = [(h_i/2) + (sum([q_j for j, q_j in enumerate(self.q[i]) if j>i]) / 4) for i, h_i in enumerate(h)]
        #self.j = {(i, j): self.q[i][j]/4 for i in range(len(self.q)) for j in range(len(self.q[0])) if j>i}
        self.j_json = self._to_jsonable(self.j)

    def _solution_blocks(self):
        self.solution_block_dict = {block_name : self.solution[var] for block_name, var in self.vars.items() if var in self.solution.keys()}
        sol_blocks = [k for k,v in self.solution_block_dict.items() if v]
        self.solution_blocks = [block for block in self.blocks if block['long_name'] in sol_blocks]
    
    @staticmethod
    def _to_jsonable(tuple_dict):
        return {str(k) : v for k, v in tuple_dict.items()}

    @staticmethod
    def _from_jsonable(str_dict):
        tuple_dict = {tuple([int(i) for i in k[1:-1].split(',')]) : v for k, v in str_dict.items()}