#  Identifying Inputs Causing Crash using Input Tagging and Propagation
Fuzzing has gained popularity in recent years as a method of discovering vulnerabilities in software. The ability to identify the specific input that leads to crashes can significantly expedite the troubleshooting process and improve the overall robustness and security of software applications. This information can help in multiple directions, it can help the developer to debug and understand the issue faster, and it can also be used to guide fuzzers to mutate on the more interesting part of the input to find more vulnerabilities. Our solution aspires to bridge the gap between mere crash identification and precise root cause analysis, enhancing the robustness of software applications.

## Goal of the analysis
This dynamic analysis would accept a function, which could be the main function of the program, which can take some inputs. The purpose of our analysis would be to detect which specific inputs caused the program's crash.

## Acceptable input
Our analysis will only work on Java bytecode.

## Installation
1) Make sure python3 and JDK are already available on your machine.
2) Install [jvm2json](https://github.com/kalhauge/jvm2json), which is the tool for converting Java bytecode into JSON. Make sure it’s available in PATH since our program will use the binary to do the conversion automatically without any extra steps.
3) Compile the Java program in the byte code. In our test case, go to the examples folder and run javac *.java

## Usage
In order to use our analysis, you'll need to run the following command after installing the requirements.

```bash
python3 java-crash-input-reporter.py "/path/to/main/classfile.class" --folder_path "/path/to/folder" --folder_path_target "/path/to/target/folder" --memory_values "value1 value2"
```

The first argument is necessary; the rest are optional.

- For the first argument, you provide the address to the compiled class file of the Java code to be analysed.
- The `folder_path` argument will be the folder path of the bytecode of the Java program to be analysed.
- The `folder_path_target` argument will be the folder path of the resulting JSON of parsed bytecode of the Java program to be analysed.
- The `memory_values` argument will be the values in memory before the start of the main function. Here, these values would be the strings that are passed to the Java main function when executing the program.

An example command to run would be the following:

```bash
python3 java-crash-input-reporter.py "examples/IndirectUsageIf.class" --folder_path_target="examples/decompiled" --memory_values 1
```

## tests
In order to run the test simply go to the tests folder and run pytest tags.py to test the main functionalities of the project.
