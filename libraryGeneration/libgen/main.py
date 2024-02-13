import sys
import os
import json
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
import argparse
import shutil


def cmdlineParse():
    # Argument line parser initialisation.
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    # Parser argument control section.
    parser.add_argument("-o", "--outputdir",
                        help="Output directory.",
                        default="test")
    parser.add_argument("-l", "--libraryname",
                        help="Library name.",
                        default="stm32rustlib")
    parser.add_argument("-j", "--json",
                        help="JSON files to parse",
                        nargs='*',
                        default=[])
    parser.add_argument("-e", "--extra",
                        help="Additionnal files to be included in the library. Example: wait.rs",
                        nargs='*',
                        default=[])

    args = parser.parse_args()

    # Printing the input for DEBUG.
    print("Given arguments:\n- Output directory {}\n- Library name {}\n- JSON {}\n- Extra: {}\n".format(
            args.outputdir,
            args.libraryname,
            args.json,
            args.extra
            ))

    return args


def generate_data_from_json(json_file_path):
    try:
        with open(json_file_path, 'r') as json_file:
            json_data = json.load(json_file)
    except FileNotFoundError:
        print(f"Error: File '{json_file_path}' not found.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Unable to parse JSON in file '{json_file_path}'.")
        sys.exit(2)

    if json_data["exhaustive"]:
        data = {
            "exhaustive": 1,
            "components": [{"name": component["name"],
                            "address": component["address"],
                            "registers": [{"name": register["name"],
                                           "offset": register["offset"],
                                           "read": register["read"],
                                           "write": register["write"]}
                                           for register in component["registers"]]}
                            for component in json_data["components"]],
            "constants" : [{"name": constant["name"],    
                            "value": constant["value"] }
                               for  constant in json_data["constants"]]
            }
    else:
        data = {
            "exhaustive": 0,
            "components": [{"name": component["name"],
                            "address": component["address"]}
                            for component in json_data["components"]],
            "registers": [{"name": register["name"],
                           "offset": register["offset"],
                           "read": register["read"],
                           "write": register["write"]}
                           for register in json_data["registers"]],
            "constants" : [{"name": constant["name"],    
                            "value": constant["value"] }
                               for  constant in json_data["constants"]]
             }


    return data


def main():

    # Parse argument line
    args = cmdlineParse()
    output_dir_path = args.outputdir
    library_dir_path = os.path.join(args.outputdir,args.libraryname)

    # Initiate Jinja2 environment
    file_loader = FileSystemLoader('../templates/')
    env = Environment(loader=file_loader)

    # Create directory
    Path(library_dir_path).mkdir(parents=True, exist_ok=True)

    # Generate various.rs file (global variables used across the library)
    mod_file_path = os.path.join(output_dir_path, args.libraryname + ".rs")
    output_file_path = library_dir_path + "/various.rs"
    with open(output_file_path, 'w') as output_file:
        t = env.get_template("various.rs")
        output_file.write(t.render())
    with open(mod_file_path, 'w') as mod_file:
        mod_file.write("pub mod various;\n")

    # Debug
    print("{} generated.".format(output_file_path))

    # Generate all library files based on arguments
    for json_file_path in args.json:
        # Read JSON data
        data = generate_data_from_json(json_file_path)

        # Get the basename from JSON file name
        basename = os.path.splitext(os.path.basename(json_file_path))[0]

        # Generate library file
        output_file_path = library_dir_path+"/"+basename+".rs"
        with open(output_file_path, 'w') as output_file:
            # TODO: verify that the file exists
            # Generate corresponding template
            t = env.get_template(basename+".rs")
            output_file.write(t.render(data))

            print("{} generated.".format(output_file_path))
            
        with open(mod_file_path, 'a') as mod_file:
            mod_file.write("pub mod "+basename+";\n")
    
    for extra_file_path in args.extra:
        shutil.copy(extra_file_path, library_dir_path)

        # Get the basename from extra file name
        basename = os.path.splitext(os.path.basename(extra_file_path))[0]

        print("{} generated.".format(basename))
            
        with open(mod_file_path, 'a') as mod_file:
            mod_file.write("pub mod "+basename+";\n")

    # - s'inspirer de https://github.com/stm32-rs/stm32f4xx-hal pour
    #    avoir une idée de quelles sections faire par la suite


if __name__ == "__main__":
    main()
