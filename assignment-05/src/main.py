from Interpreter import *
from AbstractRangeInterpreter import *
from general import *
import json

def main():
    folder_path = "../../course-02242-examples/src/executables/java/dtu/compute/exec"
    folder_path_target = "../../course-02242-examples/decompiled/dtu/compute/exec/"
    analyse_bytecode(folder_path, folder_path_target)
    file_path = "../../course-02242-examples/decompiled/dtu/compute/exec/Simple.json"
    with open(file_path, 'r') as file:
        json_obj = json.load(file)
        byte_codes = get_functions(json_obj)

        interpret = AbstractRangeInterpreter(byte_codes['add'], False, byte_codes)
        (l, s, pc) = [RangeSet(1, 10), RangeSet(2, 5)], [], 0
        interpret.memory = []
        ret = interpret.run((l, s, pc))
        print(ret)
        

if __name__ == "__main__":
    main()