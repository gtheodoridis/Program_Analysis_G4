import z3

from JavaMethod import JavaMethod
from Comparison import AbstractRangeComparison

from BaseInterpreter import BaseInterpreter


class ConcolicValue():
    def __init__(self, value, symb_value = ""):
        self.concrete = value
        self.symbolic = symb_value


    def __str__(self):
        return "Concolic {}".format(self.concrete)

    def __repr__(self):
        return self.__str__()

class ConcolicInterpreter(BaseInterpreter):
    def __init__(self, program, verbose, avail_programs):
        super().__init__(program, verbose, avail_programs)

        # Assign classes to attributes for later use
        self.comparison = AbstractRangeComparison  # Assigning the AbstractRangeComparison class to self.comparison
        from ArithmeticOperation import ArithmeticOperation
        self.arithmeticOperation = ArithmeticOperation  # Assigning the AbstractRangeArithmeticOperation class to self.arithmeticOperation
        self.javaMethod = JavaMethod  # Assigning the AbstractRangeJavaMethod class to self.javaMethod

        self.solver = z3.Solver()
        self.path = []

    def run(self, f):
        # self.stack.append(f)
        self.log_start()
        self.log_state()

        params = [z3.Int(f"p{i}") for i, _ in enumerate(self.program['params'])]

        self.program = self.program['code']

        while self.solver.check() == z3.sat:
            self.path = []
            model = self.solver.model()
            input = [model.eval(p, model_completion=True).as_long() for p in params]
            conc_input = [ConcolicValue(i[0], i[1]) for i in zip(input, params)]
            

            _f = conc_input, [], 0
            self.stack.append(_f)
            while True:
                try:
                    end_of_program, return_value = self.step()
                except Exception as e:
                    print(e)
                    break

                self.log_state()
                if return_value != None:
                    print("Program Returning: ", return_value)
                    return return_value
                if end_of_program:
                    break
            
            print(self.path)

            path_constraint = z3.simplify(z3.And(*self.path))
            self.solver.add(z3.Not(path_constraint))
    
        self.log_done()
        return None

    def _push(self, b):
        (l, os, pc) = self.stack.pop(-1)
        value = b["value"]
        value = ConcolicValue(value["value"])  # Create a new RangeSet object with the value as both start and end
        self.stack.append((l, os + [value], pc + 1))
    
    def _incr(self, b):
        # Increment the value in an array by a specified amount
        (lv, os, pc) = self.stack.pop(-1)
        lv[b["index"]].value = lv[b["index"]].value + b["amount"]
        self.stack.append((lv, os, pc + 1))

    def _array_load(self, b):
        # Load a value from an array
        (lv, os, pc) = self.stack.pop(-1)
        index_el = os[-1]  # Index of the element to load

        # TODO: maybe replace with for loop        
        assert index_el.start == index_el.end


        # index_array is assumed to not be a range but an integer
        index_array = os[-2]  # Index of the array
        if index_el.start < 0 or index_el.start >= len(self.memory[index_array]):
            raise Exception("IndexOutOfBoundsException")
        if index_array < 0 or index_array >= len(self.memory):
            raise Exception("NullPointerException")
        value = self.memory[index_array][index_el.start]  # Get the value from memory
        self.stack.append((lv, os[:-2] + [value], pc + 1))

    def _array_store(self, b):
        # Store a value in an array
        (lv, os, pc) = self.stack.pop(-1)
        value = os[-1]  # Value to store
        # index_array is assumed to not be a range but an integer
        index_of_array = os[-3]  # Index of the array to store in
        index_of_el = os[-2]  # Index of the element in the array

        # TODO: maybe replace with for loop        
        assert index_of_el.start == index_of_el.end
        
        if index_of_el.start < 0 or index_of_el.start >= len(self.memory[index_of_array]):
            raise Exception("IndexOutOfBoundsException")
        if index_of_array < 0 or index_of_array >= len(self.memory):
            raise Exception("NullPointerException")
        self.memory[index_of_array][index_of_el.start] = value  # Otherwise, update the existing element
        self.stack.append((lv, os[:-3], pc + 1))

    def _newarray(self, b):
        # Create a new array and store its index
        (lv, os, pc) = self.stack.pop(-1)
        size = os[-1]

        # TODO: maybe replace with for loop        
        assert size.start == size.end

        # TODO: use dimension
        dim = b["dim"]
        self.memory.append([None] * size.start)  # Create a new empty array in memory
        self.stack.append((lv, os + [len(self.memory)-1], pc + 1))  # Store the index of the new array

    def _arraylength(self, b):
        # Get the length of an array
        (lv, os, pc) = self.stack.pop(-1)
        index_array = os[-1]  # Index of the array
        value = len(self.memory[index_array])  # Get the length of the array in memory
        self.stack.append((lv, os[:-1] + [value], pc + 1))

    def _ifz(self, b): # maybe we remove later
        (lv, os, pc) = self.stack.pop(-1)
        condition = getattr(self.comparison, "_"+b["condition"])(os[-1].concrete, ConcolicValue(0))
        if condition:
            pc = b["target"]
        else:
            pc = pc + 1
        self.stack.append((lv, os[:-1], pc))

    def _binary(self, b):
        (lv, os, pc) = self.stack.pop(-1)
        if b["operant"] == "div":
            if os[-1].concrete == 0:
                self.path.append(os[-1].symbolic == 0)
            else:
                self.path.append(z3.simplify(z3.Not(os[-1].symbolic == 0)))


        value = getattr(self.arithmeticOperation, "_"+b["operant"])(os[-2].concrete, os[-1].concrete)
        
        self.stack.append((lv, os[:-2] + [ConcolicValue(value)], pc + 1))