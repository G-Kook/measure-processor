from .base import BaseFilter
import polars as pl
from .repo import repo_utils
from utils import filter_utils

class IdvgFilter(BaseFilter):
    @classmethod
    def can_filter(cls, df, meta):
        return 'types' in meta and 'idvg' in meta['types']

    def filter(self):
        SWEEP = self.df
        WAFERID = self.meta['waferid']
        PID = self.meta['pid']

        IOFF_MIN, IOFF_MAX = filter_utils.idvg_ioff_min_max(PID)
        ION_MIN, ION_MAX = filter_utils.idvg_ion_min_max(PID)

        BL_COLS = ['DIE_X', 'DIE_Y', 'MODULE', 'BL']
        WL_COLS = BL_COLS + ['WL']

        I_OFF = SWEEP.filter(pl.col('V_G').is_close(-5.0)).drop('V_G').rename({'I_DS': 'I_OFF'})
        I_ON = SWEEP.filter(pl.col('V_G').is_close(7.0)).drop('V_G').rename({'I_DS': 'I_ON'})
        I_MAX = SWEEP.group_by(WL_COLS).agg(pl.col('I_DS').max().alias('I_MAX'))
        PF_WL = SWEEP[WL_COLS].unique(maintain_order=True).join(
                I_OFF, on=WL_COLS
            ).join(
                I_ON, on=WL_COLS
            ).join(
                I_MAX, on=WL_COLS
            ).with_columns(
                (
                    pl.col('I_OFF').is_between(IOFF_MIN, IOFF_MAX)
                    & pl.col('I_ON').is_between(ION_MIN, ION_MAX)
                    & pl.col('I_MAX').lt(1.1*pl.col('I_ON'))
                ).alias('PF')
            ).drop(['I_OFF', 'I_ON', 'I_MAX'])

        ## BL with all good wl idvg shape
        PF_BL = PF_WL.group_by(BL_COLS).agg((pl.col('PF').all()).map_elements(lambda x: 'GOOD' if x else 'BAD').cast(pl.Categorical).alias('FILTER-BL_IDVG'))
        repo_utils.update(waferid=WAFERID, dat_type='idvg', dat_id='ssgs', id_cols=BL_COLS, filter=PF_BL)

        meta = self.meta.copy()
        repo_utils.append_filters(meta=meta, waferid=WAFERID, dat_type='idvg')
        return SWEEP, meta
