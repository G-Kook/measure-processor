from utils import resource_utils
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from parsers.factory import ParserFactory
from processors.factory import ProcessorFactory
from filters.factory import FilterFactory
from transformers.factory import TransformerFactory
import re
from pathlib import Path
from tqdm import tqdm
import spotfire.sbdf as sbdf
from trendmaker.trend_maker import make_trends

BASE_DIR = Path(__file__).resolve().parent
OUT_ROOT = BASE_DIR/'trendmaker'
IMPORT_PATHS = [str(f) for f in sorted((BASE_DIR/'files_in').iterdir()) if f.is_file()]
EXPORT_DIR = OUT_DIR = BASE_DIR / 'files_out'

def waferid_from_filename(filename: str) -> str:
    WAFERID_PATTERN = re.compile(r'[A-Z0-9]{6}W(0[1-9]|1[0-9]|2[]0-4])')
    match = WAFERID_PATTERN.search(filename)
    if not match:
        raise ValueError(f'Cannot extract wafer id from filename: {filename}')
    return match.group(0)

def run():
    with tqdm(total=len(IMPORT_PATHS), ncols=110) as pbar:
        for fpath in IMPORT_PATHS:
            pbar.write(f"Processing '{fpath}' ...")
            FNAME = Path(fpath).stem
            WAFERID = waferid_from_filename(FNAME)
            PID = resource_utils.pid_from_waferid(WAFERID)
            meta = {
                'waferid': WAFERID,
                'pid': PID,
            }
            for parser in ParserFactory.iter_parsers(fpath=fpath, meta=meta):
                for df_parsed, meta_parsed in parser.parse():
                    for processor in ProcessorFactory.iter_processors(df=df_parsed, meta=meta_parsed):
                        for df_proc, meta_proc in processor.process():
                            filter = FilterFactory.create_filter(df=df_proc, meta=meta_proc)
                            filtered, meta_filtered = filter.filter()
                            transformer = TransformerFactory.create_transformer(df=filtered, meta=meta_filtered)
                            for df_tx, meta_tx in transformer.transform():
                                if 'export' in meta_tx:
                                    out_dir = OUT_ROOT / f'{meta_tx['dir']}'
                                    out_dir.mkdir(parents=False, exist_ok=True)
                                    out_path = str(out_dir / f'{FNAME}')
                                    if 'arrow' in meta_tx['export']:
                                        df_tx.write_ipc(f'{out_path}.arrow')
            pbar.update(1)

    for name, trend in make_trends():
        sbdf.export_data(trend.to_pandas(), f'{OUT_DIR}/{name}.sbdf')