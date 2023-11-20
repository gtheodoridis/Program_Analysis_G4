import glob
import pathlib
import subprocess
import argparse
import os
import json
import subprocess
import time
from types import SimpleNamespace

def run_script(script_path, args):
    start_time = time.perf_counter()
    subprocess.run(["python3", script_path, *args], 
                   stdout=subprocess.DEVNULL, 
                   stderr=subprocess.DEVNULL)
    end_time = time.perf_counter()
    return end_time - start_time

def run_java(args):
    start_time = time.perf_counter()
    subprocess.run(["java", "-cp", *args], 
                   stdout=subprocess.DEVNULL, 
                   stderr=subprocess.DEVNULL)
    end_time = time.perf_counter()
    return end_time - start_time

def get_paths(folder_path):
    return glob.glob(folder_path + '/**/*.json', recursive = True)

def get_functions(file_name, json_obj):
    functions = {}
    for func in json_obj['methods']:
        functions[file_name + "_" + func['name']] = func
    return functions

def analyse_bytecode(folder_path, target_folder_path):
    # This function analyzes Java bytecode files (.class) using the jvm2json tool. It takes a folder path as input, finds all .class files in the specified folder and its subdirectories, and then uses the subprocess module to run the jvm2json tool to convert each .class file into a corresponding JSON file (.json).
    class_files = glob.glob(folder_path + '/**/*.class', recursive=True)
    # logger.info(class_files)
    for class_file in class_files:
        json_file = pathlib.Path(class_file).name
        json_file = json_file.replace('.class', '.json')
        command = [
            "jvm2json",
            "-s", class_file,
            "-t", target_folder_path+json_file
        ]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # logger.info(result)


def main(folder_path, folder_path_target, file_path, memory_values):
    analyse_bytecode(folder_path, folder_path_target)

    function_name = file_path[file_path.rfind('/')+1:-5]+'_main'
    with open(file_path, 'r') as file:
        json_obj = json.load(file)
        functions = get_functions(os.path.basename(file_path).split(".")[0], json_obj)
        num_of_bytecode_opr = len(functions[function_name]['code']['bytecode'])

    script_path = "java-crash-input-reporter.py"
    total_time = 0

    args_file_path = os.path.splitext(args.file_path)[0] + '.class'
    for _ in range(100):
        if memory_values:
            execution_time = run_script(script_path, [args_file_path, "--memory_values", *memory_values])
        else:
            execution_time = run_script(script_path, [args_file_path])
        total_time += execution_time

    average_time = total_time / 100
    print(f"Average execution time of each java bytecode operation in analysis: {average_time/num_of_bytecode_opr} seconds")

    args_file_path = args_file_path.replace('.class', '')
    args_file_path1 = args_file_path.split('/')[0]
    args_file_path2 = args_file_path.split('/')[1]
    for _ in range(100):
        if memory_values:
            execution_time = run_java([args_file_path1, args_file_path2, *memory_values])
        else:
            execution_time = run_java([args_file_path1, args_file_path2])
        total_time += execution_time

    average_time = total_time / 100
    print(f"Average execution time of each java bytecode operation: {average_time/num_of_bytecode_opr} seconds")

if __name__ == "__main__":
    # parser = argparse.ArgumentParser(description="Process file paths.")
    
    # Adding optional arguments with default values as None
    # parser.add_argument('--folder_path', type=str, default=None,
    #                     help='Path to the folder')
    # parser.add_argument('--folder_path_target', type=str, default=None,
    #                     help='Path to the target folder')
    # parser.add_argument('file_path', type=str,
    #                     help='Path to the class file of the main function. Should be a .class file.')
    
    # Adding arguments for local variables and memory values
    # parser.add_argument('--local_variables_values', nargs='+', default=[], type=parse_local_variable,
    #                 help='List of values for local variables (integers or strings)')
    # parser.add_argument('--memory_values', nargs='+', default=[], action=ParseMemoryValues,
                    # help='Lists of string values passed to program inside argv, each element separated by spaces, e.g., "str3 str4"')

    # args = parser.parse_args()
    
    list_args = []

    arg = SimpleNamespace()
    arg.file_path = "examples/IndirectUsageIf.class"
    arg.memory_values = ["1"]
    arg.folder_path = None
    arg.folder_path_target = None
    list_args.append(arg)

    arg = SimpleNamespace()
    arg.file_path = "examples/TaggingInsideFunction.class"
    arg.memory_values = ["1", "0"]
    arg.folder_path = None
    arg.folder_path_target = None
    list_args.append(arg)

    arg = SimpleNamespace()
    arg.file_path = "examples/SplittingInput.class"
    arg.memory_values = ["str1", "str2"]
    arg.folder_path = None
    arg.folder_path_target = None
    list_args.append(arg)

    arg = SimpleNamespace()
    arg.file_path = "examples/DirectInputUsageIf.class"
    arg.memory_values = ["1", "0"]
    arg.folder_path = None
    arg.folder_path_target = None
    list_args.append(arg)

    arg = SimpleNamespace()
    arg.file_path = "examples/ArrayAcces.class"
    arg.memory_values = ["str1","str2"]
    arg.folder_path = None
    arg.folder_path_target = None
    list_args.append(arg)

    arg = SimpleNamespace()
    arg.file_path = "examples/ArrayElement.class"
    arg.memory_values = ["str1"]
    arg.folder_path = None
    arg.folder_path_target = None
    list_args.append(arg)

    for args in list_args:
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
        
        main(args.folder_path, args.folder_path_target, args.file_path, args.memory_values)