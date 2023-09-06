#!/usr/bin/env python3

from tree_sitter import Language, Parser
import glob
import pathlib
import pydot


def is_child_of(child_node, parent_node):
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
    def visit(self, node):
        results = [self.visit(n) for n in node.children]
        if hasattr(self, node.type):
            return getattr(self, node.type)(node, results)
        else:
            return self.default(node, results)


class TypeIdentifiers(SyntaxFold):
    def default(self, node, results):
        return set().union(*results)

    def type_identifier(self, node, results):
        return {node.text.decode()}


class ContextSensitive(SyntaxFold):
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
    package_name = ""
    class_fields = {}
    class_methods = {}
    class_imports = set()

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
        return set()


def get_paths(folder_path):
    return glob.glob(folder_path + "/**/*.java", recursive=True)


def analyse(paths):
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
        classNames.class_imports.clear()

    # Get dependencies
    for path in paths:
        with open(path, "rb") as f:
            tree = parser.parse(f.read())

        imports = ContextSensitive().visit(tree.root_node)(set())
        publicClassName = pathlib.Path(path).name.replace(".java", "")
        if publicClassName in imports:
            imports.remove(publicClassName)

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
                        else:
                            new_imports.add("java.lang." + _import)
                            
                dependencies[class_path] = list(new_imports)
                break

    return dependencies, fields, methods, classes


def draw_graph(dependencies, fields, methods, classes):

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
        label = "<" + class_name + "<br align='left'/>--------<br/>"
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
