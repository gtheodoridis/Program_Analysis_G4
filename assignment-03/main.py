import json
import glob

def get_paths(folder_path):
    return glob.glob(folder_path + '/**/*.json', recursive = True)

def find_keys(json_obj, depedencies=None, interfaces=None):
    if depedencies is None:
        depedencies = set()
    if interfaces is None:
        interfaces = set()
    
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
            find_keys(value, depedencies, interfaces)
    elif isinstance(json_obj, list):
        for item in json_obj:
            find_keys(item, depedencies, interfaces)
    
    return depedencies, interfaces


def main():
    paths = get_paths("../course-02242-examples/src/dependencies/java/")
    for path in paths:
        with open(path, 'r') as file:
            json_obj = json.load(file)
            result = find_keys(json_obj)
            print(path, result)

            
            
if __name__ == "__main__":
    main()