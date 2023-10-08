import copy

from JavaMethod import JavaMethod
from Comparison import AbstractRangeComparison

from BaseInterpreter import BaseInterpreter

from general import *

class RangeSet():
    MAX_VALUE = 10000

    def __init__(self, start, end):
        self._start = max(start, -1 * self.MAX_VALUE)
        self._end = min(end, self.MAX_VALUE)

    def __eq__(self, other):
        if not isinstance(other, RangeSet):
            return False
        return self._start == other._start and self._end == other._end
    
    def __hash__(self):
        return hash((self._start, self._end))

    @property
    def start(self):
        return self._start

    @start.setter
    def start(self, value):
        if value <= self.MAX_VALUE:
            self._start = value
        else:
            self._start = self.MAX_VALUE

    @property
    def end(self):
        return self._end

    @end.setter
    def end(self, value):
        if value <= self.MAX_VALUE:
            self._end = value
        else:
            self._end = self.MAX_VALUE

    def __str__(self):
        return "[{}, {}]".format(self.start, self.end)

    def __repr__(self):
        return self.__str__()
    

def deep_copy_with_relationship(lv, os):
    # Create a mapping from old objects to new objects
    mapping = {}

    lv_new = []
    for item in lv:
        new_item = copy.deepcopy(item)
        lv_new.append(new_item)
        mapping[item] = new_item

    # Copy the os, ensuring relationship is retained
    os_new = []
    for item in os:
        if isinstance(item, RangeSet):
            os_new.append(mapping.get(item, copy.deepcopy(item)))
        else:
            os_new.append(item)

    return lv_new, os_new
    

class AbstractRangeInterpreter(BaseInterpreter):
    def __init__(self, program, verbose, avail_programs):
        super().__init__(program, verbose, avail_programs)

        # Assign classes to attributes for later use
        self.comparison = AbstractRangeComparison  # Assigning the AbstractRangeComparison class to self.comparison
        from ArithmeticOperation import AbstractRangeArithmeticOperation
        self.arithmeticOperation = AbstractRangeArithmeticOperation  # Assigning the AbstractRangeArithmeticOperation class to self.arithmeticOperation
        self.javaMethod = JavaMethod  # Assigning the AbstractRangeJavaMethod class to self.javaMethod

        self.worklist = []
        self.states = []

    def cast(self, i):
        if type(i) == RangeSet:
            return i
        return RangeSet(i, i)
    
    def wide(self, value1, value2):
        return RangeSet(
            -1 * RangeSet.MAX_VALUE if (min(value1.start, value2.start) < (-1 * RangeSet.MAX_VALUE/10)) else min(value1.start, value2.start),
            RangeSet.MAX_VALUE if (max(value1.end, value2.end) > (RangeSet.MAX_VALUE/10)) else max(value1.end, value2.end),
        )
    
    def merge(self, old_s, new_s):
        if old_s is None:
            return new_s
        
        olc, os = old_s
        nlc, ns = new_s

        mlc = {
            index: self.wide(olc[index] if index < len(olc) else None, nlc[index] if index < len(nlc) else None) for index in set(range(len(olc))) | set(range(len(nlc)))
        }
        ms = [self.wide(o, n) for o, n in zip(os, ns)]
        
        return (list(mlc.values()), ms)


    def merge_fwd(self, l, lc, s):
        res = self.merge(self.states[l], (lc, s))
        if not lists_equal(res, self.states[l]):
            self.worklist.append(l)
        else:
            print("Reached Fixed Point")
        self.states[l] = res

    def run(self, f):
        self.stack.append(f)
        self.states = [None for b in self.program['bytecode']]
        self.worklist = [0]
        (lv, os, pc) = self.stack[-1]
        self.states[0] = (lv, os)
        self.log_start()
        self.log_state()
        while self.worklist:
            i = self.worklist.pop()
            print("Workinglist:", self.worklist)
            lv, os = self.states[i]
            self.stack[-1] = (lv, os, i)
            end_of_program, return_value = self.step()
            self.log_state()
            if return_value != None:
                print("Program Returning: ", return_value)
            if end_of_program:
                break
        self.log_done()
        return None
    
    def _push(self, b):
        (l, os, pc) = self.stack.pop(-1)
        value = b["value"]
        value = RangeSet(value["value"], value["value"])  # Create a new RangeSet object with the value as both start and end
        self.stack.append((l, os + [value], pc + 1))
        self.merge_fwd(pc + 1, l, os + [value])
    
    def _incr(self, b):
        # Increment the value in an array by a specified amount
        (lv, os, pc) = self.stack.pop(-1)
        lv[b["index"]].start = lv[b["index"]].start + b["amount"]
        lv[b["index"]].end = lv[b["index"]].end + b["amount"]
        self.stack.append((lv, os, pc + 1))
        self.merge_fwd(pc + 1, lv, os)

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
        self.merge_fwd(pc + 1, lv, os[:-2] + [value])

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
        self.merge_fwd(pc + 1, lv, os[:-3])

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
        self.merge_fwd(pc + 1, lv, os + [len(self.memory)-1])

    def _arraylength(self, b):
        # Get the length of an array
        (lv, os, pc) = self.stack.pop(-1)
        index_array = os[-1]  # Index of the array
        value = len(self.memory[index_array])  # Get the length of the array in memory
        self.stack.append((lv, os[:-1] + [value], pc + 1))
        self.merge_fwd(pc + 1, lv, os + [len(self.memory)-1])

    def _ifz(self, b): # maybe we remove later
        (lv, os, pc) = self.stack.pop(-1)
        condition = getattr(self.comparison, "_"+b["condition"])(os[-1], self.cast(0))

        if condition != "Maybe":
            if condition:
                pc = b["target"]
                self.merge_fwd( b["target"], lv, os[:-1])
            else:
                pc = pc + 1
                self.merge_fwd(pc, lv, os[:-1])
        else:
            # branch that will be analysed later
            # deep copy of local variables and change using os[-1] the new copy not the old one
            lv_copy, os_copy = deep_copy_with_relationship(lv, os)
            os_copy[-1] = getattr(self.comparison, "_assert_"+b["condition"])(os_copy[-1], self.cast(0))
            self.branch_list[pc] = (lv_copy, os_copy[:-1], b["target"])
            self.merge_fwd(b["target"], lv_copy, os_copy[:-1])
            # branch that will be analysed now
            opp = self.comparison._opposite(getattr(self.comparison, "_"+b["condition"]))
            os[-1] = getattr(self.comparison, "_assert_"+opp)(os[-1], self.cast(0))
            pc = pc + 1
            self.merge_fwd(pc, lv, os[:-1])

        self.stack.append((lv, os[:-1], pc))

    def _negate(self, b):
        (lv, os, pc) = self.stack.pop(-1)
        os[-1].start = -os[-1].end 
        os[-1].end = -os[-1].start 
        self.stack.append((lv, os, pc + 1))
        self.merge_fwd(pc + 1, lv, os)

    def _load(self, b):
        (lv, os, pc) = self.stack.pop(-1)
        if b["type"] == "ref":
            value = lv[b["index"]]
            self.stack.append((lv, os + [value], pc + 1))
        else:
            value = lv[b["index"]]
            self.stack.append((lv, os + [value], pc + 1))
        self.merge_fwd(pc + 1, lv, os + [value])

    def _binary(self, b):
        (lv, os, pc) = self.stack.pop(-1)
        value = getattr(self.arithmeticOperation, "_"+b["operant"])(os[-2], os[-1])
        self.stack.append((lv, os[:-2] + [value], pc + 1))
        self.merge_fwd(pc + 1, lv, os[:-2] + [value])

    def _if(self, b):
        (lv, os, pc) = self.stack.pop(-1)
        condition = getattr(self.comparison, "_"+b["condition"])(os[-2], os[-1])
        if condition != "Maybe":
            if condition:
                pc = b["target"]
                self.merge_fwd( b["target"], lv, os[:-2])
            else:
                pc = pc + 1
                self.merge_fwd(pc, lv, os[:-2])
        else:
            lv_copy, os_copy = deep_copy_with_relationship(lv, os)
            os_copy[-1] = getattr(self.comparison, "_assert_"+b["condition"])(os_copy[-2], os_copy[-1])
            self.branch_list[pc] = (lv_copy, os_copy[:-2], b["target"])
            self.merge_fwd(b["target"], lv_copy, os_copy[:-2])

            opp = self.comparison._opposite(getattr(self.comparison, "_"+b["condition"]))
            os[-1] = getattr(self.comparison, "_assert_"+opp)(os[-2], os[-1])
            pc = pc + 1
            self.merge_fwd(pc, lv, os[:-2])

        self.stack.append((lv, os[:-2], pc))


    def _store(self, b):
        (lv, os, pc) = self.stack.pop(-1)
        value = os[-1]
        if b["index"] >= len(lv):
            lv = lv + [value]
        else:
            lv[b["index"]] = value
        self.stack.append((lv, os[:-1], pc + 1))
        self.merge_fwd(pc + 1, lv, os[:-1])

    def _goto(self, b):
        (lv, os, pc) = self.stack.pop(-1)
        value = b["target"]
        pc = value
        self.stack.append((lv, os, pc))
        self.merge_fwd(pc, lv, os)
        
    def _get(self, b):
        (lv, os, pc) = self.stack.pop(-1)
        if b["field"]["name"] == '$assertionsDisabled':
            value = self.cast(0)
        else:
            value = getattr(self.javaMethod, "_get")(b["field"])
        self.stack.append((lv, os + [value], pc + 1))
        self.merge_fwd(pc + 1, lv, os + [value])

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
                        self.merge_fwd(pc + 1, lv, os[:-arg_num-1] + [value])
                    else:
                        raise Exception
            elif b["access"] == "special" and b["method"]["ref"]["name"] == "java/lang/AssertionError":
                    self.stack.append((lv, os, pc))
            else:
                raise Exception
        except:
            pr = None
            for av_pr in self.avail_programs:
                if av_pr.endswith(b["method"]["name"]):
                    pr = av_pr
            if not pr:
                raise Exception("UnsupportedOperationException")

            interpret = self.__class__(self.avail_programs[pr], self.verbose, self.avail_programs)
            if arg_num == 0:
                (l_new, s_new, pc_new) = [], [], 0
            else:
                (l_new, s_new, pc_new) = os[-arg_num:], [], 0
            ret = interpret.run((l_new, s_new, pc_new))
            if b["method"]["returns"] == None:
                if arg_num == 0:
                    self.stack.append((lv, os, pc + 1))
                    self.merge_fwd(pc + 1, lv, os)
                else:
                    self.stack.append((lv, os[:-arg_num], pc + 1))
                    self.merge_fwd(pc + 1, lv, os[:-arg_num])
            else:
                if arg_num == 0:
                    self.stack.append((lv, os + [ret], pc + 1))
                    self.merge_fwd(pc + 1, lv, os + [ret])
                else:
                    self.stack.append((lv, os[:-arg_num] + [ret], pc + 1))
                    self.merge_fwd(pc + 1, lv, os[:-arg_num] + [ret])

    def _dup(self, b):
        (lv, os, pc) = self.stack.pop(-1)
        self.stack.append((lv, os + os[-b["words"]:], pc + 1))
        self.merge_fwd(pc + 1, lv, os + os[-b["words"]:])

    # TODO: classes are not implemented yet
    def _new(self, b):
        (lv, os, pc) = self.stack.pop(-1)
        self.stack.append((lv, os, pc + 1))
        self.merge_fwd(pc + 1, lv, os)

    def _return(self, b):
        (l, os, pc) = self.stack.pop(-1)
        self.stack.append((l, os[-1], pc+1))
        if b["type"] == None:
            return None
        elif b["type"] == "int":
            return os[-1]
