from typing import List, Dict

import pydantic


class Config(pydantic.BaseModel):
    block_size: int
    index_size: int


Key = str
Block = int


class BlockInfo(pydantic.BaseModel):
    block_list: List[Block]
    length: int


class Metadata(pydantic.BaseModel):
    num_blocks: int
    block_map: Dict[Key, BlockInfo]
    unused_block_list: List[Block]  # always sorted


class Stats(pydantic.BaseModel):
    bytes_written: int
    bytes_stored: int
    storage_efficiency: float
    metadata_size: int
