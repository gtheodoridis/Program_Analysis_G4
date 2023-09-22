import json

class Interpreter:

    def __init__(self, program, verbose):
        self.program = program
        self.verbose = verbose
        self.memory = {}
        self.stack = []

    def run(self, f):
        self.stack.append(f)
        self.log_start()
        self.log_state()
        while True:
            end_of_program, return_value = self.step()
            self.log_state()
            if return_value != None:
                print("Program Printing: ", return_value)
            if end_of_program:
                break
        self.log_done()

    def step(self):
        if len(self.stack) == 0:
            return True, None
        (l, s, pc) = self.stack[-1]
        if pc >= len(self.program['bytecode']):
            return True, None
        b = self.program['bytecode'][pc]
        print("Executing: ", b)
        if hasattr(self, "_"+b["opr"]):
            return False, getattr(self, "_"+b["opr"])(b)
        else:
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
            # self.stack.append((l, os[:-1], pc + 1))
            return None
        elif b["type"] == "int":
            # self.stack.append((l, os[:-1], pc + 1))
            return os[-1]
        
    def _push(self, b):
        (l, os, pc) = self.stack.pop(-1)
        value = b["value"]
        self.stack.append((l, os + [value["value"]], pc + 1))

    def _load(self, b):
        (lv, os, pc) = self.stack.pop(-1)
        value = lv[b["index"]]
        self.stack.append((lv, os + [value], pc + 1))

    def _binary(self, b):
        (lv, os, pc) = self.stack.pop(-1)
        if b["operant"] == "add":
            value = os[-2] + os[-1]
        self.stack.append((lv, os[:-2] + [value], pc + 1))


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


def main():
    file_path = "../course-02242-examples/decompiled/dtu/compute/exec/Simple.json"
    with open(file_path, 'r') as file:
        json_obj = json.load(file)
        byte_codes = get_functions(json_obj)

        interpret = Interpreter(byte_codes['add'], True)
        (l, s, pc) = [5, 6], [], 0
        interpret.run((l, s, pc))

if __name__ == "__main__":
    main()
