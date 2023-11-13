import glob
import pathlib
import subprocess

import Logger

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