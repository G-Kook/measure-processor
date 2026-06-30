import polars as pl
from typing import Literal
import math

def replace_nan_vth(df: pl.DataFrame, vth: str | list[str]):
    if isinstance(vth, list):
        col = [pl.when(pl.col(vt).abs()<9).then(pl.col(vt)).otherwise(None).alias(vt) for vt in vth]
    elif isinstance(vth, str):
        col = pl.when(pl.col(vth).abs()<9).then(pl.col(vth)).otherwise(None).alias(vth)
    else:
        raise Exception('vth must be str or list[str].')
    return df.with_columns(col)

def with_x_crossing_target_y(df: pl.DataFrame, index: list[str], x: str, y: str, yscale: Literal['linear', 'log10'], target: float, alias: str, alias_slope: str|None = None):
    if yscale not in ('linear', 'log10'):
        raise ValueError("yscale must be 'linear' or 'log10'")

    Y_EXPR = pl.col(y) if yscale == 'linear' else pl.col(y).log10()
    TGT = target if yscale == 'linear' else math.log10(target)
    _df = df.sort(
            index+[x]
        ).with_columns(
            (Y_EXPR-TGT).alias('d'),
            pl.col(x).shift(1).over(index).alias('x_prev'),
            Y_EXPR.shift(1).over(index).alias('y_prev'),
        ).filter(
            (pl.col('d')*pl.col('d').shift(1).over(index))<=0
        )

    addcols_exprs = [(pl.col('x_prev') + (TGT-pl.col('y_prev')) * (pl.col(x)-pl.col('x_prev')) / (Y_EXPR-pl.col('y_prev'))).alias(alias)]
    agg_exprs = [pl.col(alias).first()]
    if alias_slope is not None:
        addcols_exprs.append(((Y_EXPR-pl.col('y_prev')) / (pl.col(x)-pl.col('x_prev'))).alias(alias_slope))
        agg_exprs.append(pl.col(alias_slope).first())
    return _df.with_columns(addcols_exprs).group_by(index).agg(agg_exprs)
