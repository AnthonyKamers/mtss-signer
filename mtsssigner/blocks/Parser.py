from abc import ABC, abstractmethod
from typing import List

from mtsssigner.blocks.Block import Block


class Parser(ABC):
    def __init__(self, path: str):
        self.path: str = path
        self.blocks: List[Block] = []

    @abstractmethod
    def parse(self) -> List[Block]:
        pass

    @abstractmethod
    def get_block(self, element: any, level: int = 0) -> Block:
        pass

    def get_blocks(self) -> List[Block]:
        return self.blocks

    def get_text_from_path(self) -> str:
        with open(self.path, 'r') as file:
            return file.read()
