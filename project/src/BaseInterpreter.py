from Logger import logger

class BaseInterpreter:
    def __init__(self, program, avail_programs):
        self.program = program
        self.avail_programs = avail_programs
        self.memory = []
        self.stack = []

        self.comparison = None
        self.arithmeticOperation = None
        self.javaMethod = None
        self._class = None

        self.history = {}

    def run(self, f):
        self.stack.append(f)
        self.log_start()
        self.log_state()
        while True:
            end_of_program, return_value = self.step()
            self.log_state()
            if return_value != None:
                logger.info("Program Returning: " + str(return_value))
                return return_value
            if end_of_program:
                break
        self.log_done()
        return None

    def step(self):
        if len(self.stack) == 0:
            return True, None
        (l, s, pc) = self.stack[-1]
        b = self.program['code']['bytecode'][pc]
        logger.info("Executing: " + str(b))
        if hasattr(self, "_"+b["opr"]):
            return False, getattr(self, "_"+b["opr"])(b)
        else:
            logger.info("Unknown instruction: " + str(b))
            raise Exception("UnsupportedOperationException")
    
    def log_start(self):
        logger.info("Starting execution...")
    
    def log_done(self):
        logger.info("Done.")
            
    def log_state(self):
        logger.info("Stack: " + str(self.stack))
        logger.info("Memory: " + str(self.memory))

    def _return(self, b):
        (l, os, pc) = self.stack.pop(-1)
        if b["type"] == None:
            self.history["last_opr"] = {"opr_name":"_return"}
            return None
        elif b["type"] == "int":
            self.history["last_opr"] = {"opr_name":"_return", "args":os[-1]}
            return os[-1]

    def _load(self, b):
        (lv, os, pc) = self.stack.pop(-1)
        self.history["last_opr"] = {"opr_name":"_load", "args":lv[b["index"]]}
        if b["type"] == "ref":
            value = lv[b["index"]]
            self.stack.append((lv, os + [value], pc + 1))
        else:
            value = lv[b["index"]]
            self.stack.append((lv, os + [value], pc + 1))

    def _binary(self, b):
        pass


    def _store(self, b):
        (lv, os, pc) = self.stack.pop(-1)
        self.history["last_opr"] = {"opr_name":"_store", "args":os[-1]}
        value = os[-1]
        if b["index"] >= len(lv):
            lv = lv + [value]
        else:
            lv[b["index"]] = value
        self.stack.append((lv, os[:-1], pc + 1))


    def _goto(self, b):
        (lv, os, pc) = self.stack.pop(-1)
        self.history["last_opr"] = {"opr_name":"_goto"}
        value = b["target"]
        pc = value
        self.stack.append((lv, os, pc))


    def _dup(self, b):
        (lv, os, pc) = self.stack.pop(-1)
        self.history["last_opr"] = {"opr_name":"_dup", "args":os[-b["words"]:]}
        self.stack.append((lv, os + os[-b["words"]:], pc + 1))

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

    def _invoke(self, b):
        pass

    def _get(self, b):
        pass

    def _if(self, b):
        pass

    def _ifz(self, b): 
        pass
