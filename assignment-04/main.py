import json
import glob
import subprocess
import pathlib

class Comparison:
    def _eq(a, b):
        return a == b
    
    def _ne(a, b):
        return a != b
    
    def _lt(a, b):
        return a < b
    
    def _ge(a, b):
        return a >= b
    
    def _gt(a, b):
        return a > b

    def _le(a, b):
        return a <= b
    
    def _is(a, b):
        return a is b
    
    def _isnot(a, b):
        return a is not b
    
class ArithmaticOperation:
    def _add(a, b):
        return a + b
    
    def _mul(a, b):
        return a * b
    
    def _sub(a, b):
        return a - b
    
    def _div(a, b):
        return a // b
    
    def _mod(a, b):
        return a % b
    
class JavaMethod:
    def __init__(self):
        pass

    def _get(dict):
        if dict == {
              "class": "java/lang/System",
              "name": "out",
              "type": {
                "kind": "class",
                "name": "java/io/PrintStream"
              }
            }:
            return dict["type"]["name"]
        return None
    
    def _println(str):
        print(str)
    


class Interpreter:
    def __init__(self, program, verbose, avail_programs):
        self.program = program
        self.verbose = verbose
        self.avail_programs = avail_programs
        self.memory = []
        self.stack = []

    def run(self, f):
        self.stack.append(f)
        self.log_start()
        self.log_state()
        while True:
            end_of_program, return_value = self.step()
            self.log_state()
            if return_value != None:
                print("Program Returning: ", return_value)
                return return_value
            if end_of_program:
                break
        self.log_done()
        return None

    def step(self):
        if len(self.stack) == 0:
            return True, None
        (l, s, pc) = self.stack[-1]
        b = self.program['bytecode'][pc]
        if self.verbose:
            print("Executing: ", b)
        if hasattr(self, "_"+b["opr"]):
            return False, getattr(self, "_"+b["opr"])(b)
        else:
            print("Unknown instruction: ", b)
            return True, None
    
    def log_start(self):
        if self.verbose:
            print("Starting execution...")
    
    def log_done(self):
        if self.verbose:
            print("Done.")
            
    def log_state(self):
        if self.verbose:
            print("Stack: ", self.stack)
            print("Memory: ", self.memory)

    def _return(self, b):
        (l, os, pc) = self.stack.pop(-1)
        if b["type"] == None:
            return None
        elif b["type"] == "int":
            return os[-1]
        
    def _push(self, b):
        (l, os, pc) = self.stack.pop(-1)
        value = b["value"]
        self.stack.append((l, os + [value["value"]], pc + 1))

    def _load(self, b):
        (lv, os, pc) = self.stack.pop(-1)
        if b["type"] == "ref":
            value = lv[b["index"]]
            self.stack.append((lv, os + [value], pc + 1))
        else:
            value = lv[b["index"]]
            self.stack.append((lv, os + [value], pc + 1))

    def _binary(self, b):
        (lv, os, pc) = self.stack.pop(-1)
        value = getattr(ArithmaticOperation, "_"+b["operant"])(os[-2], os[-1])
        self.stack.append((lv, os[:-2] + [value], pc + 1))

    def _if(self, b):
        (lv, os, pc) = self.stack.pop(-1)
        condition = getattr(Comparison, "_"+b["condition"])(os[-2], os[-1])
        if condition:
            pc = b["target"]
        else:
            pc = pc + 1
        self.stack.append((lv, os[:-2], pc))

    def _store(self, b):
        (lv, os, pc) = self.stack.pop(-1)
        value = os[-1]
        if b["index"] >= len(lv):
            lv = lv + [value]
        else:
            lv[b["index"]] = value
        self.stack.append((lv, os[:-1], pc + 1))

    def _incr(self, b):
        (lv, os, pc) = self.stack.pop(-1)
        lv[b["index"]] = lv[b["index"]] + b["amount"]
        self.stack.append((lv, os, pc + 1))

    def _ifz(self, b):
        (lv, os, pc) = self.stack.pop(-1)
        condition = getattr(Comparison, "_"+b["condition"])(os[-1], 0)
        if condition:
            pc = b["target"]
        else:
            pc = pc + 1
        self.stack.append((lv, os[:-1], pc))

    def _goto(self, b):
        (lv, os, pc) = self.stack.pop(-1)
        value = b["target"]
        pc = value
        self.stack.append((lv, os, pc))
        
    def _get(self, b):
        (lv, os, pc) = self.stack.pop(-1)
        value = getattr(JavaMethod, "_get")(b["field"])
        self.stack.append((lv, os + [value], pc + 1))

    def _invoke(self, b):
        (lv, os, pc) = self.stack.pop(-1)
        arg_num = len(b["method"]["args"])

        try:
            if hasattr(JavaMethod, "_" + b["method"]["name"]):
                if arg_num == 0:
                    value = getattr(JavaMethod, "_" + b["method"]["name"])([])
                else:    
                    value = getattr(JavaMethod, "_" + b["method"]["name"])(*os[-arg_num:])
                if b["access"] != "dynamic":
                    if b["method"]["ref"]["name"] == os[-arg_num-1]:
                        self.stack.append((lv, os[:-arg_num-1] + [value], pc + 1))
                    else:
                        raise Exception
            else:
                raise Exception
        except:
            interpret = Interpreter(self.avail_programs[b["method"]["name"]], self.verbose, self.avail_programs)
            if arg_num == 0:
                (l_new, s_new, pc_new) = [], [], 0
            else:
                (l_new, s_new, pc_new) = os[-arg_num:], [], 0
            ret = interpret.run((l_new, s_new, pc_new))
            if b["method"]["returns"] == None:
                if arg_num == 0:
                    self.stack.append((lv, os, pc + 1))
                else:
                    self.stack.append((lv, os[:-arg_num], pc + 1))
            else:
                if arg_num == 0:
                    self.stack.append((lv, os + [ret], pc + 1))
                else:
                    self.stack.append((lv, os[:-arg_num] + [ret], pc + 1))

    def _array_load(self, b):
        (lv, os, pc) = self.stack.pop(-1)
        index_el = os[-1]
        index_array = os[-2]
        value = self.memory[index_array][index_el]
        self.stack.append((lv, os[:-2] + [value], pc + 1))

    def _array_store(self, b):
        (lv, os, pc) = self.stack.pop(-1)
        value = os[-1]
        index_of_array = os[-3]
        index_of_el = os[-2]
        if len(self.memory[index_of_array]) <= index_of_el:
            self.memory[index_of_array].append(value)
        else:
            self.memory[index_of_array][index_of_el] = value
        self.stack.append((lv, os[:-3], pc + 1))

    def _newarray(self, b):
        (lv, os, pc) = self.stack.pop(-1)
        self.memory.append([])
        self.stack.append((lv, os + [len(self.memory)-1], pc + 1))
    
    def _dup(self, b):
        (lv, os, pc) = self.stack.pop(-1)
        self.stack.append((lv, os + os[-b["words"]:], pc + 1))

    def _arraylength(self, b):
        (lv, os, pc) = self.stack.pop(-1)
        index_array = os[-1]
        value = len(self.memory[index_array])
        self.stack.append((lv, os[:-1] + [value], pc + 1))    

def get_function_bytecode(json_obj):
    return json_obj['code']

def get_functions(json_obj):
    functions = {}
    for func in json_obj['methods']:
        is_case = False
        for annotation in func['annotations']:
            if annotation['type'] == 'dtu/compute/exec/Case':
                is_case = True
                break
        if not is_case:
            continue
        functions[func['name']] = get_function_bytecode(func)
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

# def main():
#     folder_path = "../course-02242-examples/src/executables/java/dtu/compute/exec"
#     folder_path_target = "../course-02242-examples/decompiled/dtu/compute/exec/"
#     analyse_bytecode(folder_path, folder_path_target)
#     file_path = "../course-02242-examples/decompiled/dtu/compute/exec/Simple.json"
#     with open(file_path, 'r') as file:
#         json_obj = json.load(file)
#         byte_codes = get_functions(json_obj)

#         interpret = Interpreter(byte_codes['main'], False, byte_codes)
#         (l, s, pc) = [], [], 0
#         interpret.memory = []
#         ret = interpret.run((l, s, pc))
        

# if __name__ == "__main__":
#     main()
