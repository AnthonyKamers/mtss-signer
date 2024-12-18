import os
import sys

from pypdf import PdfWriter

FILE_BASE = "pdf/test.pdf"


# we create new PDFs by merging the same PDF multiple times
def generate_pdf(output_file, max_size):
    writer = PdfWriter()
    file_size = 0

    while file_size <= max_size:
        writer.append(FILE_BASE)
        writer.write(output_file)

        file_size = os.path.getsize(output_file)
    writer.close()


if __name__ == "__main__":
    filename = sys.argv[1]
    size_bytes = int(sys.argv[2])

    generate_pdf(filename, size_bytes)
