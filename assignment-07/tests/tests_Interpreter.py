import pytest
import json
import random
import sys
import math
import sympy
import os

sys.path.append('../src')

from Interpreter import Interpreter
from general import *

@pytest.fixture(scope="session", autouse=True)
def before_tests():
    global byte_codes
    folder_path_class_files = "../../course-02242-examples/src/executables/java/dtu/compute/exec"
    folder_path = "../../course-02242-examples/decompiled/dtu/compute/exec/"
    analyse_bytecode(folder_path_class_files, folder_path)
    files = get_paths(folder_path)
    byte_codes = {}
    for file_path in files:
        with open(file_path, 'r') as file:
            json_obj = json.load(file)
            byte_codes.update(get_functions(os.path.basename(file_path).split(".")[0], json_obj))

    print(byte_codes.keys())

def test_noop():
    interpret = Interpreter(byte_codes['Simple_noop'], False, byte_codes)
    (l, s, pc) = [], [], 0
    assert None == interpret.run((l, s, pc))

def test_zero():
    interpret = Interpreter(byte_codes['Simple_zero'], False, byte_codes)
    (l, s, pc) = [], [], 0
    assert 0 == interpret.run((l, s, pc))

def test_hundredAndTwo():
    interpret = Interpreter(byte_codes['Simple_hundredAndTwo'], False, byte_codes)
    (l, s, pc) = [], [], 0
    assert 102 == interpret.run((l, s, pc))

def test_identity():
    interpret = Interpreter(byte_codes['Simple_identity'], False, byte_codes)
    test_int = random.randint(-sys.maxsize, sys.maxsize)
    (l, s, pc) = [test_int], [], 0
    assert test_int == interpret.run((l, s, pc))

def test_add():
    interpret = Interpreter(byte_codes['Simple_add'], False, byte_codes)
    test_int1 = random.randint(-sys.maxsize, sys.maxsize)
    test_int2 = random.randint(-sys.maxsize, sys.maxsize)
    (l, s, pc) = [test_int1, test_int2], [], 0
    assert test_int1 + test_int2 == interpret.run((l, s, pc))

def test_min():
    interpret = Interpreter(byte_codes['Simple_min'], False, byte_codes)
    test_int1 = random.randint(-sys.maxsize, sys.maxsize)
    test_int2 = random.randint(-sys.maxsize, sys.maxsize)
    (l, s, pc) = [test_int1, test_int2], [], 0
    assert min(test_int1, test_int2) == interpret.run((l, s, pc))

def test_factorial():
    interpret = Interpreter(byte_codes['Simple_factorial'], False, byte_codes)
    test_int = random.randint(-100, 100)
    (l, s, pc) = [test_int], [], 0
    if test_int >= 0:
        assert math.factorial(test_int) == interpret.run((l, s, pc))
    else:
        assert 1 == interpret.run((l, s, pc))

def test_helloWorld():
    interpret = Interpreter(byte_codes['Calls_helloWorld'], False, byte_codes)
    (l, s, pc) = [], [], 0
    assert None == interpret.run((l, s, pc))

def test_fib():
    interpret = Interpreter(byte_codes['Calls_fib'], False, byte_codes)
    test_int = random.randint(0, 25)
    print("TRYING ", test_int)
    (l, s, pc) = [test_int], [], 0
    assert sympy.fibonacci(test_int+1) == interpret.run((l, s, pc))

def test_first():
    interpret = Interpreter(byte_codes['Array_first'], False, byte_codes)
    test_arr = [random.randint(0, 25) for i in range(random.randint(0, 25))]
    (l, s, pc) = [0], [], 0
    interpret.memory = [test_arr]
    assert test_arr[0] == interpret.run((l, s, pc))

def test_access():
    interpret = Interpreter(byte_codes['Array_access'], False, byte_codes)
    test_arr = [random.randint(0, 25) for i in range(random.randint(1, 25))]
    test_int = random.randint(0, len(test_arr)-1)
    (l, s, pc) = [test_int, 0], [], 0
    interpret.memory = [test_arr]
    assert test_arr[test_int] == interpret.run((l, s, pc))

def test_newArray():
    interpret = Interpreter(byte_codes['Array_newArray'], False, byte_codes)
    (l, s, pc) = [], [], 0
    assert 1 == interpret.run((l, s, pc))

def test_bubbleSort():
    interpret = Interpreter(byte_codes['Array_bubbleSort'], False, byte_codes)
    test_arr = [random.randint(0, 25) for i in range(random.randint(0, 25))]
    (l, s, pc) = [0], [], 0
    interpret.memory = [test_arr]
    interpret.run((l, s, pc))
    assert sorted(test_arr) == interpret.memory[0]
