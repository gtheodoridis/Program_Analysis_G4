import json
import glob
import subprocess
import pydot
from collections import namedtuple


def get_paths(folder_path):
    # This function takes a folder path as input and uses glob.glob to recursively find all JSON files within the specified folder and its subdirectories. It returns a list of file paths.
    return glob.glob(folder_path + '/**/*.json', recursive = True)

def find_keys(json_obj, depedencies=None, interfaces=None, fields=None, methods=None, compositions=None):
    # This function recursively traverses a JSON object representing Java class information and extracts various details, including dependencies, interfaces, fields, methods, and compositions.
    # It uses a set to keep track of each type of information.
    # The function handles nested structures within the JSON, such as inner classes and their relationships.
    if depedencies is None:
        depedencies = set()
    if interfaces is None:
        interfaces = set()
    if fields is None:
        fields = set()
    if methods is None:
        methods = set()
    if compositions is None:
        compositions = set()

    if isinstance(json_obj, dict):
        for key, value in json_obj.items():
            # Depedencies
            if key in ["type", "ref"]:
                if value:
                    if "name" in value and "/" in value["name"] and not value["name"] == "java/lang/Object":
                        depedencies.add(value["name"])
            # Interfaces
            if key == "interfaces":
                for interface in value:
                    interfaces.add(interface["name"])
            # Fields
            if key == "fields":
                for field in value:
                    try:
                        string = "- "
                        if "access" in field and field["access"]:
                            if "public" in field["access"]:
                                string = "+ "
                        string += field["name"] + ": "
                        if "name" in field["type"]:
                            string += field["type"]["name"].split("/")[-1]
                        else:
                            if "base" in field["type"]:
                                string += field["type"]["base"]
                        fields.add(string)
                    except:
                        pass
            # Methods
            if key == "methods":
                for method in value:
                    try:
                        string = "- "
                        if "public" in method["access"]:
                            string = "+ "
                        string += method["name"] + "(): "
                        if method["returns"]["type"]:
                            if "name" in method["returns"]["type"]:
                                string += method["returns"]["type"]["name"].split("/")[-1]
                            else:
                                if "base" in method["returns"]["type"]:
                                    string += method["returns"]["type"]["base"]
                        else:
                            string += "void"
                        methods.add(string)
                    except:
                        pass
            # Compositions
            if key == "innerclasses":
                for composition in value:
                    if composition["class"] == json_obj["name"]:
                        compositions.add(composition["outer"])
            find_keys(value, depedencies, interfaces, fields, methods, compositions)
    elif isinstance(json_obj, list):
        for item in json_obj:
            find_keys(item, depedencies, interfaces, fields, methods, compositions)
    
    return depedencies, interfaces, fields, methods, compositions

def analyse_bytecode(folder_path):
    # This function analyzes Java bytecode files (.class) using the jvm2json tool. It takes a folder path as input, finds all .class files in the specified folder and its subdirectories, and then uses the subprocess module to run the jvm2json tool to convert each .class file into a corresponding JSON file (.json).
    class_files = glob.glob(folder_path + '/**/*.class', recursive=True)
    for class_file in class_files:
        json_file = class_file.replace('.class', '.json')
        command = [
            "jvm2json",
            "-s", class_file,
            "-t", json_file
        ]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def draw_graph(classes):
    # Generates a class diagram using the extracted information and pydot.

    # Create a new UML diagram
    uml_diagram = pydot.Dot(graph_type='digraph', rankdir='TB')

    pydot_classes = {}

    for class_name, class_details in classes.items():
        # Create classes
        # Add attributes and methods to classes
        label = "<" + class_name + "<br align='left'/>--------<br/>"
        if 'fields' in class_details:
            for field in class_details['fields']:
                label += field.replace('<', '&lt;').replace('>', '&gt;') + "<br align='left'/>"
        if label[-5:] != "<br/>":
            label += "--------<br/>"
        if 'methods' in class_details:
            for method in class_details['methods']:
                label += method.replace('<', '&lt;').replace('>', '&gt;') + "<br align='left'/>"
        if label[-5:] == "<br/>":
            label = label[:-13]
        label += ">"

        class_node = pydot.Node(class_name, shape="rectangle", label=label)

        # Add classes to the diagram
        if class_node:
            uml_diagram.add_node(class_node)
            pydot_classes[class_name] = class_node

    for class_name, class_details in classes.items():
        if 'depedencies' in class_details:
            for dependency in class_details['depedencies']:
                association = pydot.Edge(pydot_classes[class_name], pydot_classes.get(dependency, dependency), arrowhead="vee")
                if association:
                    uml_diagram.add_edge(association)
        
        if 'interfaces' in class_details:
            for interface in class_details['interfaces']:
                association = pydot.Edge(pydot_classes[class_name], pydot_classes.get(interface, interface), arrowhead="onormal")
                if association:
                    uml_diagram.add_edge(association)
        
        if 'compositions' in class_details:
            for composition in class_details['compositions']:
                association = pydot.Edge(pydot_classes[class_name], pydot_classes.get(composition, composition), arrowhead="diamond")
                if association:
                    uml_diagram.add_edge(association)

    # Save the diagram to a file
    uml_diagram.write_png("class_diagram.png")


def main():
    folder_path = "../jpf-core-master/jpf-core-master/build/main/gov/nasa/jpf/search"
    analyse_bytecode(folder_path)
    paths = get_paths(folder_path)
    classes = {}
    for path in paths:
        with open(path, 'r') as file:
            json_obj = json.load(file)
            class_name = path[len(folder_path):].replace(".json", "")
            depedencies, interfaces, fields, methods, compositions = find_keys(json_obj)
            depedencies = depedencies - compositions
            depedencies = {item for item in depedencies if class_name not in item}
            depedencies = {item for item in depedencies if '$' not in item}
            interfaces = {item for item in interfaces if '$' not in item}
            fields = {item for item in fields if '$' not in item}
            methods = {item for item in methods if '$' not in item}
            classes[class_name] = {}
            classes[class_name]['depedencies'] = depedencies
            classes[class_name]['interfaces'] = interfaces
            classes[class_name]['fields'] = fields
            classes[class_name]['methods'] = methods
            classes[class_name]['compositions'] = compositions
            
    for key in classes.keys():
        for key2 in classes[key].keys():
            classes[key][key2] = {x for x in classes[key][key2] if x is not None}
    
    print(classes)
    draw_graph(classes)


if __name__ == "__main__":
    main()