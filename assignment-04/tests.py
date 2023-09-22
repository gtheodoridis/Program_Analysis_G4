import pytest
import json
import random
import sys
import math
import glob
import sympy

from main import Interpreter


@pytest.fixture(scope="session", autouse=True)
def before_tests():
    def get_paths(folder_path):
        return glob.glob(folder_path + '/**/*.json', recursive = True)

    def get_function_bytecode(json_obj):
        return json_obj['code']

    def get_functions(json_obj):
        functions = {}
        for func in json_obj['methods']:
            is_case = False
            for annotation in func['annotations']:
                if annotation['type'] == 'dtu/compute/exec/Case':
                    is_case = True
                    break
            if not is_case:
                continue
            functions[func['name']] = get_function_bytecode(func)
        return functions

    
    global byte_codes
    folder_path = "../course-02242-examples/decompiled/dtu/compute/exec/"
    files = get_paths(folder_path)
    byte_codes = {}
    for file_path in files:
        with open(file_path, 'r') as file:
            json_obj = json.load(file)
            byte_codes.update(get_functions(json_obj))
            print(byte_codes.keys())

def test_noop():
    interpret = Interpreter(byte_codes['noop'], False, byte_codes)
    (l, s, pc) = [], [], 0
    assert None == interpret.run((l, s, pc))

def test_zero():
    interpret = Interpreter(byte_codes['zero'], False, byte_codes)
    (l, s, pc) = [], [], 0
    assert 0 == interpret.run((l, s, pc))

def test_hundredAndTwo():
    interpret = Interpreter(byte_codes['hundredAndTwo'], False, byte_codes)
    (l, s, pc) = [], [], 0
    assert 102 == interpret.run((l, s, pc))

def test_identity():
    interpret = Interpreter(byte_codes['identity'], False, byte_codes)
    test_int = random.randint(-sys.maxsize, sys.maxsize)
    (l, s, pc) = [test_int], [], 0
    assert test_int == interpret.run((l, s, pc))

def test_add():
    interpret = Interpreter(byte_codes['add'], False, byte_codes)
    test_int1 = random.randint(-sys.maxsize, sys.maxsize)
    test_int2 = random.randint(-sys.maxsize, sys.maxsize)
    (l, s, pc) = [test_int1, test_int2], [], 0
    assert test_int1 + test_int2 == interpret.run((l, s, pc))

def test_min():
    interpret = Interpreter(byte_codes['min'], False, byte_codes)
    test_int1 = random.randint(-sys.maxsize, sys.maxsize)
    test_int2 = random.randint(-sys.maxsize, sys.maxsize)
    (l, s, pc) = [test_int1, test_int2], [], 0
    assert min(test_int1, test_int2) == interpret.run((l, s, pc))

def test_factorial():
    interpret = Interpreter(byte_codes['factorial'], False, byte_codes)
    test_int = random.randint(-100, 100)
    (l, s, pc) = [test_int], [], 0
    if test_int >= 0:
        assert math.factorial(test_int) == interpret.run((l, s, pc))
    else:
        assert 1 == interpret.run((l, s, pc))

def test_helloWorld():
    interpret = Interpreter(byte_codes['helloWorld'], False, byte_codes)
    (l, s, pc) = [], [], 0
    assert None == interpret.run((l, s, pc))

def test_fib():
    interpret = Interpreter(byte_codes['fib'], False, byte_codes)
    test_int = random.randint(0, 25)
    (l, s, pc) = [test_int], [], 0
    assert sympy.fibonacci(test_int+1) == interpret.run((l, s, pc))