import json

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
                return return_value
            if end_of_program:
                break
        self.log_done()
        return None

    def step(self):
        if len(self.stack) == 0:
            return True, None
        (l, s, pc) = self.stack[-1]
        # if pc >= len(self.program['bytecode']):
        #     return True, None
        b = self.program['bytecode'][pc]
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
        # (l_p, os_p, pc_p) = self.stack.pop(-1)
        if b["type"] == None:
            # self.stack.append((l, os[:-1], pc + 1))
            return None
        elif b["type"] == "int":
            # self.stack.append((l, os[:-1], pc + 1))
            # self.stack.append((l_p, os_p + [os[-1]], pc_p+1))
            return os[-1]
        
    def _push(self, b):
        (l, os, pc) = self.stack.pop(-1)
        value = b["value"]
        self.stack.append((l, os + [value["value"]], pc + 1))

    def _load(self, b):
        (lv, os, pc) = self.stack.pop(-1)
        value = lv[b["index"]]
        # lv = lv[:b["index"]] + lv[b["index"] + 1:]
        self.stack.append((lv, os + [value], pc + 1))

    def _binary(self, b):
        (lv, os, pc) = self.stack.pop(-1)
        if b["operant"] == "add":
            value = os[-2] + os[-1]
        elif b["operant"] == "mul":
            value = os[-2] * os[-1]
        elif b["operant"] == "sub":
            value = os[-2] - os[-1]
        elif b["operant"] == "div":
            value = os[-2] // os[-1]
        elif b["operant"] == "mod":
            value = os[-2] % os[-1]
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
            print(b["target"])
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
        print(value)
        self.stack.append((lv, os + [value], pc + 1))

    def _invoke(self, b):
        (lv, os, pc) = self.stack.pop(-1)
        arg_num = len(b["method"]["args"])

        try:
            if b["method"]["ref"]["name"] == os[-arg_num-1]:
                value = getattr(JavaMethod, "_" + b["method"]["name"])(*os[-arg_num:])
                self.stack.append((lv, os[:-arg_num-1] + [value], pc + 1))
            else:
                raise Exception
        except:
            print(self.avail_programs[b["method"]["name"]])
            interpret = Interpreter(self.avail_programs[b["method"]["name"]], True, self.avail_programs)
            (l_new, s_new, pc_new) = os[-arg_num:], [], 0
            print((l_new, s_new, pc_new))
            ret = interpret.run((l_new, s_new, pc_new))
            print("returned from function: ", ret)
            self.stack.append((lv, os[:-arg_num] + [ret], pc + 1))

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
    file_path = "../course-02242-examples/decompiled/dtu/compute/exec/Calls.json"
    with open(file_path, 'r') as file:
        json_obj = json.load(file)
        byte_codes = get_functions(json_obj)

        interpret = Interpreter(byte_codes['fib'], True, byte_codes)
        (l, s, pc) = [10], [], 0
        ret = interpret.run((l, s, pc))
        

if __name__ == "__main__":
    main()
