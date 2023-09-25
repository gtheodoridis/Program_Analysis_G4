from JavaMethod import AbstractRangeJavaMethod
from Comparison import AbstractRangeComparison
from ArithmeticOperation import AbstractRangeArithmeticOperation
from BaseInterpreter import BaseInterpreter

class RangeSet():
    def __init__(self, start, end):
        self.start = start
        self.end = end

class AbstractRangeInterpreter(BaseInterpreter):
    def __init__(self, program, verbose, avail_programs):
        super().__init__(program, verbose, avail_programs)

        # Assign classes to attributes for later use
        self.comparison = AbstractRangeComparison  # Assigning the AbstractRangeComparison class to self.comparison
        self.arithmeticOperation = AbstractRangeArithmeticOperation  # Assigning the AbstractRangeArithmeticOperation class to self.arithmeticOperation
        self.javaMethod = AbstractRangeJavaMethod  # Assigning the AbstractRangeJavaMethod class to self.javaMethod

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
        index_array = os[-2]  # Index of the array
        value = self.memory[index_array][index_el]  # Get the value from memory
        self.stack.append((lv, os[:-2] + [value], pc + 1))

    def _array_store(self, b):
        # Store a value in an array
        (lv, os, pc) = self.stack.pop(-1)
        value = os[-1]  # Value to store
        index_of_array = os[-3]  # Index of the array to store in
        index_of_el = os[-2]  # Index of the element in the array
        if len(self.memory[index_of_array]) <= index_of_el:
            self.memory[index_of_array].append(value)  # If the array is not long enough, extend it
        else:
            self.memory[index_of_array][index_of_el] = value  # Otherwise, update the existing element
        self.stack.append((lv, os[:-3], pc + 1))

    def _newarray(self, b):
        # Create a new array and store its index
        (lv, os, pc) = self.stack.pop(-1)
        self.memory.append([])  # Create a new empty array in memory
        self.stack.append((lv, os + [len(self.memory)-1], pc + 1))  # Store the index of the new array

    def _arraylength(self, b):
        # Get the length of an array
        (lv, os, pc) = self.stack.pop(-1)
        index_array = os[-1]  # Index of the array
        value = len(self.memory[index_array])  # Get the length of the array in memory
        self.stack.append((lv, os[:-1] + [value], pc + 1))
