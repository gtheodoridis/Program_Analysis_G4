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
        assert None == interpret.run((l, s, pc))
    except Exception as e:
        assert "ArithmeticException" == str(e)

def test_Arithmetics_alwaysThrows2():
    interpret = AbstractRangeInterpreter(byte_codes['Arithmetics_alwaysThrows2'], True, byte_codes)
    (l, s, pc) = [None], [], 0
    interpret.memory = []
    try:
        assert None == interpret.run((l, s, pc))
    except Exception as e:
        assert "ArithmeticException" == str(e)

def test_Arithmetics_alwaysThrows3():
    interpret = AbstractRangeInterpreter(byte_codes['Arithmetics_alwaysThrows3'], True, byte_codes)
    (l, s, pc) = [RangeSet(-100, 100), RangeSet(-100, 100)], [], 0
    interpret.memory = []
    try:
        assert None == interpret.run((l, s, pc))
    except Exception as e:
        assert "ArithmeticException" == str(e)
