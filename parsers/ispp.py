from .base import BaseParser
import polars as pl
from pathlib import Path

class IsppParser(BaseParser):
    @classmethod
    def can_parse(cls, fpath: str):
        with open(fpath, 'r') as file:
            return any('## ISPP' in l for l in file)
        
    def parse(self):
        COLUMN_TOKENS = [('BL', 'WL', 'V_PGM[V]', 'V_TH[V]')]
        cols = {c: [] for c in ['DIE_X', 'DIE_Y', 'MODULE', 'BL', 'WL', 'V_PGM', 'VTH']}
        ready = False
        parsing = False
        for line in Path(self.fpath).read_text().splitlines():
            if '## DIE' in line:
                die_x, die_y = line.split('(')[1].split(')')[0].split(',')
                continue
            if '## MODULE' in line:
                module = line.split(':')[1].strip()
                continue
            if '## ISPP' in line:
                ready = True
                continue
            if ready and tuple(line.strip().split()[:4]) in COLUMN_TOKENS:
                ready = False
                parsing = True
                continue
            if parsing:
                if line[0] != ' ':
                    parsing = False
                    continue
                bl, wl, vpgm, vth = line.strip().split()
                cols['DIE_X'].append(int(die_x))
                cols['DIE_Y'].append(int(die_y))
                cols['MODULE'].append(module)
                cols['BL'].append(bl)
                cols['WL'].append(wl)
                cols['V_PGM'].append(float(vpgm))
                cols['VTH'].append(float(vth))
                continue

        df = pl.DataFrame(
            cols,
            schema_overrides = {
                'MODULE': pl.Categorical,
                'BL': pl.Categorical,
                'WL': pl.Categorical
            }
        )
        meta = self.meta.copy()
        meta['types'] = {'parsed', 'ispp'}
        yield df, meta