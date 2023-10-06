class Comparison:
    def _eq(a, b):
        return a == b
    
    def _ne(a, b):
        return a != b
    
    def _lt(a, b):
        return a < b
    
    def _ge(a, b):
        return a >= b
    
    def _gt(a, b):
        return a > b

    def _le(a, b):
        return a <= b
    
    def _is(a, b):
        return a is b
    
    def _isnot(a, b):
        return a is not b
    

class AbstractRangeComparison:
    def _opposite(cond):
        if cond is AbstractRangeComparison._eq:
            return "eq"
        elif cond is AbstractRangeComparison._le:
            return "gt"

    def _eq(a, b):
        if a.end < b.start or b.end < a.start:
            return False
        elif a.start == a.end and b.start == b.end and a.start == b.start:
            return True
        return "Maybe"
    
    def _ne(a, b):
        result = AbstractRangeComparison._eq(a, b)
        return not result if isinstance(result, bool) else "Maybe"
    
    def _lt(a, b):
        if a.end < b.start:
            return True
        elif a.start >= b.end:
            return False
        return "Maybe"
    
    def _ge(a, b):
        result = AbstractRangeComparison._lt(a, b)
        return not result if isinstance(result, bool) else "Maybe"
    
    def _gt(a, b):
        if a.start > b.end:
            return True
        elif a.end <= b.start:
            return False
        return "Maybe"

    def _le(a, b):
        result = AbstractRangeComparison._gt(a, b)
        return not result if isinstance(result, bool) else "Maybe"
    
    def _is(a, b):
        # Identity check isn't meaningful for abstract values like ranges. 
        # It's more about checking if two references point to the same object in memory.
        # We can assume they are not the same for simplicity.
        return False
    
    def _isnot(a, b):
        # Opposite of `_is`
        return True
    
    def _assert_gt(a, b):
        if a.start > b.end:
            return a
        elif a.end < b.start:
            raise Exception("AssertionFailed")
        a.start = b.start + 1
        return a
    
    def _assert_le(a, b):
        if a.end < b.start:
            return a
        elif a.start > b.end:
            raise Exception("AssertionFailed")
        a.end = b.end
        return a
    
    def _assert_eq(a, b):
        if a.start > b.end:
            raise Exception("AssertionFailed")
        elif a.end < b.start:
            raise Exception("AssertionFailed")
        a.start = b.start
        a.end = b.end 
        return a