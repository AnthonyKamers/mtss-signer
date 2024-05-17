import sys
from timeit import default_timer as timer

from mtsssigner.utils.file_and_block_utils import *

# numpy.set_printoptions(threshold=sys.maxsize)
# correta = create_polynomial_cff(3,2)
# errada = create_polynomial_cff_2(3,2)

# print(correta == errada)

TEXT_PATH = "msg/correct/hash/"
TEXT_EXTENSION = ".txt"

XML_PATH = "msg/xml/"
XML_EXTENSION = ".xml"

files = ["64", "512", "4096", "32768"]

if __name__ == '__main__':
    for file in files:
        file_path = TEXT_PATH + file + TEXT_EXTENSION

        start_text = timer()
        get_message_and_blocks_from_file(file_path)
        end_text = timer()
        diff_text = end_text - start_text

        xml_path = XML_PATH + file + XML_EXTENSION
        start_xml = timer()
        get_message_and_blocks_from_file(xml_path)
        end_xml = timer()
        diff_xml = end_xml - start_xml

        print(diff_text, diff_xml, diff_xml - diff_text)
