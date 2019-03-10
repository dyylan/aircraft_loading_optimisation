class Block:
    """Block class for each cargo block."""
    def __init__(self, size, mass, short_name, long_name, position=None):
        self.size = size
        self.mass = mass
        self.short_name = short_name
        self.long_name = long_name
        self.density = np.true_divide(mass, size)
        self.position = position

    def __lt__(self, other):
        if self.position:
            return self.position < other.position
        else: 
            return self.size > other.size

    def add_position(self, position):
        self.position = position
        return self

    def to_dict(self):
        dict_block = {'size'    : self.size,
                      'mass'    : self.mass} 
        return dict_block

    def to_json(self):
        json_block = {'size'       : self.size,
                      'mass'       : self.mass,
                      'density'    : self.density,
                      'short_name' : self.short_name,
                      'long_name'  : self.long_name,
                      'position'   : self.position}
        return json_block

        
class BlockList:
    """Block list class for the list of cargo blocks."""
    def __init__(self, block_list, as_json=False, name_prefix='a'):
        self.name_prefix = name_prefix
        if as_json:
            self.block_list_json = block_list
            self.block_list = [(block['size'], block['mass']) for block in self.block_list_json]
            print(self.block_list)
            self._generate_blocks_from_json()
        else: 
            self.block_list = block_list
            self._generate_blocks()

    def add_block(self, block):
        self.block_list.append(block)
        self._generate_blocks()

    def add_blocks(self, blocks):
        self.block_list.extend(blocks)
        self._generate_blocks()

    def add_positions(self, positions):
        self.positions = positions 
        self._generate_blocks(positions)

    def remove_block(self, block_name):
        remove_index = [i for (i, block) in enumerate(self.blocks) if (block.long_name in block_name) or (block.short_name in block_name)]
        if remove_index:
            self.block_list.pop(remove_index[0])
            self._generate_blocks()
            return remove_index[0]
        else:
            return False 

    def length(self):
        return len(self.block_list)

    def get_sizes(self):
        sizes = [block.size for block in self.blocks]
        return sizes
    
    def get_masses(self):
        masses = [block.mass for block in self.blocks]
        return masses

    def filter_to_json(self, filter_list):
        filtered_json_blocks = [block.to_json() for block in self.blocks if block.long_name in filter_list]
        return filtered_json_blocks

    def filtered_block_list(self, filter_list):
        filtered_block_list = [tuple(block.to_dict().values()) for block in self.blocks if block.long_name in filter_list]
        return filtered_block_list

    def to_dict(self, long_name=False):
        if long_name:
            dict_blocks = { block.long_name: block.to_dict() for block in self.blocks }
        else:
            dict_blocks = { block.short_name: block.to_dict() for block in self.blocks }
        return dict_blocks

    def to_json(self):
        json_blocks = [block.to_json() for block in self.blocks]
        return json_blocks              

    def _generate_blocks(self, positions=None):
        short_name = lambda i : f'{self.name_prefix}0{i+1}' if i<9 else f'{self.name_prefix}{i+1}'
        long_name = lambda i : f'cargo_{self.name_prefix}0{i+1}' if i<9 else f'cargo_{self.name_prefix}{i+1}'
        self.blocks = [Block(block[0], block[1], short_name(i), long_name(i)) for (i, block) in enumerate(self.block_list)] 
        if positions:
            self.blocks = [block.add_position(positions[block.long_name]) for block in self.blocks]
            self.blocks.sort()

    def _generate_blocks_from_json(self):
        self.blocks = [Block(block['size'], block['mass'], block['short_name'], block['long_name'], block['position']) for block in self.block_list_json]
        self.blocks.sort()
