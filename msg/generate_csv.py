"""Use to generate a large CSV file for testing purposes. Will write CSV data to STDOUT
Usage: python make-test-csv.py 512000000   # Make a ~512mb CSV file
Taken from https://gist.github.com/shevron/e466b7f2947aa531a3e26bc970175233
"""
import csv
import sys
from enum import Enum
from itertools import count


class TypeBlock(Enum):
    BREAK_LINE = "break_line"
    COMMA = "comma"


def make_csv_row(counter, row_width, zero_fill=8):
    return [str(next(counter)).zfill(zero_fill) for _ in range(row_width)]


def generate_csv(output_file, max_size, row_width=100):
    file = open(output_file, 'w')
    writer = csv.writer(file)
    c = count()
    while True:
        writer.writerow(make_csv_row(c, row_width))
        if file.tell() >= max_size:
            break


# filename size_bytes type_block number_blocks
if __name__ == '__main__':
    filename = sys.argv[1]
    size_bytes = int(sys.argv[2])

    generate_csv(filename, size_bytes)
