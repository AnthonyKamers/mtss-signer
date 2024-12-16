"""Use to generate a large CSV file for testing purposes. Will write CSV data to STDOUT
Usage: python make-test-csv.py 512000000   # Make a ~512mb CSV file
Taken from https://gist.github.com/shevron/e466b7f2947aa531a3e26bc970175233
"""
import csv
import sys
from itertools import count


def make_csv_row(counter, row_width, zero_fill=8):
    return [str(next(counter)).zfill(zero_fill) for _ in range(row_width)]


def write_large_csv(output_file, max_size, row_width=100):
    writer = csv.writer(output_file)
    c = count()
    while True:
        writer.writerow(make_csv_row(c, row_width))
        if output_file.tell() >= max_size:
            break


if __name__ == '__main__':
    write_large_csv(sys.stdout, sys.argv[1])
