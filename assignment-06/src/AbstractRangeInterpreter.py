from JavaMethod import JavaMethod
from Comparison import AbstractRangeComparison

from BaseInterpreter import BaseInterpreter

class RangeSet():
    def __init__(self, start, end):
        self.start = start
        self.end = end

    def __str__(self):
        return "[{}, {}]".format(self.start, self.end)
    

class AbstractRangeInterpreter(BaseInterpreter):
    def __init__(self, program, verbose, avail_programs):
        super().__init__(program, verbose, avail_programs)

        # Assign classes to attributes for later use
        self.comparison = AbstractRangeComparison  # Assigning the AbstractRangeComparison class to self.comparison
        from ArithmeticOperation import AbstractRangeArithmeticOperation
        self.arithmeticOperation = AbstractRangeArithmeticOperation  # Assigning the AbstractRangeArithmeticOperation class to self.arithmeticOperation
        self.javaMethod = JavaMethod  # Assigning the AbstractRangeJavaMethod class to self.javaMethod


    def cast(self, i):
        if type(i) == RangeSet:
            return i
        return RangeSet(i, i)

    def _push(self, b):
        (l, os, pc) = self.stack.pop(-1)
        value = b["value"]
        value = RangeSet(value["value"], value["value"])  # Create a new RangeSet object with the value as both start and end
        self.stack.append((l, os + [value], pc + 1))
    
    def _incr(self, b):
        # Increment the value in an array by a specified amount
        (lv, os, pc) = self.stack.pop(-1)
        lv[b["index"]].start = lv[b["index"]].start + b["amount"]
        lv[b["index"]].end = lv[b["index"]].end + b["amount"]
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
        condition = getattr(self.comparison, "_"+b["condition"])(os[-1], self.cast(0))


        if "class" in self.program["bytecode"][pc+1]:
            if self.program["bytecode"][pc+1]["class"] == "java/lang/AssertionError":
                os[-1] = getattr(self.comparison, "_assert_"+b["condition"])(os[-1], self.cast(0))
                pc = b["target"]
        elif "class" in self.program["bytecode"][b["target"]]:
            if self.program["bytecode"][b["target"]]["class"] == "java/lang/AssertionError":
                opp = self.comparison._opposite(getattr(self.comparison, "_"+b["condition"]))
                os[-1] = getattr(self.comparison, "_assert_"+opp)(os[-1], self.cast(0))
                pc = pc + 1
        else:
            if condition != "Maybe":
                if condition:
                    pc = b["target"]
                else:
                    pc = pc + 1
            else:
                print("ADDING A BRANCH")
                # deep copy of local variables and change using os[-1] the new copy not the old one
                # os[-1] = getattr(self.comparison, "_assert_"+b["condition"])(os[-1], self.cast(0))
                self.branch_list[pc] = (lv_copy, os[:-1], b["target"])
                os[-1] = getattr(self.comparison, "_assert_"+b["condition"])(os[-1], self.cast(0))
                pc = pc+1


        self.stack.append((lv, os[:-1], pc))

    def _negate(self, b):
        (lv, os, pc) = self.stack.pop(-1)
        os[-1].start = -os[-1].end 
        os[-1].end = -os[-1].start 
        self.stack.append((lv, os, pc + 1))
