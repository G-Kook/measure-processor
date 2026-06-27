from .base import BaseFilter
import polars as pl
from .repo import repo_utils
from utils import filter_utils

class IsppFilter(BaseFilter):
    @classmethod
    def can_filter(cls, df, meta):
        return 'types' in meta and 'ispp' in meta['types']

    def filter(self):
        SWEEP = self.df
        WAFERID = self.meta['waferid']
        PID = self.meta['pid']

        ## CELL WITH GOOD ISPP SHAPE
        SLOPE_MIN, SLOPE_MAX = filter_utils.ispp_slope_min_max(PID)
        V_MIN, V_MAX = filter_utils.ispp_slope_filter_range(PID)
        WL_COLS = ['DIE_X', 'DIE_Y', 'MODULE', 'BL', 'WL']
        PF_WL = SWEEP.sort(WL_COLS+['V_PGM']).with_columns(
                (pl.col('VTH').diff().over(WL_COLS) / pl.col('V_PGM').diff().over(WL_COLS)).alias('SLOPE')
            ).filter(
                pl.col('V_PGM').is_between(V_MIN, V_MAX)
            ).with_columns(
                pl.col('SLOPE').is_between(SLOPE_MIN, SLOPE_MAX).alias('PF_SLOPE')
            ).group_by(WL_COLS).agg(pl.col('PF_SLOPE').all()).with_columns(
                pl.when(pl.col('PF_SLOPE')).then(pl.lit('GOOD')).otherwise(pl.lit('BAD')).cast(pl.Categorical).alias('FILTER-ISPP')
            ).drop(['PF_SLOPE'])
        repo_utils.update(waferid=WAFERID, dat_type='ispp', dat_id='wl', id_cols=WL_COLS, filter=PF_WL)

        ## ADD FILTERS
        meta = self.meta.copy()
        repo_utils.append_filters(meta=meta, waferid=WAFERID, dat_type='ispp')
        repo_utils.append_filters(meta=meta, waferid=WAFERID, dat_type='idvg')

        return SWEEP, meta