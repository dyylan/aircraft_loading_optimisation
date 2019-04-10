import numpy as np
#import neal
from dwave_qbsolv import QBSolv
import dimod

class CargoQubo:
    """ QUBO class to generate and solve a qubo problem from specific cargo blocks."""
    scaling = 1

    def __init__(self, params):
        """ Initialise all the class varibles required to perform annealing from 
            input params dictionary which must contain the keys: 
                'block_list'        : a list of Block objects;
                'max_load'          : maximum cargo load;
                'fuselage_length'   : fuselage length;
                'penalty'           : penalty.
            """ 
        self.blocks = params['block_list'].to_json()
        self.max_load = params['max_load']
        self.fuselage_length = params['fuselage_length']
        self.penalty = params['penalty']
        self.vars = {block['long_name']: f'x{i+1}' for i, block in enumerate(self.blocks)}
        self.slacks = {}
        self.masses = [(self.vars[block['long_name']], block['mass']) for block in self.blocks]
        self.mass_norm = self.norm([mass[1] for mass in self.masses]) / self.scaling
        self.masses_norm = [mass[1]/self.mass_norm for mass in self.masses]  
        self.sizes = [(self.vars[block['long_name']], block['size']) for block in self.blocks]
        self.size_norm = self.norm([size[1] for size in self.sizes]) / self.scaling
        self.sizes_norm = [size[1]/self.size_norm for size in self.sizes]  
        self._generate_slack_vars('mass', self.max_load, self.mass_norm)
        self._generate_slack_vars('size', self.fuselage_length, self.size_norm)
        self.a = self.a_matrix()
        self.q = self.q_matrix()
        self.offset = 0
        self.qubo()
        self.samples = []
        self.solution = {}
        self.solution_block_dict = {}
        self.solution_blocks = []

    def to_json(self):
        """ Converts class attributes to JSON format for webapp."""
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
            'offset'            : self.offset,
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
                'cargo_length'          : sum([block['size'] for block in self.solution_blocks]),
                'fuselage_length'       : self.fuselage_length,
                'max_load'              : self.max_load,
                'samples'               : len(self.samples)
            },
            self.solution_block_dict,
            self.solution_blocks
        ]
        return solution 

    def a_matrix(self):
        """ Calculates the A matrix, which contains the constraints and the slack variables"""
        row_one = self.masses_norm
        row_two = self.sizes_norm 
        row_one.extend([smass[1] for smass in self.slacks['mass']])
        row_one.extend([0 for _ in self.slacks['size']])
        row_two.extend([0 for _ in self.slacks['mass']])
        row_two.extend([ssize[1] for ssize in self.slacks['size']])
        a = np.array([row_one, row_two])
        print(f'a = {a}')
        return a.tolist() 

    def q_matrix(self):
        """ Calculates the Q matrix using from -C+D (minimise a max objective so take negative).
            This is essentially the mapping of the linear program to QUBO, see 
            the description of the QUBO on the webapp page (templates/_qubo.hmtl)
            """
        
        # A matrix of constraints with slack variables 
        a_matrix = np.array(self.a)

        # Objective function matrix C, simply the masses of the blocks in the diagonal
        c_matrix = np.zeros((a_matrix.shape[1], a_matrix.shape[1]))
        for i, mass in enumerate(self.masses_norm):
            c_matrix[i][i] = mass

        # c vector of constraint limits 
        c_vector = np.array([[self.max_load/self.mass_norm],[self.fuselage_length/self.size_norm]])

        ctc = np.matmul(c_vector.transpose(), c_vector)
        self.offset = ctc

        # diagonal matrix from b^TA part
        diagonal_ctA = np.diag(np.matmul(c_vector.transpose(), a_matrix)[0])
        diagonal_Atc = np.diag(np.matmul(a_matrix.transpose(), c_vector).transpose()[0])

        # D matrix
        d_matrix = self.penalty * (np.matmul(a_matrix.transpose(), a_matrix) - diagonal_Atc - diagonal_Atc + ctc)
        
        # Q matrix 
        q_matrix = - c_matrix + d_matrix
        return q_matrix

    def qubo(self):
        self.q_dict = {(i, j): self.q[i][j] for i in range(len(self.q)) for j in range(len(self.q[0])) if j>=i}
        self.q_dict_json = self.to_jsonable(self.q_dict)
        self.h = np.array(self.q).diagonal().tolist()
        self.h_dict = {i: h_i for i, h_i in enumerate(self.h)}
        self.j = {(i, j): self.q[i][j] for i in range(len(self.q)) for j in range(len(self.q[0])) if j>i}
        #h = np.array(self.q).diagonal().tolist()
        #self.h = [(h_i/2) + (sum([q_j for j, q_j in enumerate(self.q[i]) if j>i]) / 4) for i, h_i in enumerate(h)]
        #self.j = {(i, j): self.q[i][j]/4 for i in range(len(self.q)) for j in range(len(self.q[0])) if j>i}
        self.j_json = self.to_jsonable(self.j)

    def dimod_solver(self):
        """ Uses dimod package from D-Wave to implement a binary quadratic model and
            then use a simulated annealer to sample from the model.
            """
        linear = self.h_dict
        print(linear)
        quadratic = self.j
        print(quadratic)
        #offset = self.offset
        offset = 0
        model = dimod.BinaryQuadraticModel(linear, quadratic, offset, dimod.Vartype.SPIN)
        response = dimod.SimulatedAnnealingSampler().sample(model)        
        #response = dimod.ExactSolver().sample(model)
        #print(response)
        min_energy = 0
        for sample in response.data(['sample', 'energy']):
            sample_dict = {'sample' : {k: int((1+sample[0][k])/2) for k in sample[0]}}
            sample_dict.update({'energy' : sample[1]})            
            self.samples.append(sample_dict)
            min_energy = min(sample[1], min_energy)        
            self.solution = {f'x{k+1}':v for k,v in sample_dict['sample'].items() if k<len(self.masses)} if min_energy == sample[1] else self.solution
            if min_energy == sample[1]:
                print(sample) 
        self._solution_blocks()

    def qbsolv_solver(self, ising=True):
        """ qbsolv is for breaking up large optmisation problems into smaller
            ones for the D-Wave machines. Is not properly implemented yet.
            """
        if ising:
            response = QBSolv().sample_ising(self.h, self.j) 
        else:
            response = QBSolv().sample_qubo(self.q_dict)
        min_energy = 0
        for sample in response.data(['sample', 'energy']):
            sample_dict = {'sample' : {k: int((1+sample[0][k])/2) for k in sample[0]}}
            sample_dict.update({'energy' : sample[1]})            
            self.samples.append(sample_dict)
            min_energy = min(sample[1], min_energy)
            self.solution = {f'x{k+1}':v for k,v in sample_dict['sample'].items() if k<len(self.masses)} if min_energy == sample[1] else self.solution 
        self._solution_blocks()
        return response
    
    @property
    def num_vars(self):
        return len(self.vars)

    @staticmethod
    def norm(x):
        return np.sqrt(sum([i**2 for i in x]))

    @staticmethod
    def num_slack_vars(x):
        return int(np.log2(x)-1)  
 
    @staticmethod
    def to_jsonable(tuple_dict):
        return {str(k) : v for k, v in tuple_dict.items()}

    @staticmethod
    def from_jsonable(str_dict):
        tuple_dict = {tuple([int(i) for i in k[1:-1].split(',')]) : v for k, v in str_dict.items()}

    def _generate_slack_vars(self, name, max_value, norm):
        slacks = {f'slack_{name}{i+1}': f'x{self.num_vars+1+i}' for i in range(self.num_slack_vars(max_value))}    
        self.vars.update(slacks)
        self.slacks.update({name: [(self.vars[f'slack_{name}{i+1}'], 2**i/norm) for i in range(len(slacks))]})

    def _solution_blocks(self):
        self.solution_block_dict = {block_name : self.solution[var] for block_name, var in self.vars.items() if var in self.solution.keys()}
        sol_blocks = [k for k,v in self.solution_block_dict.items() if v]
        self.solution_blocks = [block for block in self.blocks if block['long_name'] in sol_blocks]