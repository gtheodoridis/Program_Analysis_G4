from JavaMethod import JavaMethod
from Comparison import Comparison

from BaseInterpreter import BaseInterpreter
from Logger import logger

import traceback

class FailedTagException(Exception):
    def __init__(self, e, tags):
        self.tags = tags
        self.exc_type = e
        super().__init__(f"An exception of type {e} occured with tags: {tags}")

class TaggedValue():
    def __init__(self, value, tags = []):
        self.value = value
        self.tags = tags


    def __str__(self):
        return "TV {} {}".format(self.value, self.tags)

    def __repr__(self):
        return self.__str__()
    
    def _get(self):
        return self.value

class TaggedInterpreter(BaseInterpreter):
    def __init__(self, program, avail_programs):
        super().__init__(program, avail_programs)

        # Assign classes to attributes for later use
        self.comparison = Comparison  # Assigning the AbstractRangeComparison class to self.comparison
        from ArithmeticOperation import ArithmeticOperation
        self.arithmeticOperation = ArithmeticOperation  # Assigning the AbstractRangeArithmeticOperation class to self.arithmeticOperation
        self.javaMethod = JavaMethod  # Assigning the AbstractRangeJavaMethod class to self.javaMethod
        self._class = TaggedValue
        self.functions = []
        self.if_conditions = []

        self.path = []
        self.new_arr_counter = 0
        self.push_counter = 0


    def run(self, f):
        (l, os, pc) = f
        for ind in range(len(l)):
            if not isinstance(l[ind], TaggedValue):
                l[ind] = self._class(l[ind], ["LV{}".format(ind)])
        for ind in range(len(os)):
            if not isinstance(os[ind], TaggedValue):
                os[ind] = self._class(os[ind], ["SV{}".format(ind)])

        for val in range(len(self.memory)):
            for ind in range(len(self.memory[val])):
                self.memory[val][ind] = self._class(self.memory[val][ind], ["MVEL{}".format(ind)])
            self.memory[val] = TaggedValue(self.memory[val], ["MV{}".format(val)])

        ret = super().run(f)

        logger.info(self.history)
        if ret:
            return ret

    def step(self):
        if len(self.stack) == 0:
            return True, None
        (l, s, pc) = self.stack[-1]
        b = self.program['code']['bytecode'][pc]
        logger.info("Executing: " + str(b))

        self.log_history((l, s, pc))

        if hasattr(self, "_"+b["opr"]):
            try:
                return False, getattr(self, "_"+b["opr"])(b)
            except FailedTagException as e:
                raise e
            except Exception as e:
                logger.error("smths wrong")
                print("last_opr", self.history["last_opr"])
                # flag = False
                failed_tags = []

                for arg in self.history["last_opr"]["args"]:
                    print("arg", arg.tags)
                    for tag in arg.tags:
                        if not tag.startswith("PUSH") and not tag.startswith("ARR") and not tag.startswith("JAVA"):
                            failed_tags.append(tag)
                            # print("This input Tag caused the program to crash:", tag)
                            # flag = True
                # if not flag:
                for cond in self.if_conditions:
                    for tag in cond[0].tags + cond[2].tags:
                        if not tag.startswith("PUSH") and not tag.startswith("ARR") and not tag.startswith("JAVA"):
                            failed_tags.append(tag)
                            # print("This input Tag caused the program to crash:", tag)
                            flag = True
                raise FailedTagException(e, failed_tags) from None
                return True, None
        else:
            logger.error("Unknown instruction: " + str(b))
            raise Exception("UnsupportedOperationException")
            return True, None
        
    def log_history(self, f):
        (l, s, pc) = f
        self.history[pc] = (l, s)

    # def run(self, f):
    #     # self.stack.append(f)
    #     self.log_start()
    #     self.log_state()

    #     # params = [z3.Int(f"p{i}") for i, _ in enumerate(self.program['code']['params'])]

    #     # self.program = self.program['code']

    #     while self.solver.check() == z3.sat:
    #         self.path = []
    #         model = self.solver.model()
    #         input = [model.eval(p, model_completion=True).as_long() for p in params]
    #         conc_input = [ConcolicValue(i[0], i[1]) for i in zip(input, params)]
            

    #         _f = conc_input, [], 0
    #         self.stack.append(_f)
    #         while True:
    #             try:
    #                 end_of_program, return_value = self.step()
    #             except Exception as e:
    #                 logger.error(e)
    #                 break

    #             self.log_state()
    #             if return_value != None:
    #                 logger.info("Program Returning: " + str(return_value))
    #                 return return_value
    #             if end_of_program:
    #                 break
            
    #         logger.info(self.path)

    #         path_constraint = z3.simplify(z3.And(*self.path))
    #         self.solver.add(z3.Not(path_constraint))
    
    #     self.log_done()
    #     return None

    def _push(self, b):
        (l, os, pc) = self.stack.pop(-1)
        value = b["value"]
        tag = "PUSH{}".format(self.push_counter)
        self.push_counter += 1
        value = TaggedValue(value["value"], [tag])  # Create a new RangeSet object with the value as both start and end
        self.history["last_opr"] = {"opr_name":"_push", "args":[value]}
        self.stack.append((l, os + [value], pc + 1))
    
    def _incr(self, b):
        # Increment the value in an array by a specified amount
        (lv, os, pc) = self.stack.pop(-1)
        self.history["last_opr"] = {"opr_name":"_incr",  "args":[lv[b["index"]]]}
        lv[b["index"]].value = lv[b["index"]].value + b["amount"]
        self.stack.append((lv, os, pc + 1))

    def _array_load(self, b):
        # Load a value from an array
        (lv, os, pc) = self.stack.pop(-1)
        self.history["last_opr"] = {"opr_name":"_array_load", "args":[os[-1]]}
        index_el = os[-1]  # Index of the element to load

        # index_array is assumed to not be a range but an integer
        index_array = os[-2]  # Index of the array
        if self._class._get(index_el) < 0 or self._class._get(index_el) >= len(self._class._get(self.memory[self._class._get(index_array)])):
            raise Exception("IndexOutOfBoundsException")
        if self._class._get(index_array) < 0 or self._class._get(index_array) >= len(self.memory):
            raise Exception("NullPointerException")
        value = self._class._get(self.memory[self._class._get(index_array)])[self._class._get(index_el)]  # Get the value from memory
        self.stack.append((lv, os[:-2] + [value], pc + 1))

    def _array_store(self, b):
        # Store a value in an array
        (lv, os, pc) = self.stack.pop(-1)
        self.history["last_opr"] = {"opr_name":"_array_store", "args":[os[-1]]}
        value = os[-1]  # Value to store
        # index_array is assumed to not be a range but an integer
        index_of_array = self._class._get(os[-3])  # Index of the array to store in
        index_of_el = self._class._get(os[-2])  # Index of the element in the array
        
        if index_of_el < 0 or index_of_el >= len(self._class._get(self.memory[index_of_array])):
            raise Exception("IndexOutOfBoundsException")
        if index_of_array < 0 or index_of_array >= len(self.memory):
            raise Exception("NullPointerException")
        self._class._get(self.memory[index_of_array])[index_of_el] = value  # Otherwise, update the existing element
        self.stack.append((lv, os[:-3], pc + 1))

    def _newarray(self, b):
        # Create a new array and store its index
        (lv, os, pc) = self.stack.pop(-1)
        self.history["last_opr"] = {"opr_name":"_arraylength", "args":[os[-1]]}
        size = self._class._get(os[-1])

        # TODO: use dimension
        dim = b["dim"]
        tag = "ARR{}".format(self.new_arr_counter)
        value = [TaggedValue(None, ["ARREL{}".format(i)]) for i in range(size)]
        self.new_arr_counter += 1
        self.memory.append(TaggedValue(value, [tag]))  # Create a new empty array in memory
        self.stack.append((lv, os + [TaggedValue(len(self.memory)-1, [tag])], pc + 1))  # Store the index of the new array

    def _arraylength(self, b):
        # Get the length of an array
        (lv, os, pc) = self.stack.pop(-1)
        index_array = self._class._get(os[-1])  # Index of the array
        self.history["last_opr"] = {"opr_name":"_arraylength", "args":[os[-1], self.memory[index_array]]}
        value = len(self.memory[index_array].value)  # Get the length of the array in memory
        print("arraylength", value)
        print("arraylength", self.memory[index_array].tags)
        value = TaggedValue(value, self.memory[index_array].tags)  # Create a new RangeSet object with the value as both start and end
        self.stack.append((lv, os[:-1] + [value], pc + 1))

    def _if(self, b):
        (lv, os, pc) = self.stack.pop(-1)
        self.history["last_opr"] = {"opr_name":"_if", "condition":b["condition"], "args":[os[-2], os[-1]]}
        condition = getattr(self.comparison, "_"+b["condition"])(os[-2].value, os[-1].value)
        print("###########",condition)
        if condition:
            pc = b["target"]
            self.if_conditions.append((os[-2], b["condition"], os[-1]))
        else:
            pc = pc + 1
            self.if_conditions.append((os[-2], "not_"+b["condition"], os[-1]))
        taggs = os[-2].tags + os[-1].tags
        self.stack.append((lv, os[:-2], pc))
        # self.if_conditions.append((os[-2].value, b["condition"], os[-1].value))
        # logger.info("if conditions stack: " + str(self.if_conditions))

    def _ifz(self, b): # maybe we remove later
        (lv, os, pc) = self.stack.pop(-1)
        self.history["last_opr"] = {"opr_name":"_ifz", "condition":b["condition"], "args":[os[-1]]}
        zero = TaggedValue(0)
        condition = getattr(self.comparison, "_"+b["condition"])(os[-1].value, zero.value)
        if condition:
            pc = b["target"]
            self.if_conditions.append((os[-1], b["condition"], zero))
        else:
            pc = pc + 1
            self.if_conditions.append((os[-1], "not_"+b["condition"], zero))
        self.stack.append((lv, os[:-1], pc))
        # self.if_conditions.append((os[-1].value, b["condition"], TaggedValue(0)))
        # logger.info("if conditions stack: " + str(self.if_conditions))

    def _binary(self, b):
        (lv, os, pc) = self.stack.pop(-1)
        self.history["last_opr"] = {"opr_name":"_binary", "operant":b["operant"], "args":[os[-2], os[-1]]}
        value = getattr(self.arithmeticOperation, "_"+b["operant"])(os[-2].value, os[-1].value)
        taggs = os[-2].tags + os[-1].tags
        tagged_value = TaggedValue(value, taggs)
        self.stack.append((lv, os[:-2] + [tagged_value], pc + 1))

    def _get(self, b):
        (lv, os, pc) = self.stack.pop(-1)
        self.history["last_opr"] = {"opr_name":"_get"}
        value = getattr(self.javaMethod, "_get")(b["field"])
        self.stack.append((lv, os + [TaggedValue(value, ["JAVA"])], pc + 1))

    def _invoke(self, b):
        (lv, os, pc) = self.stack.pop(-1)
        arg_num = len(b["method"]["args"])

        if b["access"] == "virtual":
            arg_num += 1
            if hasattr(self.javaMethod, "_" + b["method"]["name"]):
                # if arg_num == 0:
                    # value = getattr(self.javaMethod, "_" + b["method"]["name"])([])
                # else:    
                params = [self._class._get(i) for i in os[-arg_num:]]
                print(params)
                self.history["last_opr"] = {"opr_name":"_invoke", "method_name":b["method"]["name"], "args":os[-arg_num:]}
                value = getattr(self.javaMethod, "_" + b["method"]["name"])(*params)
                # if b["method"]["name"] == "println":
                #     if b["method"]["ref"]["name"] == os[-arg_num-1]:
                #         self.stack.append((lv, os[:-arg_num-1] + [value], pc + 1))
                #     else:
                #         raise Exception
                taggs = []
                for arg in os[-arg_num:]:
                    taggs.extend(arg.tags)
                self.stack.append((lv, os[:-arg_num-1] + [self._class(value, taggs)], pc + 1))
            else:
                raise Exception
        elif b["access"] == "static":
            pr = None
            for av_pr in self.avail_programs:
                if av_pr.endswith(b["method"]["name"]):
                    pr = av_pr
            if not pr:
                raise Exception("UnsupportedOperationException")
            
            # if b["method"]["name"] not in self.avail_programs:
            #     raise Exception("UnsupportedOperationException")

            interpret = self.__class__(self.avail_programs[pr], self.avail_programs)
            if arg_num == 0:
                (l_new, s_new, pc_new) = [], [], 0
            else:
                (l_new, s_new, pc_new) = os[-arg_num:], [], 0
            self.history["last_opr"] = {"opr_name":"_invoke", "metho_name":b["method"]["name"], "args":[l_new, s_new]}
            print(interpret)
            ret = interpret.run((l_new, s_new, pc_new))
            print(ret)
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

        self.functions.append((b["method"]["name"], b["method"]["args"], os[-arg_num:], b["method"]["returns"]))
        logger.info("Function calls stack: " + str(self.functions))

    def _negate(self, b):
        (lv, os, pc) = self.stack.pop(-1)
        os[-1].value = -os[-1].value 
        self.stack.append((lv, os, pc + 1))
