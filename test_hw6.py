import pytest
from hw6 import *

def test_vessels():
        assert Submarine(0)
        assert Destroyer(0)
        with pytest.raises(NameError):
                assert Kite(0)

def test_submarine_kill():
        s = Submarine(0)
        assert s.under_fire()

def test_destroyer_hit():
        d = Destroyer(0)
        assert not d.under_fire()

def test_destroyer_kill():
        d = Destroyer(0)
        d.under_fire()
        d.under_fire()
        d.under_fire()
        assert d.under_fire()

def test_vessel_rotation():
        j = Jet(0)
        j.vshape = np.array([[0,1,0],
                        [1,1,1],
                        [0,1,0],
                        [0,1,0]], dtype=bool)
        j_rotated = np.array([[0,0,1,0],
                        [1,1,1,1],
                        [0,0,1,0]], dtype=bool)
        j.rotate()
        assert np.array_equal(j.vshape, j_rotated)

def test_board():
        assert Board()

def test_board_small():
        with pytest.raises(AssertionError):
                Board(dim=(3,3,3))

def test_general_exist():
        with pytest.raises(AssertionError):
                Board(board_vessels={Jet:1})

def test_one_general():
        with pytest.raises(AssertionError):
                Board(board_vessels={General:0})

def test_only_one_general():
        with pytest.raises(AssertionError):
                Board(board_vessels={General:2})

def test_too_many_vessels():
        with pytest.raises(AssertionError):
                Board(board_vessels={Jet:2, General:1})

def test_valid_target():
        b = Board()
        assert b._validate_target('(0,0,0)')
        assert b._validate_target('0,0,0')

def test_invalid_target_level():
        b = Board()
        assert not b._validate_target('(3,3,3)')
                
def test_invalid_target_size():
        b = Board()
        assert not b._validate_target('4,2,2')

def test_not_full_coord():
        b = Board()
        assert not b._validate_target('1,1')
                
def test_invalid_coord():
        b = Board()
        assert not b._validate_target('a')

def test_vessel_fire():
        v = Vessel(0)
        b = Board()
        assert b._fire(v)

def test_empty_fire():
        e = 0
        b = Board()
        assert not b._fire(e)
