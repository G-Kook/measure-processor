from pathlib import Path
import polars as pl
import spotfire.sbdf as sbdf

BASE_DIR = Path(__file__).resolve().parent
OUT_DIR = BASE_DIR.parent / 'files_out'

def make_trends():

    for folder in BASE_DIR.iterdir():
        if not folder.is_dir():
            continue
        arrow_files = sorted(folder.glob('*.arrow'))
        if not arrow_files:
            continue

        trend = pl.concat(
                [pl.read_ipc(f) for f in arrow_files],
                how='diagonal'
            )

        sbdf.export_data(trend.to_pandas(), f'{OUT_DIR}/{folder.name}.sbdf')