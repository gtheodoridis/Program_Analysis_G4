import glob
import pathlib
import subprocess

def get_paths(folder_path):
    return glob.glob(folder_path + '/**/*.json', recursive = True)

def get_function_bytecode(json_obj):
    return json_obj['code']

def get_functions(file_name, json_obj):
    functions = {}
    for func in json_obj['methods']:
        is_case = False
        for annotation in func['annotations']:
            if annotation['type'] == 'dtu/compute/exec/Case':
                is_case = True
                break
        if not is_case:
            continue
        functions[file_name + "_" + func['name']] = get_function_bytecode(func)
    return functions

def analyse_bytecode(folder_path, target_folder_path):
    # This function analyzes Java bytecode files (.class) using the jvm2json tool. It takes a folder path as input, finds all .class files in the specified folder and its subdirectories, and then uses the subprocess module to run the jvm2json tool to convert each .class file into a corresponding JSON file (.json).
    class_files = glob.glob(folder_path + '/**/*.class', recursive=True)
    for class_file in class_files:
        json_file = pathlib.Path(class_file).name
        json_file = json_file.replace('.class', '.json')
        command = [
            "jvm2json",
            "-s", class_file,
            "-t", target_folder_path+json_file
        ]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(result)


def lists_equal(list1, list2):
    if list1 is None or list2 is None:
        return False

    if len(list1) != len(list2):
        return False

    for rs1, rs2 in zip(list1, list2):
        if rs1 != rs2:
            return False

    return True