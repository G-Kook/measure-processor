from .base import BaseProcessor
import polars as pl
from utils import proc_utils

class IdvgProcessor(BaseProcessor):
    @classmethod
    def can_process(cls, df, meta):
        return 'types' in meta and 'idvg' in meta['types']

    def process(self):
        SWEEP = self.df
        ID_COLS = ['DIE_X', 'DIE_Y', 'MODULE', 'BL', 'WL']

        ION = SWEEP.filter(pl.col('V_G').is_close(7.0)).drop(['V_G']).rename({'I_DS': 'I_ON'})

        ITHS = {'1nA': 1e-9, '10nA': 10e-9, '30nA': 30e-9, '100nA': 100e-9}
        vths = SWEEP.select(ID_COLS).unique(maintain_order=True)
        for ith_rep, ith in ITHS.items():
            vth = proc_utils.with_x_crossing_target_y(
                    df=SWEEP,
                    index=ID_COLS,
                    x='V_G',
                    y='I_DS',
                    yscale='log10',
                    target=ith,
                    alias=f'VTH_{ith_rep}[V]',
                    alias_slope='slope'
                ).with_columns(
                    (1000/pl.col('slope')).alias(f'SWING_{ith_rep}[mV/dec]')
                ).drop(['slope'])
            vths = vths.join(vth, on=ID_COLS, how='left')

        FEATURES = vths.join(ION, on=ID_COLS, how='left')

        meta = self.meta.copy()
        meta['features'] = FEATURES
        meta['type'] = {'processed', 'idvg'}
        yield SWEEP, meta