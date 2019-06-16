import numpy as np
from numpy.random import randint
from enum import Enum

class Levels(Enum):
    Deep = 0
    Sea_level = 1
    Air = 2

class Vessel:
    """A Vessel class for some defaults of all Vessel sub-classes.\n
    Attributes: ind.\n
    Methods: rotate, under_fire.
    """
    
    def __init__(self, ind: int):
        self.ind = ind+1
        
    def __repr__(self):
        return f'{self.vname}{self.ind}'   
    
    def assert_vessel(self):
        pass
    
    def rotate(self):
        """Rotates the vessel"""
        self.vshape = np.rot90(self.vshape,3)

    def under_fire(self):
        """Default vessel behavior when targeted - KILL."""
        self.kill = True
        print('signal.KILL')
        return self.kill

class Submarine(Vessel):
    """A submarine class, includes the submarine shape, and name for repr.\n
    Attributes: ind, level, vshape, vname, kill.
    """
    
    def __init__(self, ind: int):
        super().__init__(ind)
        self.level = Levels.Deep.value
        self.vshape = np.array([[1,1,1]], dtype=bool)
        if bool(randint(2)):
            self.rotate()
        self.vname = 'submarine'

class Destroyer(Vessel):
    """A destroyer class, includes the destroyer shape, and name for repr.\n
    Attributes: ind, level, vshape, vname, kill.\n
    Methods: under_fire.
    """
    
    def __init__(self, ind: int):
        super().__init__(ind)
        self.level = Levels.Sea_level.value
        self.vshape = np.array([[1,1,1,1]], dtype=bool)
        if bool(randint(2)):
            self.rotate()
        self.vname = 'destroyer'
        self.hit = 0
        
    def under_fire(self):
        """Destroyer is destroyed (signal.KILL) only when fully hit (signal.HIT)."""
        self.hit +=1
        self.kill = False if self.hit < self.vshape.sum() else True
        print('signal.HIT' if not self.kill else 'signal.KILL')
        return self.kill

class Jet(Vessel):
    """A jet class, includes the jet shape, and name for repr.\n
    Attributes: ind, level, vshape, vname, kill.
    """
    
    def __init__(self, ind: int):
        super().__init__(ind)
        self.level = Levels.Air.value
        self.vshape = np.array ([[0,1,0],
                                [1,1,1],
                                [0,1,0],
                                [0,1,0]], dtype=bool)
        if bool(randint(2)):
            self.rotate()
        self.vname = 'jet'

class General(Vessel):
    """A general class, includes the general shape and name for repr.\n
    Attributes: ind, level, vshape, vname, kill.\n
    Methods: under_fire.
    """
    
    def __init__(self, ind: int):
        self.ind = ''
        self.level = randint(max([level.value for level in Levels])+1)
        self.vshape = np.array ([[1]], dtype=bool)
        self.vname = 'general'

    def under_fire(self):
        """The game ends (signal.END) when the general is hit."""
        self.kill = True
        print('signal.END')
        return self.kill
    
class Board:
    """A game board class which initiates and populates a board.\n
    The board default dimentions are 4x4x3-levels. To change, edit __init__(dim)\n
    The board is populated by default with a single vessel for each type. To change, edit availabe_vessels()\n
    Attributes: rows, columns, levels, vessels, board.\n
    Methods: available_vessels, populate_board, place_vessel.
    """
    
    def __init__(self, player_id: int = 0, dim: tuple = (4, 4, 3)):
        self.player_id = player_id
        self.rows, self.columns, self.levels = dim
        assert self.levels == 3, 'Board levels must be 3.'
        self.vessels = self.available_vessels(available_vessels)
        self.populate_board()
        
    def __str__(self):
        return (f"""{Levels(0).name}:\n{self.board[:,:,0]}
                    \n{Levels(1).name}:\n{self.board[:,:,1]}
                    \n{Levels(2).name}:\n{self.board[:,:,2]}""")
    
    def available_vessels(self, av_ves: dict = {Submarine: 1, Destroyer: 1, Jet: 1, General: 1}) -> dict:
        """Defines and asserts the type of vessels for a game. 
        Asserts only one general is defined. If there are too many vessels \
        for any other type, the func populate_board() would raise an exception.
        """
        for ves in av_ves:
            try:
                ves.assert_vessel
            except (NameError, AttributeError):
                raise Exception(f'{ves} is not a Vessel object.')
        assert av_ves[General] == 1, 'More than one general is most inadvisable!'
        return av_ves

    def populate_board(self):
        """Creates a blank game board and populates it with vessels according to \
        the definition in available_vessels(). calls place_vessel() for placement.
        """
        self.board = np.zeros((self.rows, self.columns, self.levels), dtype=object)
        for vessel in self.vessels:
            for ind in range(self.vessels[vessel]):
                v = vessel(ind)
                self.place_vessel(v)
        
    def place_vessel(self, v: Vessel):
        """Chooses a random place on the board, and if it is empty, places a vessel \
        there according to the defined Vessel.vshape
        """
        trial = 0
        while True:
            rand_co = (randint(0,self.rows-v.vshape.shape[0]+2),
                        randint(0,self.columns-v.vshape.shape[1]+2),
                        v.level)
            vslice=self.board[rand_co[0]:rand_co[0]+v.vshape.shape[0],
                                    rand_co[1]:rand_co[1]+v.vshape.shape[1],
                                    rand_co[2]]
            if not vslice.any():
                try:
                    vslice[v.vshape]=v
                    break
                except Exception:
                    pass
            else:
                v.rotate()
            trial += 1
            ###########################################################
            # maximal fitting vessels is a hard mathematical problem. #
            # Insted, if placing fails too many times, it is probably #
            # too much and an error is raised. Tested and works fine. #
            ###########################################################
            if trial > self.rows*self.columns:
                raise Exception(f'{Levels(v.level).name} seems to be too crowded. Board is too small for so many vessels.')

    def validate_target(self, player_input):
        try:
            x, y, z = eval(player_input)
            try:
                t = self.board[x,y,z]
                if self.fire(t):
                    if (t.vname == 'general') or (np.size(np.flatnonzero(self.board))==1):
                        return 'game_over'
                    self.board[x,y,z] = 0
                return True
            except IndexError as e:
                print('Invalid coordinates:', e)
        except (SyntaxError, ValueError, NameError, TypeError):
            print('Invalid coordinates.')
        return False

    def fire(self, t):
        if t:
            if t.under_fire():
                self.board[self.board==t] = 0
            return True
        else:
            print('signal.MISS')
        return False


def start():
    boards = {'Board_1': Board(player_id=1, dim=board_dim), 'Board_2': Board(player_id=2, dim=board_dim)}
    print(f"""Welcome to another game of Submarines!\n\
            \nThe shape of the board is {boards['Board_1'].board.shape}.\
            \nYou can type 'show' to show your board, and 'quit' to exit the game prematurely.\
            \nThe pieces were set (randomly), let the game begin!
            """)
    i, j = 1, 2
    cont_game = True
    while cont_game:
        player_input = input(f"Player {i}, what is the coordinate you're targeting (x, y, z)? ")
        if player_input == 'show':
            print(boards[f'Board_{i}'])
        elif player_input == 'quit':
            print('quiting...')
            cont_game = False
        else:
            target = boards[f'Board_{j}'].validate_target(player_input)
            if target:
                if target == 'game_over':
                    print(f'The game is over! Thw winner is Player {i}')
                    cont_game = False
                else:
                    i = 1 if i==2 else 2
                    j = 1 if i==2 else 2
                    

if __name__ == "__main__":
    board_dim = (4,4,3)
    available_vessels = {Submarine: 1, Destroyer: 1, Jet: 1, General: 1}
    start()