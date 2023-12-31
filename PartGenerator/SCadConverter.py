import io
from abc import ABC, abstractmethod
import Request
import numpy as np
import Math3d

# parse through line by line
# build a tree
# Master: intersection, union, difference
# Subitems: requests or master

class CombinedRequest(ABC):
    def __init__(self, boolean_type: str, name: str):
        self.boolean_type = boolean_type
        self.base_request = None
        self.further_requests = [] # Request or CombiedRequest
        self.name = name

    def add_request(self, request: Request):
        if self.base_request is None:
            request.name = self.name
            self.base_request = request
        else:
            sub_name = self.name + str(len(self.further_requests))
            request.name = sub_name
        self.further_requests.append(request)


class UnionRequest(CombinedRequest):
    def __init__(self):
        pass



COMBINED_NAMES = ["union", "difference", "intersection"]
PRIMITIVE_NAMES = ["sphere", "cube", "cylinder"]
TRANSLATE = "translate"

# extracts name of function from line
def read_function_name_in_line(line: str):
    cleaned_line = line.strip()
    name_end = cleaned_line.find("(")
    if name_end == -1:
        return None
    return cleaned_line[:name_end]

def read_vector_from_text(text: str):
    start = text.find("[")
    end = text.find("]")
    cleaned_text = text[start + 1: end].replace(" ", "")
    numbers = cleaned_text.split(sep=",")
    array = []
    for i in numbers:
        array.append(float(i))
    return np.array(array)

# TODO vectors are separates by "," but so are arguments. need to concatenate for vectors
def read_arguments_in_line(line: str):
    start = line.find("(")
    end = line.find(")")
    cleaned_text = line[start + 1: end].replace(" ", "")
    arguments_split = cleaned_text.split(sep=",")

    # Here combine vector values together
    arguments_raw = []
    i = 0
    while i < len(arguments_split):
        token = arguments_split[i]
        if "[" in token:
            built_token = token
            while "]" not in token:
                i += 1
                token = arguments_split[i]
                built_token += "," + token
            arguments_raw.append(built_token)
        else:
            arguments_raw.append(token)
        i += 1

    # Separate into dictionary
    arguments = {}
    for raw_argument in arguments_raw:
        equals_ind = raw_argument.find("=")
        name = raw_argument[:equals_ind]

        value = raw_argument[equals_ind+1:]
        if value == "true":
            value = True
        elif value == "false":
            value = False
        elif "[" in value:
            value = read_vector_from_text(value)
        else:
            value = float(value)

        arguments[name] = value
    return arguments

def read_function_in_line(line: str):
    function_name = read_function_name_in_line(line)
    arguments = read_arguments_in_line(line)
    return function_name, arguments

# dictionary of function_name: arguments
# reads lines building a primitive until reach a ;
def read_primitive_functions(first_line: str, scad_file: io.TextIOWrapper) -> dict:
    functions = {}
    function_name, arguments = read_function_in_line(first_line)
    functions[function_name] = arguments
    while True:
        line = scad_file.readline()
        function_name, arguments = read_function_in_line(line)
        functions[function_name] = arguments
        if ";" in line:
            break

    return functions

def build_primitive_request(first_line: str, scad_file: io.TextIOWrapper):
    functions = read_primitive_functions(first_line, scad_file)
    function_names = functions.keys()

    # get rotate
    orientation = np.array([0.0, 0.0, 0.0])
    if "rotate" in function_names:
        orientation = functions["rotate"]
    axis = Math3d.orientation_to_axis(orientation)

    translation = np.array([0.0, 0.0, 0.0])
    if "translate" in function_names:
        translation = functions["translate"]

    if "sphere" in function_names:
        arguments = functions["sphere"]
        if arguments["r"] is not None:
            diameter = arguments["r"] * 2.0
        else:
            diameter = arguments["d"]
        return Request.Sphere(name="a",
                              origin=translation,
                              diameter=diameter,
                              boolean_type=Request.BooleanType.ADD)
    elif "cube" in function_names:
        arguments = functions["cube"]
        return Request.Prism(name="a",
                             boolean_type=Request.BooleanType.ADD,
                             dimensions=arguments["size"],
                             origin=translation,
                             origin_is_corner=not arguments["center"])
    elif "cylinder" in function_names:
        arguments = functions["cylinder"]
        # TODO: cones are not yet supported.
        if arguments["r"] is not None:
            diameter = arguments["r"] * 2.0
        else:
            diameter = arguments["d"]
        return Request.Hole(name="a",
                            boolean_type=Request.BooleanType.ADD,
                            axis=axis,
                            depth=arguments["h"],
                            origin=translation,
                            diameter=diameter)
    # end at ;
def build_combined_request(first_line: str, scad_file: io.TextIOWrapper):
    combined_name = read_function_name_in_line(first_line)
    combined_request = CombinedRequest(name="A", boolean_type=combined_name)
    while True: # Continue until reach "}"
        line = scad_file.readline()
        print(line)
        function_name = read_function_name_in_line(line)
        if function_name is not None:
            if function_name in COMBINED_NAMES:
                request = build_combined_request(first_line=line, scad_file=scad_file)
            else: # normal request
                request = build_primitive_request(first_line=line, scad_file=scad_file)
            combined_request.add_request(request)

        #case for empty line
        if "}" in line: # End of combined
            break
    return combined_request


def build_tree_from_scad(scad_file_name: str):
    with open(scad_file_name, "r") as f:
        first_line = f.readline()
        function_name = read_function_name_in_line(first_line)
        while function_name is None:
            first_line = f.readline()
            function_name = read_function_name_in_line(first_line)
        return build_combined_request(first_line, f)

def print_file_line(f):
    next_line = f.readline()
    print(next_line)

if __name__ == "__main__":
    # text = "translate([0, 0, 0])\n"
    # print(read_vector_from_text(text))

    filename = "cube.scad"
    combined_requset = build_tree_from_scad(filename)

    a = "sphere(r = 57, $fn = 12);"
    print(read_arguments_in_line(a))