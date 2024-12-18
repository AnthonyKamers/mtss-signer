import sys
from itertools import count


def generate_json(output_file, max_size):
    counter = count()

    with open(output_file, 'w') as file:
        file.write("{\n")
        while file.tell() <= max_size:
            file.write(f"\t\"{next(counter)}\": \"content\",\n")
        file.write("}")


# filename size_bytes
if __name__ == "__main__":
    filename = sys.argv[1]
    size_bytes = int(sys.argv[2])

    generate_json(filename, size_bytes)
