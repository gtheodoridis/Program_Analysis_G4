from Interpreter import *
from AbstractRangeInterpreter import *
from general import *
import json

# TODO: check inputs of the fucntion and automatically generate the inputs in local variables
def main():
    folder_path = "../../course-02242-examples/src/executables/java/eu/bogoe/dtu/exceptional"
    folder_path_target = "../../course-02242-examples/decompiled/eu/bogoe/dtu/exceptional"
    analyse_bytecode(folder_path, folder_path_target)
    file_path = "../../course-02242-examples/decompiled/eu/bogoe/dtu/exceptional/Arithmetics.json"
    with open(file_path, 'r') as file:
        json_obj = json.load(file)
        byte_codes = get_functions(json_obj)

        interpret = AbstractRangeInterpreter(byte_codes['alwaysThrows1'], False, byte_codes)
        (l, s, pc) = [], [], 0
        interpret.memory = []
        ret = interpret.run((l, s, pc))
        print(ret)
        

if __name__ == "__main__":
    main()