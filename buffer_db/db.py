from __future__ import annotations

import os
from typing import BinaryIO, Union

from buffer_db import model
from buffer_db.io import IO


class Context:
    cfg: model.Config
    file: Union[BinaryIO, IO]
    meta: model.Metadata
    using: bool

    def __init__(self, file: Union[BinaryIO, IO], block_size: int = 1024, index_size: int = 8):
        """
        FileDB

        memory structure

            [file] = [block][block]...[block][block][metadata][start_of_metadata]

            - start_of_metadata is position of meta
            - metadata contains necessary information to get records
            - object is written into blocks
            - object is deleted leads to unused blocks
            - unused blocks will be allocated for newly inserted object

        """
        self.cfg = model.Config(block_size=block_size, index_size=index_size)
        self.file = file
        is_new_file = self.file.seek(0, os.SEEK_END) == 0
        if not is_new_file:
            self.__read_metadata()
        else:
            self.meta = model.Metadata(
                num_blocks=0,
                value_length_map={},
                block_map={},
                unused_block_list=[],
            )
            self.__write_metadata()
        self.using = False

    def __enter__(self) -> Context:
        self.using = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.using = False
        self.__write_metadata()

    def __read_metadata(self):
        end_of_meta = self.file.seek(-self.cfg.index_size, os.SEEK_END)
        start_of_meta = int.from_bytes(
            bytes=self.file.read(self.cfg.index_size),
            byteorder="little",
            signed=False,
        )
        self.file.seek(start_of_meta)
        self.meta = model.Metadata.parse_raw(self.file.read(end_of_meta - start_of_meta))

    def __write_metadata(self):
        start_of_meta = self.cfg.block_size * self.meta.num_blocks
        self.file.seek(start_of_meta)
        self.file.write(self.meta.json().encode("utf-8"))
        self.file.write(start_of_meta.to_bytes(
            length=self.cfg.index_size,
            byteorder="little",
            signed=False,
        ))
        self.file.truncate()

    def __create_blocks_local(self, num_create_blocks: int):  # _local does not write to file
        if num_create_blocks == 0:
            return
        self.meta.unused_block_list.extend(range(self.meta.num_blocks, self.meta.num_blocks + num_create_blocks))
        self.meta.num_blocks += num_create_blocks

    def __remove_blocks_local(self, num_remove_blocks: int):  # _local does not write to file
        """
        assume
        - unused_block_list always sorted
        - all del blocks are at the tail of unused_block_list
        """
        if num_remove_blocks == 0:
            return
        self.meta.unused_block_list = self.meta.unused_block_list[:-num_remove_blocks]
        self.meta.num_blocks -= num_remove_blocks

    def __write_block(self, block: model.Block, b: bytes):
        self.file.seek(block * self.cfg.block_size)
        self.file.write(b)

    def __read_block(self, block: model.Block) -> bytes:
        self.file.seek(block * self.cfg.block_size)
        return self.file.read(self.cfg.block_size)

    def keys(self) -> set[model.Key]:
        return set(self.meta.block_map.keys())

    def write(self, key: model.Key, b: bytes):
        if key not in self.meta.block_map:
            self.meta.block_map[key] = model.BlockInfo(
                block_list=[],
                length=0,
            )

        # CALCULATE
        # number of blocks of input
        num_blocks = 1 + (len(b) - 1) // self.cfg.block_size
        # number of blocks in old assignment will be reused
        num_reuse_blocks = min(num_blocks, len(self.meta.block_map[key].block_list))
        # number of blocks in unused blocks will be used
        num_new_blocks = max(0, num_blocks - len(self.meta.block_map[key].block_list))
        # number of new blocks to be created
        num_create_blocks = max(
            0,
            num_new_blocks - len(self.meta.unused_block_list),
        )
        # CREATE NEW BLOCKS IF ANY
        self.__create_blocks_local(num_create_blocks)
        # WRITE METADATA
        # block_list = old_assignment[:num_reused_blocks] + unused_blocks[:num_new_blocks]
        block_list = [
            *self.meta.block_map[key].block_list[:num_reuse_blocks],
            *self.meta.unused_block_list[:num_new_blocks],
        ]
        # unused_blocks = sort(old_assignment[num_reused_blocks:] + unused_blocks[num_new_blocks:])
        self.meta.unused_block_list = [
            *self.meta.unused_block_list[num_new_blocks:],
            *self.meta.block_map[key].block_list[num_reuse_blocks:],
        ]
        self.meta.unused_block_list.sort()
        # set block_map and value_length
        self.meta.block_map[key].block_list = block_list
        self.meta.block_map[key].length = len(b)

        # WRITE BLOCK AND METADATA TO FILE
        for i, block in enumerate(block_list):
            start_idx = i * self.cfg.block_size
            stop_idx = min(start_idx + self.cfg.block_size, len(b))
            self.__write_block(block, b[start_idx:stop_idx])

    def read(self, key: model.Key) -> bytes:
        if key not in self.meta.block_map:
            return b""
        block_list = self.meta.block_map[key].block_list
        value = b""
        for block in block_list:
            value += self.__read_block(block)
        length = self.meta.block_map[key].length
        return value[:length]

    def delete(self, key: model.Key):
        if key not in self.meta.block_map:
            return
        block_list = self.meta.block_map[key].block_list
        self.meta.block_map.pop(key)
        self.meta.unused_block_list.extend(block_list)
        self.meta.unused_block_list.sort()
        num_del_blocks = 0
        for block in range(self.meta.num_blocks - 1, -1, -1):
            if block not in self.meta.unused_block_list:
                break
            num_del_blocks += 1
        self.__remove_blocks_local(num_del_blocks)


class DB:
    def __init__(self, file: Union[BinaryIO, IO], block_size: int = 1024, index_size: int = 8):
        self.ctx = Context(file=file, block_size=block_size, index_size=index_size)

    def context(self) -> Context:
        if self.ctx.using:
            raise Exception("a single context is allowed to enter at the same time")
        self.ctx.__enter__()
        return self.ctx

    def stats(self) -> model.Stats:
        stats = model.Stats(
            bytes_written=0,
            bytes_stored=0,
            storage_efficiency=0,
            metadata_size=0,
        )
        for key in self.ctx.meta.block_map:
            stats.bytes_written += self.ctx.meta.block_map[key].length
        stats.bytes_stored = self.ctx.file.seek(0, os.SEEK_END)
        stats.storage_efficiency = stats.bytes_written / stats.bytes_stored
        stats.metadata_size = len(self.ctx.meta.json().encode("utf-8"))
        return stats
