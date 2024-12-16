import math
from typing import Union, List

import numpy

from mtsssigner.blocks.Block import Block
from mtsssigner.blocks.PGMReader import PGMReader
from mtsssigner.blocks.Parser import Parser


# ImageParser for pgm images only
class ImageParser(Parser):
    def __init__(self, path: str):
        super().__init__(path)
        self.block_size: Union[None, int] = None
        self.reader: Union[None, PGMReader] = None
        self.image: Union[None, numpy.ndarray] = None

    def set_block_size(self, block_size: int):
        self.block_size = block_size

    def parse(self) -> List[Block]:
        self.blocks = []

        if self.block_size is None:
            raise Exception("Block size is not set (ImageParser requires it)")

        if self.image is None:
            self.get_content()

        width = self.reader.width
        height = self.reader.height

        # handle case where block_size is larger than image
        # we only create one block covering the entire image
        if self.block_size > width or self.block_size > height:
            self.block_size = max(width, height)

        block_rows = math.floor((width + self.block_size - 1) / self.block_size)
        block_columns = math.floor((height + self.block_size - 1) / self.block_size)

        # iterate over each block
        for i in range(block_rows):
            for j in range(block_columns):
                # calculate indexes for the block
                start_row = i * self.block_size
                end_row = min(start_row + self.block_size, block_rows)
                start_column = j * self.block_size
                end_column = min(start_column + self.block_size, block_columns)

                block_content = b''

                # iterate over elements and store pixels for determined block
                for row in range(start_row, end_row):
                    for column in range(start_column, end_column):
                        int_number = self.image[row][column].item()
                        block_content += int_number.to_bytes(1, byteorder='big')

                self.blocks.append(Block(name=f"{i}_{j}", content=block_content))

        return self.blocks

    def get_block(self, element: any, level: int = 0) -> Block:
        pass

    def get_content(self) -> Union[str, bytes]:
        if self.image is None:
            self.reader = PGMReader()
            self.image = self.reader.read_pgm(self.path)

        return self.image.tostring()
