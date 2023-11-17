import pytest
import json
import sys
import os

sys.path.append('../src')

from TaggedInterpreter import TaggedInterpreter, FailedTagException
from general import *

@pytest.fixture(scope="session", autouse=True)
def before_tests():
    global byte_codes
    byte_codes = {}

    folder_path = "../../course-02242-examples/decompiled/eu/bogoe/dtu/exceptional"
    files = get_paths(folder_path)
    for file_path in files:
        with open(file_path, 'r') as file:
            json_obj = json.load(file)
            byte_codes.update(get_functions(os.path.basename(file_path).split(".")[0], json_obj))

def test_Arithmetics_alwaysThrows1():
    interpret = TaggedInterpreter(byte_codes['Arithmetics_alwaysThrows1'], byte_codes)
    (l, s, pc) = [], [], 0
    interpret.memory = []

    try:
        interpret.run((l, s, pc))
        raise Exception("THIS SHOULD NEVER HAPPEN")
    except FailedTagException as e:
        print(e)
        assert set([]) == set(e.tags)


def test_Arithmetics_alwaysThrows2():
    interpret = TaggedInterpreter(byte_codes['Arithmetics_alwaysThrows2'], byte_codes)
    (l, s, pc) = [None], [], 0
    interpret.memory = []
    try:
        interpret.run((l, s, pc))
        raise Exception("THIS SHOULD NEVER HAPPEN")
    except FailedTagException as e:
        print(e)
        assert set(['LV0']) == set(e.tags)

def test_Arithmetics_alwaysThrows3():
    interpret = TaggedInterpreter(byte_codes['Arithmetics_alwaysThrows3'], byte_codes)
    (l, s, pc) = [9, 0], [], 0
    interpret.memory = []
    try:
        interpret.run((l, s, pc))
        raise Exception("THIS SHOULD NEVER HAPPEN")
    except FailedTagException as e:
        print(e)
        assert set(['LV0', 'LV1']) == set(e.tags)

def test_Arithmetics_alwaysThrows4():
    interpret = TaggedInterpreter(byte_codes['Arithmetics_alwaysThrows4'], byte_codes)
    (l, s, pc) = [8, 0], [], 0
    interpret.memory = []
    try:
        interpret.run((l, s, pc))
        raise Exception("THIS SHOULD NEVER HAPPEN")
    except FailedTagException as e:
        print(e)
        assert set(['LV0', 'LV1']) == set(e.tags)

def test_Arithmetics_alwaysThrows5():
    interpret = TaggedInterpreter(byte_codes['Arithmetics_alwaysThrows5'], byte_codes)
    (l, s, pc) = [0, 8], [], 0
    interpret.memory = []
    try:
        interpret.run((l, s, pc))
        raise Exception("THIS SHOULD NEVER HAPPEN")
    except FailedTagException as e:
        print(e)
        assert set(['LV0', 'LV1']) == set(e.tags)

def test_Arithmetics_itDependsOnLattice1():
    interpret = TaggedInterpreter(byte_codes['Arithmetics_itDependsOnLattice1'], byte_codes)
    (l, s, pc) = [], [], 0
    interpret.memory = []
    interpret.run((l, s, pc))

def test_Arithmetics_itDependsOnLattice2():
    interpret = TaggedInterpreter(byte_codes['Arithmetics_itDependsOnLattice2'], byte_codes)
    (l, s, pc) = [], [], 0
    interpret.memory = []
    interpret.run((l, s, pc))

def test_Arithmetics_itDependsOnLattice3():
    interpret = TaggedInterpreter(byte_codes['Arithmetics_itDependsOnLattice3'], byte_codes)
    (l, s, pc) = [1000, 100], [], 0
    interpret.memory = []
    try:
        interpret.run((l, s, pc))
        raise Exception("THIS SHOULD NEVER HAPPEN")
    except FailedTagException as e:
        print(e)
        assert set(['LV0', 'LV1']) == set(e.tags)

def test_Arithmetics_itDependsOnLattice4():
    interpret = TaggedInterpreter(byte_codes['Arithmetics_itDependsOnLattice4'], byte_codes)
    (l, s, pc) = [], [], 0
    interpret.memory = []
    try:
        interpret.run((l, s, pc))
        raise Exception("THIS SHOULD NEVER HAPPEN")
    except FailedTagException as e:
        print(e)
        assert set([]) == set(e.tags)

def test_Arithmetics_neverThrows1():
    interpret = TaggedInterpreter(byte_codes['Arithmetics_neverThrows1'], byte_codes)
    (l, s, pc) = [], [], 0
    interpret.memory = []
    interpret.run((l, s, pc))
    
def test_Arithmetics_neverThrows2():
    interpret = TaggedInterpreter(byte_codes['Arithmetics_neverThrows2'], byte_codes)
    (l, s, pc) = [5], [], 0
    interpret.memory = []
    interpret.run((l, s, pc))

def test_Arithmetics_neverThrows3():
    interpret = TaggedInterpreter(byte_codes['Arithmetics_neverThrows3'], byte_codes)
    (l, s, pc) = [5, 8], [], 0
    interpret.memory = []
    interpret.run((l, s, pc))

def test_Arithmetics_neverThrows4():
    interpret = TaggedInterpreter(byte_codes['Arithmetics_neverThrows4'], byte_codes)
    (l, s, pc) = [5], [], 0
    interpret.memory = []
    interpret.run((l, s, pc))

def test_Arithmetics_neverThrows5():
    interpret = TaggedInterpreter(byte_codes['Arithmetics_neverThrows5'], byte_codes)
    (l, s, pc) = [5, 8], [], 0
    interpret.memory = []
    interpret.run((l, s, pc))

def test_Arithmetics_speedVsPrecision():
    interpret = TaggedInterpreter(byte_codes['Arithmetics_speedVsPrecision'], byte_codes)
    (l, s, pc) = [], [], 0
    interpret.memory = []
    try:
        interpret.run((l, s, pc))
        raise Exception("THIS SHOULD NEVER HAPPEN")
    except FailedTagException as e:
        print(e)
        assert set([]) == set(e.tags)

def test_Arrays_alwaysThrows1():
    interpret = TaggedInterpreter(byte_codes['Arrays_alwaysThrows1'], byte_codes)
    (l, s, pc) = [], [], 0
    interpret.memory = []
    try:
        interpret.run((l, s, pc))
        raise Exception("THIS SHOULD NEVER HAPPEN")
    except FailedTagException as e:
        print(e)
        assert set([]) == set(e.tags)

def test_Arrays_alwaysThrows2():
    interpret = TaggedInterpreter(byte_codes['Arrays_alwaysThrows2'], byte_codes)
    (l, s, pc) = [0], [], 0
    interpret.memory = [[]]
    try:
        interpret.run((l, s, pc))
        raise Exception("THIS SHOULD NEVER HAPPEN")
    except FailedTagException as e:
        print(e)
        assert set([]).issubset(e.tags)
