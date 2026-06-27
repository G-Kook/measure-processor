from .base import BaseFilter
import polars as pl
from .repo import repo_utils
from utils import filter_utils

class BridgeFilter(BaseFilter):
    @classmethod
    def can_filter(cls, df, meta):
        return 'types' in meta and 'bridge' in meta['types']

    def filter(self):
        SWEEP = self.df
        WAFERID = self.meta['waferid']

        I_LEAK_MAX = filter_utils.bridge_ileak_max()
        ID_COLS = ['DIE_X', 'DIE_Y', 'MODULE', 'PAD1', 'PAD2']
        PF_PAIR = SWEEP.group_by(ID_COLS).agg(
                (pl.col('I_1').abs().max()<I_LEAK_MAX).alias('PF')
            ).with_columns(
                pl.when(pl.col('PF')).then(pl.lit('GOOD')).otherwise(pl.lit('BAD')).cast(pl.Categorical).alias('FILTER-PAIR_LEAKAGE')
            ).drop(['PF'])
        repo_utils.update(waferid=WAFERID, dat_type='bridge', dat_id='leakage', id_cols=ID_COLS, filter=PF_PAIR)

        ## ADD FILTERS
        meta = self.meta.copy()
        repo_utils.append_filters(meta=meta, waferid=WAFERID, dat_type='bridge')

        return SWEEP, meta