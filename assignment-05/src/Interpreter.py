from JavaMethod import JavaMethod
from Comparison import Comparison
from ArithmeticOperation import ArithmeticOperation
from BaseInterpreter import BaseInterpreter

class Interpreter(BaseInterpreter):
    def __init__(self, program, verbose, avail_programs):
        super().__init__(program, verbose, avail_programs)

        self.comparison = Comparison
        self.arithmeticOperation = ArithmeticOperation
        self.javaMethod = JavaMethod
        self.abstr_type = int


    def _push(self, b):
        (l, os, pc) = self.stack.pop(-1)
        value = b["value"]
        self.stack.append((l, os + [value["value"]], pc + 1))
        

    def _incr(self, b):
        (lv, os, pc) = self.stack.pop(-1)
        lv[b["index"]] = lv[b["index"]] + b["amount"]
        self.stack.append((lv, os, pc + 1))


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
        self.memory[index_of_array][index_of_el] = value
        self.stack.append((lv, os[:-3], pc + 1))

    def _newarray(self, b):
        (lv, os, pc) = self.stack.pop(-1)
        size = os[-1]
        self.memory.append([None]*size)
        self.stack.append((lv, os + [len(self.memory)-1], pc + 1))
    
    def _arraylength(self, b):
        (lv, os, pc) = self.stack.pop(-1)
        index_array = os[-1]
        value = len(self.memory[index_array])
        self.stack.append((lv, os[:-1] + [value], pc + 1))    

    def _negate(self, b):
        (lv, os, pc) = self.stack.pop(-1)
        os[-1] = -os[-1]
        self.stack.append((lv, os, pc + 1))
