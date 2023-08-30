# A source dependency graph tool, that can create graphs over a Java source code repository.

## Current output

$ python3 main.py /tmp/course-02242-examples
/tmp/course-02242-examples/src/dependencies/java/dtu/deps/simple/Other.java
['dtu.deps.util.Utils', 'java.lang.String']

/tmp/course-02242-examples/src/dependencies/java/dtu/deps/simple/Example.java
['java.lang.Other', 'dtu.deps.util.Utils', 'java.lang.String']

/tmp/course-02242-examples/src/dependencies/java/dtu/deps/util/Utils.java
['java.lang.System']

/tmp/course-02242-examples/src/dependencies/java/dtu/deps/normal/Primes.java
['java.lang.Iterable', 'java.lang.PrimesIterator', 'java.lang.String', 'java.util.ArrayList', 'java.util.List', 'java.lang.Integer', 'java.util.Iterator', 'java.lang.System']

/tmp/course-02242-examples/src/dependencies/java/dtu/deps/tricky/Tricky.java
['dtu.deps.simple.Other', 'java.lang.Utils', 'java.lang.Example', 'java.lang.Tricky']