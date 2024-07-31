def read_file(file_path):
    try:
        with open(file_path, 'r') as file:
            content = file.read()
        return content
    except FileNotFoundError:
        return "File not found."

def write_to_file(file_path, data):
    with open(file_path, 'w') as file:
        file.write(data)
    return "Write operation successful."


def append_to_file(file_path, data):
    with open(file_path, 'a') as file:
        file.write(data + '\n')
    return "Append operation successful."

