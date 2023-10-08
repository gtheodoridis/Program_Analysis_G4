from general import *

class BaseInterpreter:
    def __init__(self, program, verbose, avail_programs):
        self.program = program
        self.verbose = verbose
        self.avail_programs = avail_programs
        self.memory = []
        self.stack = []
                
        self.branch_list = {}

        self.comparison = None
        self.arithmeticOperation = None
        self.javaMethod = None
    
    def cast(self, i):
        return i

    def run(self, f):
        self.stack.append(f)
        self.log_start()
        self.log_state()
        while True:
            end_of_program, return_value = self.step()
            self.log_state()
            if return_value != None:
                print("Program Returning: ", return_value)
                return_list = [return_value]
                for branch in self.branch_list.keys():
                    interpret = self.__class__(self.program, self.verbose, self.avail_programs)
                    ret = interpret.run(self.branch_list[branch])
                    print("Program Returning: ", ret)
                    return_list.append(ret)
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
            raise Exception("UnsupportedOperationException")
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
        value = getattr(self.arithmeticOperation, "_"+b["operant"])(os[-2], os[-1])
        self.stack.append((lv, os[:-2] + [value], pc + 1))

    def _if(self, b):
        (lv, os, pc) = self.stack.pop(-1)
        condition = getattr(self.comparison, "_"+b["condition"])(os[-2], os[-1])
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

    def _ifz(self, b): # maybe we remove later
        (lv, os, pc) = self.stack.pop(-1)
        condition = getattr(self.comparison, "_"+b["condition"])(os[-1], 0)
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
        if b["field"]["name"] == '$assertionsDisabled':
            value = self.cast(0)
        else:
            value = getattr(self.javaMethod, "_get")(b["field"])
        self.stack.append((lv, os + [value], pc + 1))

    def _invoke(self, b):
        (lv, os, pc) = self.stack.pop(-1)
        arg_num = len(b["method"]["args"])

        try:
            if hasattr(self.javaMethod, "_" + b["method"]["name"]):
                if arg_num == 0:
                    value = getattr(self.javaMethod, "_" + b["method"]["name"])([])
                else:    
                    value = getattr(self.javaMethod, "_" + b["method"]["name"])(*os[-arg_num:])
                if b["access"] == "static":
                    if b["method"]["ref"]["name"] == os[-arg_num-1]:
                        self.stack.append((lv, os[:-arg_num-1] + [value], pc + 1))
                    else:
                        raise Exception
            elif b["access"] == "special" and b["method"]["ref"]["name"] == "java/lang/AssertionError":
                    self.stack = []
            else:
                raise Exception
        except:
            pr = None
            for av_pr in self.avail_programs:
                if av_pr.endswith(b["method"]["name"]):
                    pr = av_pr
            if not pr:
                raise Exception("UnsupportedOperationException")
            
            # if b["method"]["name"] not in self.avail_programs:
            #     raise Exception("UnsupportedOperationException")

            interpret = self.__class__(self.avail_programs[pr], self.verbose, self.avail_programs)
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

    def _dup(self, b):
        (lv, os, pc) = self.stack.pop(-1)
        self.stack.append((lv, os + os[-b["words"]:], pc + 1))

    # TODO: classes are not implemented yet
    def _new(self, b):
        (lv, os, pc) = self.stack.pop(-1)
        self.stack.append((lv, os, pc + 1))

    def _array_load(self, b):
        pass

    def _array_store(self, b):
        pass

    def _newarray(self, b):
        pass

    def _arraylength(self, b):
        pass 

    def _incr(self, b):
        pass

    def _negate(self, b):
        pass
