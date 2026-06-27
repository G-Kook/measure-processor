import json
from pathlib import Path
import polars as pl

CUR_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CUR_DIR.parent
RESOURCE_DIR = PROJECT_ROOT / 'resources'

def pid_from_waferid(waferid: str):
    FPATH = RESOURCE_DIR / 'waferid-to-pid.json'
    with open(FPATH, 'r', encoding='utf-8') as f:
        d = json.load(f)
    if waferid not in d:
        raise Exception('WAFERID is not in the list. Please add the item to resources/waferid_to_pid.json')
    return d[waferid]

def get_die_to_radius(pid: str):
    resource = None
    if pid in ['Gen10']: resource = RESOURCE_DIR / 'gen10-die-radius-map'
    if pid in ['Gen11']: resource = RESOURCE_DIR / 'gen11-die-radius-map'
    if resource is None:
        raise Exception('pid is not supported.')
    df = pl.read_csv(resource, separator='\t').select(['DIE_X', 'DIE_Y', 'RADIUS']).with_columns(pl.col('RADIUS').cast(pl.Float64))
    return df

def get_additional_info(waferid: str):
    fpath = RESOURCE_DIR / 'additional-info.json'
    with open(fpath, 'r', encoding='utf-8') as f:
        d = json.load(f)
        if waferid in d:
            return d[waferid]
    return {}
