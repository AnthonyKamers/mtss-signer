import sys
from itertools import count

DEFAULT_LINE = "0" * 8 + "\n"


def write_line(counter, row_width, zero_fill=8):
    return "\n".join([str(next(counter)).zfill(zero_fill) for _ in range(row_width)])


def write_one_line(counter, row_width, zero_fill=8):
    return ",".join([str(next(counter)).zfill(zero_fill) for _ in range(row_width)])


def generate_txt(output_file, max_size, lines=None, row_width=100):
    counter = count()
    counter_lines = 1

    with open(output_file, 'w') as f:
        while f.tell() <= max_size:
            if lines:
                if counter_lines == lines:
                    content = write_one_line(counter, row_width)
                else:
                    content = DEFAULT_LINE
                    counter_lines += 1
            else:
                content = write_line(counter, row_width)

            f.write(content)


# filename size_bytes lines
if __name__ == '__main__':
    filename = sys.argv[1]
    size_bytes = int(sys.argv[2])

    lines_file = None
    if len(sys.argv) == 4:
        lines_file = int(sys.argv[3])

    generate_txt(filename, size_bytes, lines_file)
