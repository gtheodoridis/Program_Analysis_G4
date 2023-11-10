import pytest
import json
import random
import sys
import math
import os
import sympy

sys.path.append('../src')

from TaggedInterpreter import TaggedInterpreter, TaggedValue
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

def test_DirectInputsUsage_Throw():
    interpret = TaggedInterpreter(byte_codes['DirectInputsUsage_main'], byte_codes)
    (l, s, pc) = [0, 1], [], 0
    interpret.memory = []
    try:
        interpret.run((l, s, pc))
    except Exception as e:
        assert set(['LV0']) == set(e.args[0])

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
    except Exception as e:
        assert set(['LV0']) == set(e.args[0])

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
    except Exception as e:
        assert set(['LV0']) == set(e.args[0])

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
    except Exception as e:
        assert set(['LV1']) == set(e.args[0])

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
    except Exception as e:
        assert set(['LV1']) == set(e.args[0])

def test_noop():
    interpret = TaggedInterpreter(byte_codes['Simple_noop'], byte_codes)
    (l, s, pc) = [], [], 0
    assert None == interpret.run((l, s, pc))

def test_zero():
    interpret = TaggedInterpreter(byte_codes['Simple_zero'], byte_codes)
    (l, s, pc) = [], [], 0
    assert 0 == interpret.run((l, s, pc))

def test_hundredAndTwo():
    interpret = TaggedInterpreter(byte_codes['Simple_hundredAndTwo'], byte_codes)
    (l, s, pc) = [], [], 0
    assert 102 == interpret.run((l, s, pc))

def test_identity():
    interpret = TaggedInterpreter(byte_codes['Simple_identity'], byte_codes)
    test_int = random.randint(-sys.maxsize, sys.maxsize)
    (l, s, pc) = [test_int], [], 0
    assert test_int == interpret.run((l, s, pc))

def test_add():
    interpret = TaggedInterpreter(byte_codes['Simple_add'], byte_codes)
    test_int1 = random.randint(-sys.maxsize, sys.maxsize)
    test_int2 = random.randint(-sys.maxsize, sys.maxsize)
    (l, s, pc) = [test_int1, test_int2], [], 0
    assert test_int1 + test_int2 == interpret.run((l, s, pc))

def test_min():
    interpret = TaggedInterpreter(byte_codes['Simple_min'], byte_codes)
    test_int1 = random.randint(-sys.maxsize, sys.maxsize)
    test_int2 = random.randint(-sys.maxsize, sys.maxsize)
    (l, s, pc) = [test_int1, test_int2], [], 0
    assert min(test_int1, test_int2) == interpret.run((l, s, pc))

def test_factorial():
    interpret = TaggedInterpreter(byte_codes['Simple_factorial'], byte_codes)
    test_int = random.randint(-100, 100)
    (l, s, pc) = [test_int], [], 0
    if test_int >= 0:
        assert math.factorial(test_int) == interpret.run((l, s, pc))
    else:
        assert 1 == interpret.run((l, s, pc))

def test_helloWorld():
    interpret = TaggedInterpreter(byte_codes['Calls_helloWorld'], byte_codes)
    (l, s, pc) = [], [], 0
    assert None == interpret.run((l, s, pc))

def test_fib():
    interpret = TaggedInterpreter(byte_codes['Calls_fib'], byte_codes)
    test_int = random.randint(0, 25)
    logger.info("TRYING " + str(test_int))
    (l, s, pc) = [test_int], [], 0
    assert sympy.fibonacci(test_int+1) == interpret.run((l, s, pc))

def test_first():
    interpret = TaggedInterpreter(byte_codes['Array_first'], byte_codes)
    test_arr = [random.randint(0, 25) for i in range(random.randint(0, 25))]
    (l, s, pc) = [0], [], 0
    interpret.memory = [test_arr]
    assert test_arr[0] == interpret.run((l, s, pc))

def test_access():
    interpret = TaggedInterpreter(byte_codes['Array_access'], byte_codes)
    test_arr = [random.randint(0, 25) for i in range(random.randint(1, 25))]
    test_int = random.randint(0, len(test_arr)-1)
    (l, s, pc) = [test_int, 0], [], 0
    interpret.memory = [test_arr]
    assert test_arr[test_int] == interpret.run((l, s, pc))

def test_newArray():
    interpret = TaggedInterpreter(byte_codes['Array_newArray'], byte_codes)
    (l, s, pc) = [], [], 0
    assert 1 == interpret.run((l, s, pc))

def test_bubbleSort():
    interpret = TaggedInterpreter(byte_codes['Array_bubbleSort'], byte_codes)
    test_arr = [random.randint(0, 25) for i in range(random.randint(0, 25))]
    (l, s, pc) = [0], [], 0
    interpret.memory = [test_arr]
    interpret.run((l, s, pc))
    assert sorted(test_arr) == interpret.memory[0]
