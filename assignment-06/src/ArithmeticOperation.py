from AbstractRangeInterpreter import RangeSet

class ArithmeticOperation:
    def _add(a, b):
        return a + b
    
    def _mul(a, b):
        return a * b
    
    def _sub(a, b):
        return a - b
    
    def _div(a, b):
        return a // b
    
    def _mod(a, b):
        return a % b
    

class AbstractRangeArithmeticOperation:
    def _add(a, b):
        return RangeSet(a.start + b.start, a.end + b.end)
    
    def _mul(a, b):
        products = [a.start * b.start, a.start * b.end, a.end * b.start, a.end * b.end]
        return RangeSet(min(products), max(products))
    
    def _sub(a, b):
        return RangeSet(a.start - b.end, a.end - b.start)
    
    def _div(a, b):
        print(a, b)
        if b.start <= 0 and b.end >= 0:
            raise Exception("ArithmeticException")
        quotients = [a.start // b.start, a.start // b.end, a.end // b.start, a.end // b.end]
        return RangeSet(min(quotients), max(quotients))
    
    def _mod(a, b):
        if b.start <= 0 and b.end >= 0:
            raise Exception("ArithmeticException")
        # return RangeSet(0, max(abs(b.end, b.start)) - 1)
        if b.start > 0:
            return RangeSet(0, b.end - 1)
        elif b.end > 0:
            return RangeSet(b.start + 1, b.end - 1)
        elif b.end < 0:
            return RangeSet((-1)*max(abs(b.end, b.start)) - 1, 0)

