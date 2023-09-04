from tree_sitter import Language, Parser

class SyntaxFold:

    def visit(self, node):
        results = [ self.visit(n) for n in node.children ]
        if hasattr(self, node.type):
            return getattr(self, node.type)(node, results)
        else:
            return self.default(node, results)

    def default(self, node):
        pass

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
    def default(self, node, results):
        return set().union(*results)


    # def class_declaration(self, node, results):
    #     class_name_node = [child for child in node.children if child.type == 'identifier']
    #     return {class_name_node[0].text}

    def identifier(self, node, results):
        if node.parent:
            if node.parent.type == 'class_declaration':
                return {node.text}
        return set()


FILE = "./languages.so" # the ./ is important
Language.build_library(FILE, ["tree-sitter-java"])
JAVA_LANGUAGE = Language(FILE, "java")

parser = Parser()
parser.set_language(JAVA_LANGUAGE)

with open("example-dependency-graphs/src/main/java/dtu/compute/simple/Example.java", "rb") as f:
    tree = parser.parse(f.read())

# the tree is now ready for analysing
print(ContextSensitive().visit(tree.root_node)(set()))
print(ClassNames().visit(tree.root_node))