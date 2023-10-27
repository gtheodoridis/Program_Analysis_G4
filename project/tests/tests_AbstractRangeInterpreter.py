import pytest
import json
import random
import sys
import math
import os

sys.path.append('../src')

from AbstractRangeInterpreter import AbstractRangeInterpreter, RangeSet
from general import *

@pytest.fixture(scope="session", autouse=True)
def before_tests():
    global byte_codes
    # folder_path_class_files = "../../course-02242-examples/src/executables/java/dtu/compute/exec"
    folder_path = "../../course-02242-examples/decompiled/eu/bogoe/dtu/exceptional"
    # analyse_bytecode(folder_path_class_files, folder_path)
    files = get_paths(folder_path)
    byte_codes = {}
    for file_path in files:
        with open(file_path, 'r') as file:
            json_obj = json.load(file)
            byte_codes.update(get_functions(os.path.basename(file_path).split(".")[0], json_obj))

def test_Arithmetics_alwaysThrows1():
    interpret = AbstractRangeInterpreter(byte_codes['Arithmetics_alwaysThrows1'], True, byte_codes)
    (l, s, pc) = [], [], 0
    interpret.memory = []
    try:
        interpret.run((l, s, pc))
    except Exception as e:
        assert "ArithmeticException" == str(e)

def test_Arithmetics_alwaysThrows2():
    interpret = AbstractRangeInterpreter(byte_codes['Arithmetics_alwaysThrows2'], True, byte_codes)
    (l, s, pc) = [None], [], 0
    interpret.memory = []
    try:
        interpret.run((l, s, pc))
    except Exception as e:
        assert "ArithmeticException" == str(e)

def test_Arithmetics_alwaysThrows3():
    interpret = AbstractRangeInterpreter(byte_codes['Arithmetics_alwaysThrows3'], True, byte_codes)
    (l, s, pc) = [RangeSet(-100, 100), RangeSet(-100, 100)], [], 0
    interpret.memory = []
    try:
        interpret.run((l, s, pc))
    except Exception as e:
        assert "ArithmeticException" == str(e)

def test_Arithmetics_alwaysThrows4():
    interpret = AbstractRangeInterpreter(byte_codes['Arithmetics_alwaysThrows4'], True, byte_codes)
    (l, s, pc) = [RangeSet(-1, 100), RangeSet(-100, 1)], [], 0
    interpret.memory = []
    try:
        interpret.run((l, s, pc))
    except Exception as e:
        assert "ArithmeticException" == str(e)

def test_Arithmetics_alwaysThrows5():
    interpret = AbstractRangeInterpreter(byte_codes['Arithmetics_alwaysThrows5'], True, byte_codes)
    (l, s, pc) = [RangeSet(-100, 100), RangeSet(-100, 100)], [], 0
    interpret.memory = []
    try:
        interpret.run((l, s, pc))
    except Exception as e:
        assert "ArithmeticException" == str(e)

def test_Arithmetics_itDependsOnLattice1():
    interpret = AbstractRangeInterpreter(byte_codes['Arithmetics_itDependsOnLattice1'], True, byte_codes)
    (l, s, pc) = [], [], 0
    interpret.memory = []
    interpret.run((l, s, pc))

def test_Arithmetics_itDependsOnLattice2():
    interpret = AbstractRangeInterpreter(byte_codes['Arithmetics_itDependsOnLattice2'], True, byte_codes)
    (l, s, pc) = [], [], 0
    interpret.memory = []
    interpret.run((l, s, pc))

def test_Arithmetics_itDependsOnLattice3():
    interpret = AbstractRangeInterpreter(byte_codes['Arithmetics_itDependsOnLattice3'], True, byte_codes)
    (l, s, pc) = [RangeSet(1000, 100000), RangeSet(100, 100000)], [], 0
    interpret.memory = []
    try:
        interpret.run((l, s, pc))
    except Exception as e:
        assert "ArithmeticException" == str(e)

def test_Arithmetics_itDependsOnLattice4():
    interpret = AbstractRangeInterpreter(byte_codes['Arithmetics_itDependsOnLattice4'], True, byte_codes)
    (l, s, pc) = [], [], 0
    interpret.memory = []
    try:
        interpret.run((l, s, pc))
    except Exception as e:
        assert "ArithmeticException" == str(e)

def test_Arithmetics_neverThrows1():
    interpret = AbstractRangeInterpreter(byte_codes['Arithmetics_neverThrows1'], True, byte_codes)
    (l, s, pc) = [], [], 0
    interpret.memory = []
    interpret.run((l, s, pc))
    
def test_Arithmetics_neverThrows2():
    interpret = AbstractRangeInterpreter(byte_codes['Arithmetics_neverThrows2'], True, byte_codes)
    (l, s, pc) = [RangeSet(-100, 100)], [], 0
    interpret.memory = []
    interpret.run((l, s, pc))

def test_Arithmetics_neverThrows3():
    interpret = AbstractRangeInterpreter(byte_codes['Arithmetics_neverThrows3'], True, byte_codes)
    (l, s, pc) = [RangeSet(-100, 100), RangeSet(-100, 100)], [], 0
    interpret.memory = []
    interpret.run((l, s, pc))

def test_Arithmetics_neverThrows4():
    interpret = AbstractRangeInterpreter(byte_codes['Arithmetics_neverThrows4'], True, byte_codes)
    (l, s, pc) = [RangeSet(-100, 100)], [], 0
    interpret.memory = []
    interpret.run((l, s, pc))

def test_Arithmetics_neverThrows5():
    interpret = AbstractRangeInterpreter(byte_codes['Arithmetics_neverThrows5'], True, byte_codes)
    (l, s, pc) = [RangeSet(-100, 100), RangeSet(-100, 100)], [], 0
    interpret.memory = []
    interpret.run((l, s, pc))

def test_Arithmetics_speedVsPrecision():
    interpret = AbstractRangeInterpreter(byte_codes['Arithmetics_speedVsPrecision'], True, byte_codes)
    (l, s, pc) = [], [], 0
    interpret.memory = []
    try:
        interpret.run((l, s, pc))
    except Exception as e:
        assert "ArithmeticException" == str(e)

def test_Arrays_alwaysThrows1():
    flag_passed = 0
    interpret = AbstractRangeInterpreter(byte_codes['Arrays_alwaysThrows1'], True, byte_codes)
    (l, s, pc) = [], [], 0
    interpret.memory = []
    try:
        interpret.run((l, s, pc))
    except Exception as e:
        flag_passed = 1
        assert "IndexOutOfBoundsException" == str(e)
    
    assert flag_passed == 1

def test_Arrays_alwaysThrows2():
    flag_passed = 0
    interpret = AbstractRangeInterpreter(byte_codes['Arrays_alwaysThrows2'], True, byte_codes)
    (l, s, pc) = [0], [], 0
    interpret.memory = [[]]
    try:
        interpret.run((l, s, pc))
    except Exception as e:
        flag_passed = 1
        assert "IndexOutOfBoundsException" == str(e)

    assert flag_passed == 1

