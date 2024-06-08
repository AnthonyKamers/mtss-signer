import sys


def main(file_name: str, index: int):
    output = ""
    with open(file_name, 'r') as file:
        lines = file.readlines()
        for line in lines:
            split = line.rsplit(" ")
            time_seconds = float(split[index])
            time_ms = time_seconds * 1000

            for i in range(len(split)):
                output += f'{split[i]} ' if i != index else f'{time_ms}'
            output += "\n"

    with open(f'{get_ms_file(file_name)}', 'w') as file:
        file.write(output)


def get_ms_file(file_name: str):
    file = file_name.split('.')[0]
    file_ms = file.replace("seconds", "ms") + ".txt"

    return file_ms


if __name__ == "__main__":
    file_name = sys.argv[1]
    index = int(sys.argv[2])

    main(file_name, index)
