import numpy as np
from numpy.random import randint
from enum import Enum
from typing import Union

class Levels(Enum):
    Deep = 0
    Sea_level = 1
    Air = 2

class Vessel:
    """A Vessel class for some defaults of all Vessel sub-classes.
    Creates a Vessel repr defined by its vname and ind.
    Attributes: ind.
    Methods: assert_vessel, rotate, under_fire.
    """
    
    def __init__(self, ind: int):
        self.ind = ind+1
        self.vname = 'vessel'
        # A Vessel does not store its place on board. If needed, a line should be added to Board._place_vessel().
        
    def __repr__(self):
        return f'{self.vname}{self.ind}'   
    
    def assert_vessel(self):
        """Results in error if a vessel in dict{available_vessels} is not 
        defined as a Vessel (sub-)class
        """
        pass
    
    def rotate(self) -> None:
        """Changes vessel orientation"""
        self.vshape = np.rot90(self.vshape,3)

    def under_fire(self) -> bool:
        """Default vessel behavior when targeted (signal.KILL)."""
        self.kill = True
        print('signal.KILL')
        return self.kill

class Submarine(Vessel):
    """A submarine class, includes the submarine shape, and vname for repr.
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
    """A destroyer class, includes the destroyer shape, and vname for repr.
    Attributes: ind, level, vshape, vname, kill.
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
        
    def under_fire(self) -> bool:
        """Destroyer is destroyed (signal.KILL) only when fully hit (signal.HIT).
        Will work with any Vessel/vshape.
        """
        self.hit +=1
        self.kill = False if self.hit < self.vshape.sum() else True
        print('signal.KILL' if self.kill else 'signal.HIT')
        return self.kill

class Jet(Vessel):
    """A jet class, includes the jet shape, and vname for repr.
    Attributes: ind, level, vshape, vname, kill.
    """
    
    def __init__(self, ind: int):
        super().__init__(ind)
        self.level = Levels.Air.value
        self.vshape = np.array([[0,1,0],
                                [1,1,1],
                                [0,1,0],
                                [0,1,0]], dtype=bool)
        if bool(randint(2)):
            self.rotate()
        self.vname = 'jet'

class General(Vessel):
    """A general class, includes the general shape and vname for repr.
    Attributes: ind, level, vshape, vname, kill.
    Methods: under_fire.
    """
    
    def __init__(self, ind: int):
        self.ind = ''
        self.level = randint(max([level.value for level in Levels])+1)
        self.vshape = np.array ([[1]], dtype=bool)
        self.vname = 'general'

    def under_fire(self) -> bool:
        """The game ends (signal.END) when the general is hit."""
        self.kill = True
        print('signal.END')
        return self.kill
    
class Board:
    """A game board class which initiates and populates a board.\n
    The board default dimentions are 4 x4 x3-levels. To change, edit __init__(dim). \
    Asserts 3 levels, each at least 4x4.\n
    The board is populated by default with a single vessel for each type. \
    To change, edit availabe_vessels().\n
    Attributes: player_id, rows, columns, levels, vessels, board.\n
    Methods: _available_vessels, _populate_board, _place_vessel, _validate_target, _fire.
    """
    
    def __init__(self, player_id: int = 0, dim: tuple = (4, 4, 3), 
                board_vessels = {Submarine: 1, Destroyer: 1, Jet: 1, General: 1}):
        self.player_id = player_id
        self.rows, self.columns, self.levels = dim
        assert self.levels == 3, 'Board levels must be 3.'
        assert (self.rows >= 4 and self.columns >= 4), 'Board is too small for its vessels (min 4x4).'
        self.vessels = self._available_vessels(board_vessels)
        self._populate_board()
        
    def __str__(self):
        return (f"""{Levels(0).name}:\n{self.board[:,:,0]}
                    \n{Levels(1).name}:\n{self.board[:,:,1]}
                    \n{Levels(2).name}:\n{self.board[:,:,2]}
                """)
    
    def _available_vessels(self, av_ves: dict) -> dict:
        """Triggered by Board.__init__().
        Defines and asserts the type of vessels for a game.
        Asserts only one general is defined. If there are too many vessels of \
        any other type, the func _populate_board() would raise an exception.
        """
        assert type(av_ves)==dict, 'board_vessels should be a dictionary'
        assert General in av_ves and av_ves[General] == 1, 'You should have 1 general.'
        for ves in av_ves:
            try:
                ves.assert_vessel
            except (NameError, AttributeError):
                raise Exception(f'{ves} is not a Vessel object.')
        return av_ves

    def _populate_board(self) -> None:
        """Triggered by Board.__init__().
        Creates a blank game board and populates it with vessels according to \
        the definition in _available_vessels(). calls _place_vessel() for placement.
        """
        self.board = np.zeros((self.rows, self.columns, self.levels), dtype=object)
        for vessel in self.vessels:
            for ind in range(self.vessels[vessel]):
                v = vessel(ind)
                self._place_vessel(v)
        
    def _place_vessel(self, v: Vessel) -> None:
        """Triggered by Board._populate_board().
        Chooses a random place on the board, and if it is empty, places a vessel \
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
                    # v.vplace = rand_co # if uncommented, a Vessel would store its ref point on board.
                    break
                except Exception:
                    pass
            else:
                v.rotate()
            trial += 1
            ###########################################################
            # Maximal fitting vessels is a hard mathematical problem. #
            # Insted, if placing fails too many times, it is probably #
            # too much and an error is raised. Tested and works fine. #
            ###########################################################
            if trial > self.rows*self.columns:
                raise AssertionError(
                    f'{Levels(v.level).name} seems to be too crowded. Board is too small for so many vessels.')

    def _validate_target(self, player_input) -> Union[bool, str]:
        """Recieves coordinates from main func start(). Calls _fire() and returns True \
        if valid; prints to player and returns False if invalid.
        Returns game_over when _fire() redults in a win condition.
        """
        try:
            x, y, z = eval(player_input)
            try:
                t = self.board[x,y,z]
                # Calls _fire() if coordinates are valid.
                if self._fire(t):
                    # Checks if a win condition is met.
                    if (t.vname == 'general') or (np.size(np.flatnonzero(self.board))==1):
                        return 'game_over'
                    self.board[x,y,z] = 0
                return True
            except IndexError as e:
                print(f'Invalid coordinates or unrecognized command. ({e})\nTry again.')
        except (SyntaxError, ValueError, NameError, TypeError) as e:
            print(f'Invalid coordinates or unrecognized command. ({e})\nTry again.')
        return False

    def _fire(self, t) -> bool:
        """Having a valid coordinates to target from _validate_target(), fires if are'nt empty.
        Returns True when the vessel is destroyed.
        """
        if t:
            if t.under_fire():
                # Destroys the vessel if signal.KILL.
                self.board[self.board==t] = 0
            return True
        else:
            print('signal.MISS')
        return False


def start() -> None:
    """Main function to run a game.
    Creates boards for 2 players and welcome them.
    Asks for player's input, switch players after a valid target.
    Accpets show (and hide) and quit commands.
    """
    boards = {'Board_1': Board(player_id=1, dim=board_dim, board_vessels=available_vessels), 
                'Board_2': Board(player_id=2, dim=board_dim, board_vessels=available_vessels)}
    print(f"""Welcome to another game of Submarines!\n\
            \nThe shape of the board is {boards['Board_1'].board.shape}.\
            \nYou can type show to show your board (and hide to hide it), or \
            \nquit to exit the game prematurely.\
            \nThe pieces were set (randomly), let the game begin!
            """)
    i, j = 1, 2
    cont_game = True
    while cont_game:
        player_input = input(f"Player {i}, what is the coordinate you're targeting (x, y, z)? ")
        if str.lower(player_input) == 'show':
        ##################################################################################
        # I tried to use eval() in order to accept 'show' (and not only show), but that  #
        # evaluate quit as Quitter and raises Exception. Probably can find a workaround. #
        ##################################################################################
            print(boards[f'Board_{i}'])
        elif str.lower(player_input) == 'hide':
            print('\n' *15)
        elif str.lower(player_input) == 'quit':
            print('quiting...')
            cont_game = False
        else:
            target = boards[f'Board_{j}']._validate_target(player_input)
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