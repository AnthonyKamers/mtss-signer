from typing import List

from mtsssigner.blocks.Block import Block
from mtsssigner.blocks.Parser import Parser


class TXTParser(Parser):
    def __init__(self, path: str):
        super().__init__(path)

    def parse(self) -> List[Block]:
        self.blocks = []
        for line in self.get_text_from_path().splitlines():
            self.blocks.append(self.get_block(line))

        return self.blocks

    def get_block(self, element: any, level: int = 0) -> Block:
        return Block(content=element)
