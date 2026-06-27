import pickle
import polars as pl
from pathlib import Path

CUR_DIR = Path(__file__).resolve().parent

def load_file(waferid: str):
    try:
        fpath = CUR_DIR / f'{waferid}.pkl'
        with open(fpath, 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        return {}
    
def save_file(waferid: str, repo):
    fpath = CUR_DIR / f'{waferid}.pkl'
    with open(fpath, 'wb') as f:
        pickle.dump(repo, f, protocol=pickle.HIGHEST_PROTOCOL)

def update(waferid: str, dat_type: str, dat_id: str, id_cols: tuple, filter: pl.DataFrame):
    repo = load_file(waferid)
    if dat_type not in repo:
        repo[dat_type] = {}
    if (dat_id not in repo[dat_type]) or (set(repo[dat_type][dat_id]['id_cols']) != set(id_cols)):
        repo[dat_type][dat_id] = {'id_cols': tuple(id_cols), 'df': filter}
    else:
        old: pl.DataFrame
        old = repo[dat_type][dat_id]['df']
        repo[dat_type][dat_id]['df'] = pl.concat([old, filter]).unique(subset=id_cols, keep='last', maintain_order=True)
    save_file(waferid, repo)

def load_filters(waferid: str, dat_type: str):
    repo = load_file(waferid)
    if dat_type in repo:
        return repo[dat_type]
    return None

def append_filters(meta: dict[str], waferid: str, dat_type: str):
    if (filters := load_filters(waferid=waferid, dat_type=dat_type)) is not None:
        if 'filters' not in meta:
            meta['filters'] = []
        for dat_id, filter in filters.items():
            meta['filters'].append(filter)