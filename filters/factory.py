from .base import BaseFilter
import polars as pl

class FilterFactory():
    @staticmethod
    def create_filter(df: pl.DataFrame, meta: dict[str]) -> BaseFilter:
        for filter_cls in BaseFilter.__subclasses__():
            if filter_cls.can_filter(df=df, meta=meta):
                return filter_cls(df=df, meta=meta)
        raise Exception('Unable to provide any filter.')