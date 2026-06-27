'''
[Measure Processor Demo]
Copyright 2026, Geon Kook

** REQUIRED MODULES
numpy, polars, pandas, pyarrow, spotfire, tqdm

** HOW TO USE
Put measurement data in /files_in, then run.
You will find the trend data in /files_out.
'''

from pathlib import Path
from tqdm import tqdm
import spotfire.sbdf as sbdf

BASE_DIR = Path(__file__).resolve().parent
FPATHS = [str(f) for f in sorted((BASE_DIR/'files_in').iterdir()) if f.is_file()]

from pipeline import run
with tqdm(total=len(FPATHS), ncols=110) as pbar:
    for fpath in FPATHS:
        pbar.write(f"Processing '{fpath}' ...")
        run(fpath)
        pbar.update(1)

from trendmaker.trend_maker import make_trends
make_trends()

print('\nFINISHED :)')