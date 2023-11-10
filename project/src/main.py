from Interpreter import *
from TaggedInterpreter import *
from general import *
from Logger import logger
import json
import os


# TODO: check inputs of the fucntion and automatically generate the inputs in local variables
def main():
    folder_path = "../examples"
    folder_path_target = "../examples/decompiled/"
    analyse_bytecode(folder_path, folder_path_target)
    # file_path = "../examples/decompiled/IndirectUsageIf.json"
    file_path = "../../course-02242-examples/decompiled/dtu/compute/exec/Calls.json"


    folder_path_class_files = "../../course-02242-examples/src/executables/java/dtu/compute/exec"
    folder_path = "../../course-02242-examples/decompiled/dtu/compute/exec/"
    analyse_bytecode(folder_path_class_files, folder_path)


    function_name = file_path[file_path.rfind('/')+1:-5]+'_main'
    with open(file_path, 'r') as file:
        json_obj = json.load(file)
        # byte_codes = get_functions_code(os.path.basename(file_path).split(".")[0], json_obj)
        functions = get_functions(os.path.basename(file_path).split(".")[0], json_obj)


        # interpret = TaggedInterpreter(functions['Calls_fib'], functions)
        # test_arr = [3,5,1,6]
        # (l, s, pc) = [0], [], 0
        # interpret.memory = [test_arr]
        # assert test_arr[0] == interpret.run((l, s, pc))

        interpret = TaggedInterpreter(functions['Calls_fib'], functions)
        import sympy
        test_int = 5
        logger.info("TRYING " + str(test_int))
        (l, s, pc) = [test_int], [], 0
        assert sympy.fibonacci(test_int+1) == interpret.run((l, s, pc)).value

        # interpret = TaggedInterpreter(functions[function_name], functions)
        # (l, s, pc) = [1, 12], [], 0
        # interpret.memory = []
        # ret = interpret.run((l, s, pc))
        # logger.info(ret)
        

if __name__ == "__main__":
    main()