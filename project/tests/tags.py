import pytest
import json
import sys
import os
import cProfile

sys.path.append('../src')

from TaggedInterpreter import TaggedInterpreter, FailedTagException
from general import *
pr = cProfile.Profile()

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
    yield
    pr.print_stats()
    pr.dump_stats('test.prof')
    # gprof2dot -f pstats test.prof | dot -Tpng -o output.png

def test_DirectInputsUsage_Throw():
    
    interpret = TaggedInterpreter(byte_codes['DirectInputsUsage_main'], byte_codes)
    (l, s, pc) = [0], [], 0
    interpret.memory = [["0", "1"]]
    try:
        pr.enable()
        interpret.run((l, s, pc))
        raise Exception("THIS SHOULD NEVER HAPPEN")
    except FailedTagException as e:
        assert set(['MVEL0']) == set(e.tags)
    finally:
        pr.disable()

def test_DirectInputsUsage_DoesntThrow():
    interpret = TaggedInterpreter(byte_codes['DirectInputsUsage_main'], byte_codes)
    (l, s, pc) = [0], [], 0
    interpret.memory = [["1", "1"]]
    pr.enable()
    interpret.run((l, s, pc))
    pr.disable()

def test_OperationOnInput_Throw():
    interpret = TaggedInterpreter(byte_codes['OperationOnInput_main'], byte_codes)
    (l, s, pc) = [0], [], 0
    interpret.memory = [["-1", "1"]]
    try:
        pr.enable()
        interpret.run((l, s, pc))
        raise Exception("THIS SHOULD NEVER HAPPEN")
    except FailedTagException as e:
        assert set(['MVEL0']).issubset(e.tags)
    finally:
        pr.disable()

def test_OperationOnInput_DoesntThrow():
    interpret = TaggedInterpreter(byte_codes['OperationOnInput_main'], byte_codes)
    (l, s, pc) = [0], [], 0
    interpret.memory = [["0", "1"]]
    pr.enable()
    interpret.run((l, s, pc))
    pr.disable()

def test_IndirectUsageIf_Throw():
    interpret = TaggedInterpreter(byte_codes['IndirectUsageIf_main'], byte_codes)
    (l, s, pc) = [0], [], 0
    interpret.memory = [["1", "1"]]
    try:
        pr.enable()
        interpret.run((l, s, pc))
        raise Exception("THIS SHOULD NEVER HAPPEN")
    except FailedTagException as e:
        assert set(['MVEL0']).issubset(e.tags)
    finally:
        pr.disable()

def test_IndirectUsageIf_DoesntThrow():
    interpret = TaggedInterpreter(byte_codes['IndirectUsageIf_main'], byte_codes)
    (l, s, pc) = [0], [], 0
    interpret.memory = [["-1", "1"]]
    pr.enable()
    interpret.run((l, s, pc))
    pr.disable()

def test_TaggingInsideFunction_Throw():
    interpret = TaggedInterpreter(byte_codes['TaggingInsideFunction_main'], byte_codes)
    (l, s, pc) = [0], [], 0
    interpret.memory = [["1", "0"]]
    try:
        pr.enable()
        interpret.run((l, s, pc))
        raise Exception("THIS SHOULD NEVER HAPPEN")
    except FailedTagException as e:
        assert set(['MVEL1']) == set(e.tags)
    finally:
        pr.disable()

def test_TaggingInsideFunction_DoesntThrow():
    interpret = TaggedInterpreter(byte_codes['TaggingInsideFunction_main'], byte_codes)
    (l, s, pc) = [0], [], 0
    interpret.memory = [["-1", "1"]]
    pr.enable()
    interpret.run((l, s, pc))
    pr.disable()

def test_SplittingInput_Throw():
    interpret = TaggedInterpreter(byte_codes['SplittingInput_main'], byte_codes)
    (l, s, pc) = [0], [], 0
    interpret.memory = [["str1", "str2"]]
    try:
        pr.enable()
        interpret.run((l, s, pc))
        raise Exception("THIS SHOULD NEVER HAPPEN")
    except FailedTagException as e:
        assert set(['MVEL1']) == set(e.tags)
    finally:
        pr.disable()

def test_DirectInputUsageIf_Throw():
    interpret = TaggedInterpreter(byte_codes['DirectInputUsageIf_main'], byte_codes)
    (l, s, pc) = [0], [], 0
    interpret.memory = [["1", "0"]]
    try:
        pr.enable()
        interpret.run((l, s, pc))
        raise Exception("THIS SHOULD NEVER HAPPEN")
    except FailedTagException as e:
        assert set(['MVEL0', 'MVEL1']) == set(e.tags)
    finally:
        pr.disable()

def test_ArrayAcces_Throw():
    interpret = TaggedInterpreter(byte_codes['ArrayAcces_main'], byte_codes)
    (l, s, pc) = [0], [], 0
    interpret.memory = [["str1","str2"]]
    try:
        pr.enable()
        interpret.run((l, s, pc))
        raise Exception("THIS SHOULD NEVER HAPPEN")
    except FailedTagException as e:
        assert set(['MV0']).issubset(e.tags)
    finally:
        pr.disable()

def test_ArrayElement_Throw():
    interpret = TaggedInterpreter(byte_codes['ArrayElement_main'], byte_codes)
    (l, s, pc) = [0], [], 0
    interpret.memory = [["str1"]]
    try:
        pr.enable()
        interpret.run((l, s, pc))
        raise Exception("THIS SHOULD NEVER HAPPEN")
    except FailedTagException as e:
        assert set(['MVEL0']) == set(e.tags)
    finally:
        pr.disable()
