
import json
import os
import argparse
import ast
import hashlib
import sys

sys.path.append('./src/')

from TaggedInterpreter import *
from general import *
from Logger import logger

class ParseMemoryValues(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        # Process the values here as needed
        # For example, you might want to split each value by spaces
        processed_values = []
        for value in values:
            # Split by spaces and extend the list
            processed_values.extend(value.split())
        
        # Set the processed values in the namespace
        setattr(namespace, self.dest, processed_values)
    
def generate_report(exception, interpreter, function_name, json_obj, file_path):
    # Calculate SHA256 of the file
    def get_sha256(file_path):
        with open(file_path, 'rb') as f:
            bytes = f.read()  # Read the entire file as bytes
            return hashlib.sha256(bytes).hexdigest()

    # Generate the report
    print("---CRASH SUMMARY---")
    print(f"Filename: {file_path}")
    print(f"SHA256: {get_sha256(file_path)}")
    print(f"COMMAND:")
    print(sys.executable)
    print(sys.argv)
    print("Disassembly of crashing operation:")
    print(interpreter.history["last_opr"])

    print("Stack and memory history:")
    for key, value in interpreter.history.items():
        if key != "last_opr":
            print(f"{key}: {value}")

    print("Extra Data:")
    for func in interpreter.functions:
        print(func)
    
    print("---END SUMMARY---")


def main(folder_path, folder_path_target, file_path, l_values, memory_values):
    analyse_bytecode(folder_path, folder_path_target)

    function_name = file_path[file_path.rfind('/')+1:-5]+'_main'
    with open(file_path, 'r') as file:
        json_obj = json.load(file)
        functions = get_functions(os.path.basename(file_path).split(".")[0], json_obj)
        # function_name = 'ArrayElement_main'
        interpret = TaggedInterpreter(functions[function_name], functions)
        (l, s, pc) = l_values, [], 0
        # (l, s, pc) = [0, 1], [], 0
        interpret.memory = memory_values
        # interpret.memory = [["str1","str2"]]
        try:
            interpret.run((l, s, pc))
        except FailedTagException as e:
            print(e)
            generate_report(e, interpret, function_name, json_obj, file_path)
        

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process file paths.")
    
    # Adding optional arguments with default values as None
    parser.add_argument('--folder_path', type=str, default=None,
                        help='Path to the folder')
    parser.add_argument('--folder_path_target', type=str, default=None,
                        help='Path to the target folder')
    parser.add_argument('file_path', type=str,
                        help='Path to the class file of the main function. Should be a .class file.')
    
    # Adding arguments for local variables and memory values
    # parser.add_argument('--local_variables_values', nargs='+', default=[], type=parse_local_variable,
    #                 help='List of values for local variables (integers or strings)')
    parser.add_argument('--memory_values', nargs='+', default=[], action=ParseMemoryValues,
                    help='Lists of string values passed to program inside argv, each element separated by spaces, e.g., "str3 str4"')

    args = parser.parse_args()

    # Check if file_path has .class extension
    if not args.file_path.lower().endswith('.class'):
        raise ValueError("The file_path must be a .class file")
    
    # Change .class extension to .json
    args.file_path = os.path.splitext(args.file_path)[0] + '.json'

    # Determine the default values based on file_path if not provided
    base_path = os.path.dirname(args.file_path)
    if args.folder_path is None:
        args.folder_path = base_path
    if args.folder_path_target is None:
        args.folder_path_target = base_path

    if not args.folder_path.endswith('/'):
        args.folder_path = args.folder_path + "/"
    if not args.folder_path_target.endswith('/'):
        args.folder_path_target = args.folder_path_target + "/"

    args.file_path = args.folder_path_target + os.path.splitext(args.file_path)[0].split('/')[-1] + ".json"
    
    if args.memory_values:
        args.local_variables_values = [0]
        args.memory_values = [args.memory_values]
    else:
        args.local_variables_values = []
        args.memory_values = [args.memory_values]

    main(args.folder_path, args.folder_path_target, args.file_path, args.local_variables_values, args.memory_values)

