from .base import BaseTransformer
import polars as pl

class TransformerFactory():
    @staticmethod
    def create_transformer(df: pl.DataFrame, meta: dict[str]) -> BaseTransformer:
        for transformer_cls in BaseTransformer.__subclasses__():
            if transformer_cls.can_transform(df=df, meta=meta):
                return transformer_cls(df=df, meta=meta)
        raise Exception('Unable to provide any transformer.')