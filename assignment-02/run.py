from tree_sitter import Language, Parser


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
        return {node.text}


class ContextSensitive(SyntaxFold):
    def type_identifier(self, node, results):
        def ret(ids):
            if node.text in ids:
                return set()
            else:
                return {node.text}

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
    class_fields = {}
    class_methods = {}

    def classify_declaration(self, node, p, dic):
        if p.parent:
            p = p.parent
            if p.type == "class_body":
                if p.parent:
                    p = p.parent
                    if p.type == "class_declaration" and p.named_children:
                        for child in p.named_children:
                            if child.type == "identifier":
                                if child.text in dic:
                                    dic[child.text].append(node.text)
                                else:
                                    dic[child.text] = [node.text]

    def default(self, node, results):
        return set().union(*results)

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
                return {(node.text, p.start_byte, p.end_byte)}
        return set()


FILE = "./languages.so"  # the ./ is important
Language.build_library(FILE, ["tree-sitter-java"])
JAVA_LANGUAGE = Language(FILE, "java")

parser = Parser()
parser.set_language(JAVA_LANGUAGE)

with open(
    "/home/hollowman/Downloads/course-02242-examples/src/dependencies/java/dtu/deps/normal/Primes.java",
    "rb",
) as f:
    tree = parser.parse(f.read())

# the tree is now ready for analysing
print(ContextSensitive().visit(tree.root_node)(set()))
classes = ClassNames()
print(classes.visit(tree.root_node))
print(classes.class_fields)
print(classes.class_methods)
