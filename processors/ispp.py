from .base import BaseProcessor
from utils import proc_utils
import polars as pl

TGT_VTH = 4.0

class IsppProcessor(BaseProcessor):
    @classmethod
    def can_process(cls, df, meta):
        return 'types' in meta and 'ispp' in meta['types']

    def process(self):
        SWEEP = proc_utils.replace_nan_vth(df=self.df, vth='VTH')
        ID_COLS = ['DIE_X', 'DIE_Y', 'MODULE', 'BL', 'WL']

        features = proc_utils.with_x_crossing_target_y(
            df=SWEEP,
            index=ID_COLS,
            x='V_PGM',
            y='VTH',
            yscale='linear',
            target=TGT_VTH,
            alias=f'V_PGM_{TGT_VTH:.1f}V',
            alias_slope=f'SLOPE_{TGT_VTH:.1f}V'
        )

        meta = self.meta.copy()
        meta['features'] = features
        meta['type'] = {'processed', 'ispp'}
        yield SWEEP, meta