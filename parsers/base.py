from abc import ABC, abstractmethod
import polars as pl
from typing import Iterator

class BaseParser(ABC):
    @classmethod
    @abstractmethod
    def can_parse(cls, fpath: str) -> bool:
        pass

    @abstractmethod
    def parse(self) -> Iterator[tuple[pl.DataFrame, dict[str]]]:
        pass
    
    def __init__(self, fpath: str, meta: dict[str]):
        self.fpath = fpath
        self.meta = meta.copy()