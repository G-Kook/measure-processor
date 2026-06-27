from abc import ABC, abstractmethod
import polars as pl
from typing import Iterator

class BaseProcessor(ABC):
    @classmethod
    @abstractmethod
    def can_process(cls, df: pl.DataFrame, meta: dict[str]) -> bool:
        pass
    
    @abstractmethod
    def process(self) -> Iterator[tuple[pl.DataFrame, dict[str]]]:
        pass

    def __init__(self, df: pl.DataFrame, meta: dict[str]):
        self.df = df
        self.meta = meta.copy()