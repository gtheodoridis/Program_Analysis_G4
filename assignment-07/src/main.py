from Interpreter import *
from ConcolicInterpreter import *
from general import *
import json
import os

# TODO: check inputs of the fucntion and automatically generate the inputs in local variables
def main():
    folder_path = "../../course-02242-examples/src/executables/java/eu/bogoe/dtu/exceptional"
    folder_path_target = "../../course-02242-examples/decompiled/eu/bogoe/dtu/exceptional"
    analyse_bytecode(folder_path, folder_path_target)
    file_path = "../../course-02242-examples/decompiled/eu/bogoe/dtu/exceptional/Arithmetics.json"
    file_path = "../../course-02242-examples/decompiled/eu/bogoe/dtu/Integers.json"
    with open(file_path, 'r') as file:
        json_obj = json.load(file)
        byte_codes = get_functions_code(os.path.basename(file_path).split(".")[0], json_obj)
        functions = get_functions(os.path.basename(file_path).split(".")[0], json_obj)

        interpret = ConcolicInterpreter(functions['Integers_arithmetic'], True, byte_codes)
        (l, s, pc) = [], [], 0
        interpret.memory = []
        ret = interpret.run((l, s, pc))
        print(ret)
        

if __name__ == "__main__":
    main()