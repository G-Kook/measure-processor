from .base import BaseParser
import polars as pl
from pathlib import Path

class BridgeParser(BaseParser):
    @classmethod
    def can_parse(cls, fpath: str):
        with open(fpath, 'r') as file:
            return any('## BRIDGE' in l for l in file)
            
    def parse(self):
        COLUMN_TOKENS = [('PAD1', 'PAD2', 'V_12[V]', 'I_1[A]')]
        cols = {c: [] for c in ['DIE_X', 'DIE_Y', 'MODULE', 'PAD1', 'PAD2', 'V_12', 'I_1']}
        ready = False
        parsing = False
        for line in Path(self.fpath).read_text().splitlines():
            if '## DIE' in line:
                die_x, die_y = line.split('(')[1].split(')')[0].split(',')
                continue
            if '## MODULE' in line:
                module = line.split(':')[1].strip()
                continue
            if '## BRIDGE' in line:
                ready = True
            if ready and tuple(line.split()) in COLUMN_TOKENS:
                ready = False
                parsing = True
                continue
            if parsing:
                if line[0] != ' ':
                    parsing = False
                    continue
                pad1, pad2, v12, i1 = line.split()
                cols['DIE_X'].append(int(die_x))
                cols['DIE_Y'].append(int(die_y))
                cols['MODULE'].append(module)
                cols['PAD1'].append(pad1)
                cols['PAD2'].append(pad2)
                cols['V_12'].append(float(v12))
                cols['I_1'].append(float(i1))
                continue
        df = pl.DataFrame(
            cols,
            schema_overrides = {
                'MODULE': pl.Categorical,
                'PAD1': pl.Categorical,
                'PAD2': pl.Categorical
            }
        )
        meta = self.meta.copy()
        meta['types'] = {'parsed', 'bridge'}
        yield df, meta