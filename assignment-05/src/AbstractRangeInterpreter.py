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
        # index_array is assumed to not be a range but an integer
        index_array = os[-2]  # Index of the array
        if index_el < 0 or index_el >= len(self.memory[index_array]):
            raise Exception("IndexOutOfBoundsException")
        if index_array < 0 or index_array >= len(self.memory):
            raise Exception("NullPointerException")
        value = self.memory[index_array][index_el]  # Get the value from memory
        self.stack.append((lv, os[:-2] + [value], pc + 1))

    def _array_store(self, b):
        # Store a value in an array
        (lv, os, pc) = self.stack.pop(-1)
        value = os[-1]  # Value to store
        # index_array is assumed to not be a range but an integer
        index_of_array = os[-3]  # Index of the array to store in
        index_of_el = os[-2]  # Index of the element in the array
        if index_of_el < 0 or index_of_el > len(self.memory[index_of_array]):
            raise Exception("IndexOutOfBoundsException")
        if index_of_array < 0 or index_of_array >= len(self.memory):
            raise Exception("NullPointerException")
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
