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
        while self.step():
            self.log_state()
        self.log_done()

    def step(self):
        (l, s, pc) = self.stack[-1]
        b = self.program['bytecode'][pc]
        if hasattr(self, "_"+b["opr"]):
            return getattr(self, "_"+b["opr"])(b)
        else:
            return False
    
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
        (l, s, pc) = self.stack.pop(-1)
        if len(self.stack) == 1:
            self.stack.append((l, s[:-1], pc + 1))
            return False
        else:
            return False


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

        interpret = Interpreter(byte_codes['noop'], True)
        (l, s, pc) = [], [], 0
        interpret.run((l, s, pc))

if __name__ == "__main__":
    main()
