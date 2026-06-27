from abc import ABC, abstractmethod
import polars as pl
from utils import resource_utils

class BaseFilter(ABC):
    @classmethod
    @abstractmethod
    def can_filter(cls, df: pl.DataFrame, meta: dict[str]) -> bool:
        pass

    @abstractmethod
    def filter(self) -> tuple[pl.DataFrame, dict[str]]:
        pass

    def __init__(self, df: pl.DataFrame, meta: dict[str]):
        self.df = df
        self.meta = meta.copy()