import pytest
import json
import random
import sys
import math
import os
import sympy

sys.path.append('../src')

from TaggedInterpreter import TaggedInterpreter, FailedTagException
from general import *

@pytest.fixture(scope="session", autouse=True)
def before_tests():
    global byte_codes
    folder_path = "../examples"
    folder_path_target = "../examples/decompiled/"
    analyse_bytecode(folder_path, folder_path_target)
    files = get_paths(folder_path)
    byte_codes = {}
    for file_path in files:
        with open(file_path, 'r') as file:
            json_obj = json.load(file)
            byte_codes.update(get_functions(os.path.basename(file_path).split(".")[0], json_obj))

    folder_path_class_files = "../../course-02242-examples/src/executables/java/dtu/compute/exec"
    folder_path = "../../course-02242-examples/decompiled/dtu/compute/exec/"
    analyse_bytecode(folder_path_class_files, folder_path)
    files = get_paths(folder_path)
    for file_path in files:
        with open(file_path, 'r') as file:
            json_obj = json.load(file)
            byte_codes.update(get_functions(os.path.basename(file_path).split(".")[0], json_obj))

    folder_path = "../../course-02242-examples/decompiled/eu/bogoe/dtu/exceptional"
    files = get_paths(folder_path)
    for file_path in files:
        with open(file_path, 'r') as file:
            json_obj = json.load(file)
            byte_codes.update(get_functions(os.path.basename(file_path).split(".")[0], json_obj))

def test_DirectInputsUsage_Throw():
    interpret = TaggedInterpreter(byte_codes['DirectInputsUsage_main'], byte_codes)
    (l, s, pc) = [0, 1], [], 0
    interpret.memory = []
    try:
        interpret.run((l, s, pc))
        raise Exception("THIS SHOULD NEVER HAPPEN")
    except FailedTagException as e:
        assert set(['LV0']) == set(e.tags)

def test_DirectInputsUsage_DoesntThrow():
    interpret = TaggedInterpreter(byte_codes['DirectInputsUsage_main'], byte_codes)
    (l, s, pc) = [1, 1], [], 0
    interpret.memory = []
    interpret.run((l, s, pc))

def test_OperationOnInput_Throw():
    interpret = TaggedInterpreter(byte_codes['OperationOnInput_main'], byte_codes)
    (l, s, pc) = [-1, 1], [], 0
    interpret.memory = []
    try:
        interpret.run((l, s, pc))
        raise Exception("THIS SHOULD NEVER HAPPEN")
    except FailedTagException as e:
        assert set(['LV0']) == set(e.tags)

def test_OperationOnInput_DoesntThrow():
    interpret = TaggedInterpreter(byte_codes['OperationOnInput_main'], byte_codes)
    (l, s, pc) = [0, 1], [], 0
    interpret.memory = []
    interpret.run((l, s, pc))

def test_IndirectUsageIf_Throw():
    interpret = TaggedInterpreter(byte_codes['IndirectUsageIf_main'], byte_codes)
    (l, s, pc) = [1, 1], [], 0
    interpret.memory = []
    try:
        interpret.run((l, s, pc))
        raise Exception("THIS SHOULD NEVER HAPPEN")
    except FailedTagException as e:
        assert set(['LV0']) == set(e.tags)

def test_IndirectUsageIf_DoesntThrow():
    interpret = TaggedInterpreter(byte_codes['IndirectUsageIf_main'], byte_codes)
    (l, s, pc) = [-1, 1], [], 0
    interpret.memory = []
    interpret.run((l, s, pc))


def test_TaggingInsideFunction_Throw():
    interpret = TaggedInterpreter(byte_codes['TaggingInsideFunction_main'], byte_codes)
    (l, s, pc) = [1, 0], [], 0
    interpret.memory = []
    try:
        interpret.run((l, s, pc))
        raise Exception("THIS SHOULD NEVER HAPPEN")
    except FailedTagException as e:
        assert set(['LV1']) == set(e.tags)

def test_TaggingInsideFunction_DoesntThrow():
    interpret = TaggedInterpreter(byte_codes['TaggingInsideFunction_main'], byte_codes)
    (l, s, pc) = [-1, 1], [], 0
    interpret.memory = []
    interpret.run((l, s, pc))

def test_SplittingInput_Throw():
    interpret = TaggedInterpreter(byte_codes['SplittingInput_main'], byte_codes)
    (l, s, pc) = ["str1", "str2"], [], 0
    interpret.memory = []
    try:
        interpret.run((l, s, pc))
        raise Exception("THIS SHOULD NEVER HAPPEN")
    except FailedTagException as e:
        assert set(['LV1']) == set(e.tags)

def test_DirectInputUsageIf_Throw():
    interpret = TaggedInterpreter(byte_codes['DirectInputUsageIf_main'], byte_codes)
    (l, s, pc) = [1, 0], [], 0
    interpret.memory = []
    try:
        interpret.run((l, s, pc))
        raise Exception("THIS SHOULD NEVER HAPPEN")
    except FailedTagException as e:
        assert set(['LV0', 'LV1']) == set(e.tags)

def test_ArrayAcces_Throw():
    interpret = TaggedInterpreter(byte_codes['ArrayAcces_main'], byte_codes)
    (l, s, pc) = [0, 5], [], 0
    interpret.memory = [["str1","str2"]]
    try:
        interpret.run((l, s, pc))
        raise Exception("THIS SHOULD NEVER HAPPEN")
    except FailedTagException as e:
        assert set(['LV1']) == set(e.tags)

def test_ArrayElement_Throw():
    interpret = TaggedInterpreter(byte_codes['ArrayElement_main'], byte_codes)
    (l, s, pc) = [0, 1], [], 0
    interpret.memory = [["str1","str2"]]
    try:
        interpret.run((l, s, pc))
        raise Exception("THIS SHOULD NEVER HAPPEN")
    except FailedTagException as e:
        assert set(['MVEL1']) == set(e.tags)

def test_noop():
    interpret = TaggedInterpreter(byte_codes['Simple_noop'], byte_codes)
    (l, s, pc) = [], [], 0
    assert None == interpret.run((l, s, pc))

def test_zero():
    interpret = TaggedInterpreter(byte_codes['Simple_zero'], byte_codes)
    (l, s, pc) = [], [], 0
    assert 0 == interpret.run((l, s, pc)).value

def test_hundredAndTwo():
    interpret = TaggedInterpreter(byte_codes['Simple_hundredAndTwo'], byte_codes)
    (l, s, pc) = [], [], 0
    assert 102 == interpret.run((l, s, pc)).value

def test_identity():
    interpret = TaggedInterpreter(byte_codes['Simple_identity'], byte_codes)
    test_int = random.randint(-sys.maxsize, sys.maxsize)
    (l, s, pc) = [test_int], [], 0
    assert test_int == interpret.run((l, s, pc)).value

def test_add():
    interpret = TaggedInterpreter(byte_codes['Simple_add'], byte_codes)
    test_int1 = random.randint(-sys.maxsize, sys.maxsize)
    test_int2 = random.randint(-sys.maxsize, sys.maxsize)
    (l, s, pc) = [test_int1, test_int2], [], 0
    assert test_int1 + test_int2 == interpret.run((l, s, pc)).value

def test_min():
    interpret = TaggedInterpreter(byte_codes['Simple_min'], byte_codes)
    test_int1 = random.randint(-sys.maxsize, sys.maxsize)
    test_int2 = random.randint(-sys.maxsize, sys.maxsize)
    (l, s, pc) = [test_int1, test_int2], [], 0
    assert min(test_int1, test_int2) == interpret.run((l, s, pc)).value

def test_factorial():
    interpret = TaggedInterpreter(byte_codes['Simple_factorial'], byte_codes)
    test_int = random.randint(-100, 100)
    (l, s, pc) = [test_int], [], 0
    if test_int >= 0:
        assert math.factorial(test_int) == interpret.run((l, s, pc)).value
    else:
        assert 1 == interpret.run((l, s, pc)).value

def test_helloWorld():
    interpret = TaggedInterpreter(byte_codes['Calls_helloWorld'], byte_codes)
    (l, s, pc) = [], [], 0
    assert None == interpret.run((l, s, pc))

def test_fib():
    interpret = TaggedInterpreter(byte_codes['Calls_fib'], byte_codes)
    test_int = random.randint(0, 25)
    logger.info("TRYING " + str(test_int))
    (l, s, pc) = [test_int], [], 0
    assert sympy.fibonacci(test_int+1) == interpret.run((l, s, pc)).value

def test_first():
    interpret = TaggedInterpreter(byte_codes['Array_first'], byte_codes)
    test_arr = [random.randint(0, 25) for i in range(random.randint(1, 25))]
    (l, s, pc) = [0], [], 0
    interpret.memory = [test_arr]
    assert test_arr[0] == interpret.run((l, s, pc)).value

def test_access():
    interpret = TaggedInterpreter(byte_codes['Array_access'], byte_codes)
    test_arr = [random.randint(0, 25) for i in range(random.randint(1, 25))]
    test_int = random.randint(0, len(test_arr)-1)
    (l, s, pc) = [test_int, 0], [], 0
    interpret.memory = [test_arr]
    assert test_arr[test_int] == interpret.run((l, s, pc)).value

def test_newArray():
    interpret = TaggedInterpreter(byte_codes['Array_newArray'], byte_codes)
    (l, s, pc) = [], [], 0
    assert 1 == interpret.run((l, s, pc)).value

def test_bubbleSort():
    interpret = TaggedInterpreter(byte_codes['Array_bubbleSort'], byte_codes)
    test_arr = [random.randint(0, 25) for i in range(random.randint(0, 25))]
    input = test_arr.copy()
    (l, s, pc) = [0], [], 0
    interpret.memory = [test_arr]
    interpret.run((l, s, pc))
    output = [i.value for i in interpret.memory[0].value]
    assert sorted(input) ==  output


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
        assert set([]) == set(e.tags)
