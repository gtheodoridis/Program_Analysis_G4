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
        return RangeSet(a.start - b.start, a.end - b.end)
    
    def _div(a, b):
        # Need to handle the case where b contains zero. Here, for simplicity, let's assume b doesn't contain zero.
        quotients = [a.start // b.start, a.start // b.end, a.end // b.start, a.end // b.end]
        return RangeSet(min(quotients), max(quotients))
    
    def _mod(a, b):
        # The modulus result will be in the range [0, b.end), assuming b doesn't contain 0 and b.start >= 0.
        return RangeSet(0, b.end - 1)
