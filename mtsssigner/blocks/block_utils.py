from enum import Enum

from mtsssigner.blocks.JSONParser import JSONParser
from mtsssigner.blocks.PDFParser import PDFParser
from mtsssigner.blocks.Parser import Parser
from mtsssigner.blocks.TXTParser import TXTParser
from mtsssigner.blocks.XMLParser import XMLParser


class EXTENSION(Enum):
    TXT = "txt"
    XML = "xml"
    PDF = "pdf"
    JSON = "json"


MAPPING_EXTENSION_PARSER = {
    EXTENSION.TXT: TXTParser,
    EXTENSION.XML: XMLParser,
    EXTENSION.PDF: PDFParser,
    EXTENSION.JSON: JSONParser
}


def get_extension_file(file_path: str) -> str:
    return file_path.rsplit(".", 1)[1]


def get_parser_for_file(file_path: str) -> Parser:
    extension = get_extension_file(file_path)
    parser = MAPPING_EXTENSION_PARSER[EXTENSION(extension)](file_path)
    return parser