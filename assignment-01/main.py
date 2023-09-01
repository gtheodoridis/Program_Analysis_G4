import glob
import sys
import re
import pathlib
import graphviz

def get_paths(folder_path):
    return glob.glob(folder_path + '/**/*.java', recursive = True)

def get_packages(pathes):
    packages = {}
    for path in pathes:
        with open(path, 'r') as file:
            text = file.read()
            package_name = re.findall(r"(?:package )([a-z.]+)", text)[0]

            class_name = pathlib.Path(path).name.replace('.java', '')
            
            try:
                packages[package_name].append(class_name)
            except:
                packages[package_name] = [class_name]

    return packages

def remove_comments(text):
    oneline = re.compile(r"\/\/.*")
    multiline = re.compile(r"\/\*[\s\S]*?\*\/")
    return re.sub(multiline, '', re.sub(oneline, '', text))


def get_imports(text, packages, current_package_name):
    classes_pattern = re.compile(r"(?:[^\w@])(([a-z.]+\.)?\*?([A-Z]{1}[a-zA-Z]+))(?:(?:\()|(?: [A-Za-z])|(?:))")
    inside_classes_pattern = re.compile(r"(?:class )([A-Z]{1}[a-zA-Z]+)")

    all_classes = re.findall(classes_pattern, text)
    inside_classes = re.findall(inside_classes_pattern, text)
    
    all_imports = [i[0] for i in all_classes]
    all_imports = list(set(all_imports)-set(inside_classes))

    for _import in all_imports:
        if '*' in _import:
            package = _import.replace('.*', '')
            all_imports.remove(_import)

            for _class in packages[package]:
                all_imports.append(package + '.' + _class)

    all_imports = list(set(all_imports))

    result_dependencies = []
    for _import in all_imports:
        if len([i for i in all_imports if _import in i]) == 1:
            if '.' in _import:
                result_dependencies.append(_import)
            else:
                if _import in packages[current_package_name]:
                    result_dependencies.append(current_package_name+'.'+_import)
                else:
                    result_dependencies.append('java.lang.'+_import)

    return result_dependencies


def get_dependencies(paths, packages):

    dependencies = {}

    for path in paths:
        with open(path, 'r') as file:

            text = file.read()
            no_comments = remove_comments(text)

            current_package_name = ''
            with open(path, 'r') as file:
                text = file.read()
                current_package_name = re.findall(r"(?:package )([a-z.]+)", text)[0]

            imports = get_imports(no_comments, packages, current_package_name)
            try:
                imports.remove(pathlib.Path(path).name.replace('.java', ''))
            except:
                pass

        for name in packages:
            className = pathlib.Path(path).name.replace('.java', '')
            if className in packages[name]:
                dependencies[name + '.' + className] = imports
                break
        

    return dependencies

def draw_graph(dependencies):
    dot = graphviz.Digraph(comment='Dependencies')
    for key in dependencies.keys():
        for value in dependencies[key]:
            dot.edge(key, value)
    dot.render('dependencies.gv', view=True)

def main():
    args = sys.argv[1:]
    if len(args) != 1:
        exit('You should provide a path to a folder')
        
    paths = get_paths(args[0])
    packages = get_packages(paths)
    dependencies = get_dependencies(paths, packages)
    draw_graph(dependencies)
    print(dependencies)
    

if __name__ == "__main__":
    main()

