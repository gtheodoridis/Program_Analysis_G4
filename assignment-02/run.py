#!/usr/bin/env python3

from tree_sitter import Language, Parser
import glob
import pathlib
import pydot
from collections import namedtuple


def is_child_of(child_node, parent_node):
    # Checks if one node is a child of another node in the syntax tree.
    # Get the start and end positions of the parent and child nodes.
    child_start = child_node.start_byte
    child_end = child_node.end_byte
    parent_start = parent_node.start_byte
    parent_end = parent_node.end_byte

    # Check if child_node is within the boundaries of parent_node.
    if child_start >= parent_start and child_end <= parent_end:
        return True

    return False


class SyntaxFold:
     # A base class for folding over the syntax tree.
    def visit(self, node):
        results = [self.visit(n) for n in node.children]
        if hasattr(self, node.type):
            return getattr(self, node.type)(node, results)
        else:
            return self.default(node, results)


class TypeIdentifiers(SyntaxFold):
    # A class for extracting type identifiers from the syntax tree.
    def default(self, node, results):
        return set().union(*results)

    def type_identifier(self, node, results):
        return {node.text.decode()}


class ContextSensitive(SyntaxFold):
    # A class for handling context-sensitive analysis of the syntax tree.
    def type_identifier(self, node, results):
        def ret(ids):
            if node.text.decode() in ids:
                return set()
            else:
                return {node.text.decode()}

        return ret

    def default(self, node, results):
        def ret(ids):
            return set().union(*[r(ids) for r in results])

        return ret

    def method_declaration(self, node, results):
        tp = node.child_by_field_name("type_parameters")
        if tp is None:
            return self.default(node, results)
        else:
            nids = TypeIdentifiers().visit(tp)

        def ret(ids):
            return self.default(node, results)(ids | nids)

        return ret


class ClassNames(SyntaxFold):
    # A class for extracting class names, fields, and methods from the syntax tree.
    package_name = ""
    class_fields = {}
    class_methods = {}
    class_imports = set()
    class_fields_access = set()

    def classify_declaration(self, node, p, dic):
        if p.parent:
            p = p.parent
            if p.type == "class_body":
                if p.parent:
                    p = p.parent
                    if p.type == "class_declaration" and p.named_children:
                        for child in p.named_children:
                            if child.type == "identifier":
                                class_path = (
                                    self.package_name + "." + child.text.decode()
                                )
                                if class_path in dic:
                                    dic[class_path].append(node.text.decode())
                                else:
                                    dic[class_path] = [node.text.decode()]

    def default(self, node, results):
        return set().union(*results)

    def package_declaration(self, node, results):
        for child in node.named_children:
            if child.type == "scoped_identifier":
                self.package_name = child.text.decode()
                break
        return set()

    def import_declaration(self, node, results):
        for child in node.named_children:
            if child.type == "scoped_identifier":
                import_path = child.text.decode()
                if child.next_sibling and child.next_sibling.type == ".":
                    import_path += ".*"
                self.class_imports.add(import_path)
                break
        return set()

    def identifier(self, node, results):
        if node.parent:
            p = node.parent
            if p.type == "variable_declarator":
                if p.parent:
                    p = p.parent
                    if p.type == "field_declaration":
                        self.classify_declaration(node, p, self.class_fields)
            elif p.type == "method_declaration":
                self.classify_declaration(node, p, self.class_methods)
            elif p.type == "class_declaration":
                return {
                    (
                        self.package_name + "." + node.text.decode(),
                        p.start_byte,
                        p.end_byte,
                    )
                }
            elif p.type == "method_invocation":
                text = p.text.decode()
                text = text.split('.')[:-1]

                imp = []
                flag = False
                for el in text:
                    imp.append(el)
                    if el[0].isupper():
                        flag = True
                        break
                
                if flag:
                    text = '.'.join(imp)

                    if len(imp)>0:
                        self.class_fields_access.add(text)
        return set()


def get_paths(folder_path):
    # Retrieves a list of file paths for Java source code files in a folder.
    return glob.glob(folder_path + "/**/*.java", recursive=True)


def analyse(paths):
    # Analyzes Java source code files to extract dependencies, fields, methods, and classes.
    dependencies = {}
    fields = {}
    methods = {}
    classes = set()

    FILE = "./languages.so"  # the ./ is important
    Language.build_library(FILE, ["../tree-sitter-java"])
    JAVA_LANGUAGE = Language(FILE, "java")

    parser = Parser()
    parser.set_language(JAVA_LANGUAGE)

    packages = {}
    class_imports = {}
    class_fields_access = {}

    # Get class information
    for path in paths:
        with open(path, "rb") as f:
            tree = parser.parse(f.read())

        # the tree is now ready for analysing
        classNames = ClassNames()
        classes.update(classNames.visit(tree.root_node))
        fields.update(classNames.class_fields)
        methods.update(classNames.class_methods)

        publicClassName = pathlib.Path(path).name.replace(".java", "")

        if classNames.package_name in packages:
            packages[classNames.package_name].append(publicClassName)
        else:
            packages[classNames.package_name] = [publicClassName]

        new_set = set()
        new_set.update(classNames.class_imports)
        class_imports[classNames.package_name + "." + publicClassName] =  new_set
        new_fields_access = set()
        new_fields_access.update(classNames.class_fields_access)
        class_fields_access[classNames.package_name + "." + publicClassName] = new_fields_access

        classNames.class_imports.clear()
        classNames.class_fields_access.clear()

    # Get dependencies
    for path in paths:
        with open(path, "rb") as f:
            tree = parser.parse(f.read())

        imports = ContextSensitive().visit(tree.root_node)(set())
        publicClassName = pathlib.Path(path).name.replace(".java", "")
        if publicClassName in imports:
            imports.remove(publicClassName)

        list_of_imports_to_remove = []
        for _import in imports:
            for className in classes:
                if className[0].endswith("." + _import):
                    for parentClassName in classes:
                        if parentClassName[0].endswith("." + publicClassName):
                            Node = namedtuple('Node', ['name', 'start_byte', 'end_byte'])
                            parent_node = Node(parentClassName[0], parentClassName[1], parentClassName[2])
                            child_node = Node(className[0], className[1], className[2])
                            if is_child_of(child_node, parent_node):
                                if parentClassName[0].rsplit('.', 1)[0] == className[0].rsplit('.', 1)[0]:
                                    list_of_imports_to_remove.append(_import)
        for _import in list_of_imports_to_remove:
            imports.remove(_import)
            break
        

        for name in packages:
            className = pathlib.Path(path).name.replace(".java", "")
            if className in packages[name]:
                class_path = name + "." + className
                new_class_imports = set()
                new_class_imports.update(class_imports[class_path])

                for class_import in class_imports[class_path]:
                    if class_import.endswith(".*"):
                        new_class_imports.remove(class_import)
                        for cn in packages[class_import.replace(".*", "")]:
                            new_class_imports.add(class_import.replace(".*", "") + "." + cn)
                class_imports[class_path] = new_class_imports
                
                new_imports = set()                
                imports = imports.union(set(class_fields_access[class_path]))
                for _import in imports:
                    is_imported = False

                    for class_import in new_class_imports:
                        if class_import.endswith("." + _import):
                            new_imports.add(class_import)
                            is_imported = True
                            break
                    if not is_imported:
                        if _import in packages[name]:
                            new_imports.add(name + "." + _import)
                        elif _import[0].isupper():
                            new_imports.add("java.lang." + _import)
                        else:
                            new_imports.add(_import)
                            
                dependencies[class_path] = list(new_imports)
                # dependencies[class_path].extend(class_fields_access[class_path])
                break

    return dependencies, fields, methods, classes


def draw_graph(dependencies, fields, methods, classes):
    # Generates a class diagram using the extracted information and pydot.

    nested_classes = []
    for value1 in classes:
        for value2 in classes:
            if value1 != value2 and value1[0].rsplit('.', 1)[0] == value2[0].rsplit('.', 1)[0]:
                Node = namedtuple('Node', ['name', 'start_byte', 'end_byte'])
                node1 = Node(value1[0], value1[1], value1[2])
                node2 = Node(value2[0], value2[1], value2[2])
                if is_child_of(node1, node2):
                    nested_classes.append((value1[0], value2[0]))
    
    # Create a new UML diagram
    uml_diagram = pydot.Dot(graph_type='digraph', rankdir='TB')

    # Collect all classes
    all_classes = set(map(lambda x: x[0], classes))
    all_classes.update(dependencies.keys())
    for key in dependencies.keys():
        for value in dependencies[key]:
            all_classes.add(value)
    all_classes.update(fields.keys())
    all_classes.update(methods.keys())

    pydot_classes = {}

    for class_name in all_classes:
        # Create classes
        # Add attributes and methods to classes
        label = ""
        nested_class_found = False
        for nested_class in nested_classes:
            if nested_class[0] == class_name:
                nested_class_name = nested_class[0].rsplit('.', 1)[-1]
                nested_class_name = nested_class[1] + '.' + nested_class_name
                label += "<" + nested_class_name + "<br align='left'/>--------<br/>"
                nested_class_found = True
                break
        if not nested_class_found:
            label += "<" + class_name + "<br align='left'/>--------<br/>"
        if class_name in fields:
            for field in fields[class_name]:
                label += "+ " + field + "<br align='left'/>"
        if label[-5:] != "<br/>":
            label += "--------<br/>"
        if class_name in methods:
            for method in methods[class_name]:
                label += "+ " + method + "()<br align='left'/>"
        if label[-5:] == "<br/>":
            label = label[:-13]
        label += ">"

        class1 = pydot.Node(class_name, shape="rectangle", label = label)

        # Add classes to the diagram
        uml_diagram.add_node(class1)
        pydot_classes[class_name] = class1

    for key in dependencies.keys():
        for value in dependencies[key]:
            # Create associations between classes
            association = pydot.Edge(pydot_classes[key], pydot_classes[value])
            uml_diagram.add_edge(association)

    for nested_class in nested_classes:
        association = pydot.Edge(pydot_classes[nested_class[0]], pydot_classes[nested_class[1]])
        uml_diagram.add_edge(association)

    # Save the diagram to a file
    uml_diagram.write_png("class_diagram.png")


def main():
    # import sys
    # args = sys.argv[1:]
    # if len(args) != 1:
    #     exit("You should provide a path to a folder")

    # paths = get_paths(args[0])
    paths = get_paths("../course-02242-examples/src/dependencies/java/dtu/deps")
    dependencies, fields, methods, classes = analyse(paths)
    draw_graph(dependencies, fields, methods, classes)
    print(dependencies)
    print(fields)
    print(methods)
    print(classes)


if __name__ == "__main__":
    main()