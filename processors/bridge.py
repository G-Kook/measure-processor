from .base import BaseProcessor
import polars as pl

class BridgeProcessor(BaseProcessor):
    @classmethod
    def can_process(cls, df, meta):
        return 'types' in meta and 'bridge' in meta['types']

    def process(self):
        SWEEP = self.df

        ID_COLS = ['DIE_X', 'DIE_Y', 'MODULE', 'PAD1', 'PAD2']
        FEATURES = SWEEP.group_by(ID_COLS).agg(pl.col('I_1').abs().max().alias('ILEAK_ABS'))

        meta = self.meta.copy()
        meta['features'] = FEATURES
        meta['type'] = {'processed', 'bridge'}
        yield SWEEP, meta