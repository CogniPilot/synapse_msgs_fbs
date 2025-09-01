import argparse
import os
import re

# Mapping from ROS primitive types to FlatBuffers scalar types.
# ROS `char` is a special case, treated as `uint8`.
ROS_TO_FBS_TYPE_MAP = {
    'bool': 'bool',
    'byte': 'byte',
    'char': 'ubyte',
    'int8': 'byte',
    'uint8': 'ubyte',
    'int16': 'short',
    'uint16': 'ushort',
    'int32': 'int',
    'uint32': 'uint',
    'int64': 'long',
    'uint64': 'ulong',
    'float32': 'float',
    'float64': 'double',
    'string': '[ubyte:64]',
    # ROS time/duration types can be represented as 64-bit integers.
    # A common practice is to store total nanoseconds.
    'time': 'uint64',
    'duration': 'int64',
}

def convert_ros_type_to_fbs(ros_type):
    """
    Converts a ROS message field type to its FlatBuffers equivalent.

    Args:
        ros_type (str): The ROS type (e.g., 'int32', 'string[]', 'geometry_msgs/Point').

    Returns:
        tuple: A tuple containing the FlatBuffers type (str) and a boolean indicating if it's an array.
    """
    # Check for array types, including fixed-size arrays (e.g., uint8[16])
    is_array = ros_type.endswith(']')
    base_type = re.sub(r'\[.*\]', '', ros_type)

    # Map the base type to its FlatBuffers equivalent
    if base_type in ROS_TO_FBS_TYPE_MAP:
        fbs_type = ROS_TO_FBS_TYPE_MAP[base_type]
    else:
        # This is a nested message type. Convert ROS's 'package/Msg' to
        # FlatBuffers' 'package.Msg' for namespaced access.
        fbs_type = base_type.replace('/', '.')

    return fbs_type, is_array

def parse_msg_file(msg_path):
    """
    Parses a .msg file to extract its name, fields, constants, and dependencies.

    Args:
        msg_path (str): The path to the input .msg file.

    Returns:
        tuple: A tuple containing the message name, a list of fields, a list of
               constants, and a list of dependencies (other .fbs files).
    """
    fields = []
    constants = []
    dependencies = set()
    msg_name = os.path.splitext(os.path.basename(msg_path))[0]

    with open(msg_path, 'r') as f:
        for line in f:
            # Remove comments and strip whitespace
            line = line.split('#', 1)[0].strip()
            if not line:
                continue

            # Check for constant definitions (e.g., "uint8 FOO=1")
            if '=' in line:
                parts = line.split('=', 1)
                type_name_part = parts[0].strip().split()
                const_type, const_name = type_name_part[0], type_name_part[1]
                const_value = parts[1].strip()
                constants.append((const_type, const_name, const_value))
            else:
                # This is a field definition
                parts = line.split()
                if len(parts) < 2:
                    continue
                ros_type, field_name = parts[0], parts[1]
                
                # Identify dependencies on other message packages
                base_type = re.sub(r'\[.*\]', '', ros_type)
                if '/' in base_type:
                    # e.g., 'std_msgs/Header' becomes a dependency on 'std_msgs/Header.fbs'
                    dependency_file = base_type + '.fbs'
                    dependencies.add(dependency_file)

                fields.append((ros_type, field_name))

    return msg_name, fields, constants, sorted(list(dependencies))

def generate_fbs_content(msg_name, fields, constants, dependencies, namespace):
    """
    Generates the string content for the .fbs schema file.
    """
    content = []

    # Add include statements for dependencies
    for dep in dependencies:
        content.append(f'include "{dep}";')
    if dependencies:
        content.append('')

    # Add namespace declaration
    if namespace:
        content.append(f'namespace {namespace};')
        content.append('')

    # Add constants. For simplicity, each constant is defined directly.
    # A more advanced approach could group them into enums.
    for const_type, const_name, const_value in constants:
        fbs_type, _ = convert_ros_type_to_fbs(const_type)
        content.append(f'const {const_name}:{fbs_type} = {const_value};')
    if constants:
        content.append('')
    
    # Define the main table for the message
    content.append(f'table {msg_name} {{')
    for ros_type, field_name in fields:
        fbs_type, is_array = convert_ros_type_to_fbs(ros_type)
        if is_array:
            content.append(f'  {field_name}:[{fbs_type}];')
        else:
            content.append(f'  {field_name}:{fbs_type};')
    content.append('}')
    content.append('')

    # Add the root_type declaration
    content.append(f'root_type {msg_name};')
    
    return '\n'.join(content)

def find_files(folder_path, file_extension):
    """
    Finds all files with a given extension in a folder and its subfolders.

    Args:
        folder_path (str): The absolute or relative path to the folder to search.
        file_extension (str): The file extension to search for (e.g., '.txt', '.py').

    Returns:
        list: A list of full paths to the files found.
              Returns an empty list if the folder doesn't exist or no files are found.
    """
    # Ensure the file extension starts with a dot
    if not file_extension.startswith('.'):
        file_extension = '.' + file_extension

    found_files = []
    
    # Check if the provided path is a valid directory
    if not os.path.isdir(folder_path):
        print(f"Error: The folder path '{folder_path}' does not exist or is not a directory.")
        return found_files

    # os.walk() recursively traverses the directory tree
    for root, dirs, files in os.walk(folder_path):
        for filename in files:
            # Check if the file ends with the specified extension
            if filename.endswith(file_extension):
                # Construct the full path and add it to our list
                full_path = os.path.join(root, filename)
                found_files.append(full_path)
                
    return found_files


def main():
    """Main function to parse arguments and run the conversion."""
    parser = argparse.ArgumentParser(
        description='Convert a ROS .msg file to a FlatBuffers .fbs schema.',
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument('interface_folder', help='Path to the input ROS interface folder.')
    parser.add_argument(
        '-o', '--output',
        help='Path for the output .fbs files.\n(default: creates .fbs file in a root fbs directory structure adjacent the interface folder)'
    )
    parser.add_argument('-e', '--extension', default=".msg", help="The file extension to look for (e.g., '.msg', '.srv', '.action').")
    parser.add_argument(
        '-n', '--namespace',
        help='Namespace for the generated schema.\n(default: inferred from the parent directory of the "msg" folder)'
    )
    
    args = parser.parse_args()

    
    interface_file_list = find_files(args.interface_folder, args.extension)

    for interface_file in interface_file_list:

        # Determine the output path if not specified
        output_path = args.output
        if not output_path:
            base_name = os.path.splitext(interface_file)[0].replace("/msg/", "/fbs/", 1).replace("/msg/", "/")
            output_path = os.path.dirname(interface_file).replace("/msg/", "/fbs/", 1).replace("/msg/", "/")
            output_file = f'{base_name}.fbs'
            
        

        # Attempt to infer the namespace from the file path if not specified
        namespace = args.namespace
        if not namespace:
            # Path might be /path/to/ros_ws/src/my_package/msg/MyMessage.msg
            # We want to extract 'my_package'
            try:
                # Normalize path separators
                norm_path = os.path.normpath(interface_file)
                path_parts = norm_path.split(os.sep)
                # Find the 'msg' directory and get its parent
                msg_index = path_parts.index('msg')
                if msg_index > 0:
                    namespace = path_parts[msg_index - 1]
            except (ValueError, IndexError):
                # 'msg' not in path, cannot infer namespace
                pass

        try:
            if not os.path.exists(output_path):
                os.makedirs(output_path)
                print(f"Successfully created directory: '{output_path}'")

            msg_name, fields, constants, dependencies = parse_msg_file(interface_file)
            fbs_content = generate_fbs_content(msg_name, fields, constants, dependencies, namespace)

            with open(output_file, 'w') as f:
                f.write(fbs_content)
            
            print(f"✅ Successfully converted '{interface_file}' to '{output_file}'")

        except FileNotFoundError:
            print(f"❌ Error: Input file not found at '{interface_file}'")
        except Exception as e:
            print(f"❌ An unexpected error occurred: {e}")

if __name__ == '__main__':
    main()
