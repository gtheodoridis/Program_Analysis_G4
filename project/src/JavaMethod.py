class JavaMethod:
    def __init__(self):
        pass

    def _get(dict):
        if dict == {
            "class": "java/lang/System",
            "name": "out",
            "type": {
                "kind": "class",
                "name": "java/io/PrintStream"
            }
            }:
            return dict["type"]["name"]
        return None
    
    def _println(system, str):
        print(str)

    def _length(str):
        print("STRING IS:", str)
        return len(str)
    
    def _charAt(str, index):
        return ord(str[index])