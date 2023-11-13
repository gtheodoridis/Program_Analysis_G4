from JavaMethod import JavaMethod
from Comparison import Comparison

from BaseInterpreter import BaseInterpreter
from Logger import logger


class FailedTagException(Exception):
    def __init__(self, e, tags):
        self.tags = tags
        self.exc_type = e
        super().__init__(f"An exception of type {e} occured with tags: {tags}")

class TaggedValue():
    def __init__(self, value, tags = set()):
        self.value = value
        self.tags = tags

    def __str__(self):
        return "TV {} {}".format(self.value, self.tags)

    def __repr__(self):
        return self.__str__()

class TaggedInterpreter(BaseInterpreter):
    def __init__(self, program, avail_programs):
        super().__init__(program, avail_programs)

        self.comparison = Comparison 
        from ArithmeticOperation import ArithmeticOperation
        self.arithmeticOperation = ArithmeticOperation
        self.javaMethod = JavaMethod 
        self.functions = []
        self.if_conditions = []

        self.path = []
        self.new_arr_counter = 0
        self.push_counter = 0


    def run(self, f):
        (l, os, pc) = f
        for ind in range(len(l)):
            if not isinstance(l[ind], TaggedValue):
                l[ind] = TaggedValue(l[ind], {"LV{}".format(ind)})
        for ind in range(len(os)):
            if not isinstance(os[ind], TaggedValue):
                os[ind] = TaggedValue(os[ind], {"SV{}".format(ind)})

        for val in range(len(self.memory)):
            for ind in range(len(self.memory[val])):
                self.memory[val][ind] = TaggedValue(self.memory[val][ind], {"MVEL{}".format(ind)})
            self.memory[val] = TaggedValue(self.memory[val], {"MV{}".format(val)})

        ret = super().run(f)

        logger.debug(self.history)
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
                logger.error("Exception happened during " + str(self.history["last_opr"]))
                failed_tags = []

                for arg in self.history["last_opr"]["args"]:
                    for tag in arg.tags:
                        if not tag.startswith("PUSH") and not tag.startswith("ARR") and not tag.startswith("JAVA"):
                            failed_tags.append(tag)
                for cond in self.if_conditions:
                    tags = cond[0].tags.union(cond[2].tags)
                    for tag in tags:
                        if not tag.startswith("PUSH") and not tag.startswith("ARR") and not tag.startswith("JAVA"):
                            failed_tags.append(tag)
                raise FailedTagException(e, failed_tags) from None
        else:
            logger.error("Unknown instruction: " + str(b))
            raise Exception("UnsupportedOperationException")
        
    def log_history(self, f):
        (l, s, pc) = f
        self.history[pc] = (l, s)

    def _push(self, b):
        (l, os, pc) = self.stack.pop(-1)
        value = b["value"]
        tag = "PUSH{}".format(self.push_counter)
        self.push_counter += 1
        value = TaggedValue(value["value"], {tag})
        self.history["last_opr"] = {"opr_name":"_push", "args":[value]}
        self.stack.append((l, os + [value], pc + 1))
    
    def _incr(self, b):
        (lv, os, pc) = self.stack.pop(-1)
        self.history["last_opr"] = {"opr_name":"_incr",  "args":[lv[b["index"]]]}
        lv[b["index"]].value = lv[b["index"]].value + b["amount"]
        self.stack.append((lv, os, pc + 1))

    def _array_load(self, b):
        (lv, os, pc) = self.stack.pop(-1)
        self.history["last_opr"] = {"opr_name":"_array_load", "args":[os[-1]]}
        index_el = os[-1]

        index_array = os[-2]
        if index_el.value < 0 or index_el.value >= len(self.memory[index_array.value].value):
            raise Exception("IndexOutOfBoundsException")
        if index_array.value < 0 or index_array.value >= len(self.memory):
            raise Exception("NullPointerException")
        value = self.memory[index_array.value].value[index_el.value]
        self.stack.append((lv, os[:-2] + [value], pc + 1))

    def _array_store(self, b):
        # Store a value in an array
        (lv, os, pc) = self.stack.pop(-1)
        self.history["last_opr"] = {"opr_name":"_array_store", "args":[os[-1]]}
        value = os[-1]  # Value to store

        index_of_array = os[-3].value  # Index of the array to store in
        index_of_el = os[-2].value  # Index of the element in the array
        
        if index_of_el < 0 or index_of_el >= len(self.memory[index_of_array].value):
            raise Exception("IndexOutOfBoundsException")
        if index_of_array < 0 or index_of_array >= len(self.memory):
            raise Exception("NullPointerException")
        self.memory[index_of_array].value[index_of_el] = value  # Otherwise, update the existing element
        self.stack.append((lv, os[:-3], pc + 1))

    def _newarray(self, b):
        # Create a new array and store its index
        (lv, os, pc) = self.stack.pop(-1)
        self.history["last_opr"] = {"opr_name":"_arraylength", "args":[os[-1]]}
        size = os[-1].value

        # TODO: use dimension
        dim = b["dim"]
        tag = "ARR{}".format(self.new_arr_counter)
        value = [TaggedValue(None, ["ARREL{}".format(i)]) for i in range(size)]
        self.new_arr_counter += 1
        self.memory.append(TaggedValue(value, {tag}))  # Create a new empty array in memory
        self.stack.append((lv, os + [TaggedValue(len(self.memory)-1, {tag})], pc + 1))  # Store the index of the new array

    def _arraylength(self, b):
        # Get the length of an array
        (lv, os, pc) = self.stack.pop(-1)
        index_array = os[-1].value  # Index of the array
        self.history["last_opr"] = {"opr_name":"_arraylength", "args":[os[-1], self.memory[index_array]]}
        value = len(self.memory[index_array].value)  # Get the length of the array in memory
        value = TaggedValue(value, self.memory[index_array].tags) 
        self.stack.append((lv, os[:-1] + [value], pc + 1))

    def _if(self, b):
        (lv, os, pc) = self.stack.pop(-1)
        self.history["last_opr"] = {"opr_name":"_if", "condition":b["condition"], "args":[os[-2], os[-1]]}
        condition = getattr(self.comparison, "_"+b["condition"])(os[-2].value, os[-1].value)
        if condition:
            pc = b["target"]
            self.if_conditions.append((os[-2], b["condition"], os[-1]))
        else:
            pc = pc + 1
            self.if_conditions.append((os[-2], "not_"+b["condition"], os[-1]))
        self.stack.append((lv, os[:-2], pc))

    def _ifz(self, b): 
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

    def _binary(self, b):
        (lv, os, pc) = self.stack.pop(-1)
        self.history["last_opr"] = {"opr_name":"_binary", "operant":b["operant"], "args":[os[-2], os[-1]]}
        value = getattr(self.arithmeticOperation, "_"+b["operant"])(os[-2].value, os[-1].value)
        taggs = os[-2].tags.union(os[-1].tags)
        tagged_value = TaggedValue(value, taggs)
        self.stack.append((lv, os[:-2] + [tagged_value], pc + 1))

    def _get(self, b):
        (lv, os, pc) = self.stack.pop(-1)
        self.history["last_opr"] = {"opr_name":"_get"}
        value = getattr(self.javaMethod, "_get")(b["field"])
        self.stack.append((lv, os + [TaggedValue(value, {"JAVA"})], pc + 1))

    def _invoke(self, b):
        (lv, os, pc) = self.stack.pop(-1)
        arg_num = len(b["method"]["args"])

        if b["access"] == "virtual":
            arg_num += 1
            if hasattr(self.javaMethod, "_" + b["method"]["name"]):
                params = [i.value for i in os[-arg_num:]]
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
                self.stack.append((lv, os[:-arg_num-1] + [TaggedValue(value, taggs)], pc + 1))
            else:
                raise Exception
        elif b["access"] == "static":
            pr = None
            for av_pr in self.avail_programs:
                if av_pr.endswith(b["method"]["name"]):
                    pr = av_pr
            if not pr:
                raise Exception("UnsupportedOperationException")

            interpret = self.__class__(self.avail_programs[pr], self.avail_programs)
            if arg_num == 0:
                (l_new, s_new, pc_new) = [], [], 0
            else:
                (l_new, s_new, pc_new) = os[-arg_num:], [], 0
            self.history["last_opr"] = {"opr_name":"_invoke", "metho_name":b["method"]["name"], "args":[l_new, s_new]}
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

        self.functions.append((b["method"]["name"], b["method"]["args"], os[-arg_num:], b["method"]["returns"]))
        logger.info("Function calls stack: " + str(self.functions))

    def _negate(self, b):
        (lv, os, pc) = self.stack.pop(-1)
        os[-1].value = -os[-1].value 
        self.stack.append((lv, os, pc + 1))
