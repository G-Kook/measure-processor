from .base import BaseProcessor
import polars as pl

class ProcessorFactory():
    @staticmethod
    def iter_processors(df: pl.DataFrame, meta: dict[str]):
        provided: False
        for processor_cls in BaseProcessor.__subclasses__():
            if processor_cls.can_process(df=df, meta=meta):
                provided = True
                yield processor_cls(df=df, meta=meta)
        if not provided:
            raise ValueError('Unable to provide any processor for the dataframe.')