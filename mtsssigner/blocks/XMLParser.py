from typing import List
from xml.etree import ElementTree

from mtsssigner.blocks.Block import Block
from mtsssigner.blocks.Parser import Parser


class XMLParser(Parser):
    def __init__(self, path: str):
        super().__init__(path)
        self.root = None

    def _iterate_element(self, element: ElementTree.Element, level: int = 0):
        block = self.get_block(element, level)
        self.blocks.append(block)
        for child in element:
            self._iterate_element(child, level + 1)

    def parse(self) -> List[Block]:
        self.blocks = []
        self.root = ElementTree.parse(self.path).getroot()

        self.blocks.append(self.get_block(self.root, 1))
        for element in self.root:
            self._iterate_element(element, 2)

        return self.blocks

    def get_block(self, element: ElementTree.Element, level: int = 0) -> Block:
        return Block(content=element.text, name=element.tag, attributes=element.attrib, level=level)
