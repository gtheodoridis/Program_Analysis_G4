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
    file_path = "../examples/decompiled/ParseComplex.json"
    # file_path = "../examples/decompiled/Simple.json"
    function_name = file_path[file_path.rfind('/')+1:-5]+'_main'
    with open(file_path, 'r') as file:
        json_obj = json.load(file)
        byte_codes = get_functions_code(os.path.basename(file_path).split(".")[0], json_obj)
        functions = get_functions(os.path.basename(file_path).split(".")[0], json_obj)

        interpret = TaggedInterpreter(functions[function_name], byte_codes)
        (l, s, pc) = ["FUZ"], [], 0
        interpret.memory = []
        ret = interpret.run((l, s, pc))
        logger.info(ret)
        

if __name__ == "__main__":
    main()