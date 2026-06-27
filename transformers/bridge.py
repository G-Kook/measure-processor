from .base import BaseTransformer
import polars as pl
from utils import tx_utils

class BridgeTransformer(BaseTransformer):
    @classmethod
    def can_transform(cls, df, meta):
        return 'types' in meta and 'bridge' in meta['types']
    
    def transform(self):
        WAFERID = self.meta['waferid']
        PID = self.meta['pid']
        
        SWEEP_LONG = self.df
        FEATURES_WIDE = self.meta['features']
        FILTERS = [] if 'filters' not in self.meta else self.meta['filters']

        ID_COLS = ['DIE_X', 'DIE_Y', 'MODULE', 'PAD1', 'PAD2']
        FEATURES_LONG = FEATURES_WIDE.unpivot(
                index=ID_COLS, on=[c for c in FEATURES_WIDE.columns if c not in ID_COLS], variable_name='ITEM', value_name='VALUE'
            ).with_columns(
                pl.col('ITEM').cast(pl.Categorical)
            )

        EXPORTS = {
            'brg_sweep': SWEEP_LONG,
            'brg_features': FEATURES_WIDE
        }

        type: str
        df: pl.DataFrame
        for type, df in EXPORTS.items():
            for filter in FILTERS:
                df = df.join(filter['df'], on=filter['id_cols'], how='left')

            df = df.with_columns(
                pl.lit(WAFERID).cast(pl.Categorical).alias('WAFERID'),
                pl.lit(PID).cast(pl.Categorical).alias('PID')
            )
            df = tx_utils.with_die_xy(df=df, diex='DIE_X', diey='DIE_Y', alias='DIE_XY')
            df = tx_utils.with_radius(df=df, pid=PID, diex='DIE_X', diey='DIE_Y', alias='RADIUS')
            df = tx_utils.with_additional_info(df=df, waferid=WAFERID)

            meta = {
                'type': set(type.split('_')),
                'dir': type,
                'export': {'arrow'}
            }
            yield df, meta