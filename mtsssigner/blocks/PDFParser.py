from io import TextIOWrapper, BytesIO
from typing import List, Union

import pikepdf

from mtsssigner.blocks.Block import Block
from mtsssigner.blocks.Parser import Parser


class PDFParser(Parser):
    def __init__(self, path: str):
        super().__init__(path)
        self.passed: List[pikepdf.Object] = []

    def _iterate_element(self, object_pdf: pikepdf.Object, level: int = 1, prev_dict_block: Union[None, Block] = None):
        if object_pdf in self.passed:
            return

        self.passed.append(object_pdf)

        if isinstance(object_pdf, pikepdf.Dictionary):
            for key in object_pdf.keys():
                block = Block(name=key, level=level)
                self.blocks.append(block)

                self._iterate_element(object_pdf[key], level + 1, block)
        elif isinstance(object_pdf, pikepdf.Array):
            for item in object_pdf:
                self._iterate_element(item, level + 1)
        elif isinstance(object_pdf, pikepdf.Stream):
            try:
                content_stream = TextIOWrapper(BytesIO(object_pdf.read_bytes())).read()
            except UnicodeDecodeError:
                content_stream = object_pdf.read_bytes().decode('utf-8', errors='replace')

            block = Block(name="Stream", content=content_stream, level=level)
            self.blocks.append(block)

            for key in object_pdf.keys():
                block = Block(name=key, level=level+1)
                self.blocks.append(block)

                self._iterate_element(object_pdf[key], level + 2, block)
        else:
            # it is a final value of a dictionary, just update the previous block content
            prev_dict_block.content = str(object_pdf)

    def parse(self) -> List[Block]:
        self.blocks = []
        self.passed = []

        with pikepdf.open(self.path) as pdf:
            for object_pdf in pdf.objects:
                self._iterate_element(object_pdf, 1, None)

        return self.blocks

    def get_block(self, element: any, level: int = 0) -> Block:
        pass
