from abc import ABC, abstractmethod
import polars as pl
from typing import Iterator

class BaseTransformer(ABC):
    @classmethod
    @abstractmethod
    def can_transform(cls, df: pl.DataFrame, meta: dict[str]) -> bool:
        pass

    @abstractmethod
    def transform(self) -> Iterator[tuple[pl.DataFrame, dict[str]]]:
        pass
    
    def __init__(self, df: pl.DataFrame, meta: dict[str]):
        self.df = df
        self.meta = meta.copy()