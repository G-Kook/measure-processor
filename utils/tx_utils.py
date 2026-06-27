import polars as pl
from . import resource_utils

def with_die_xy(df: pl.DataFrame, diex: str, diey: str, alias: str):
    return df.with_columns(
        pl.concat_str([
            pl.lit('('),
            pl.col(diex).cast(pl.Utf8),
            pl.lit(','),
            pl.col(diey).cast(pl.Utf8),
            pl.lit(')')
        ]).cast(pl.Categorical).alias(alias)
    )

def with_radius(df: pl.DataFrame, pid: str, diex: str, diey: str, alias: str):
    return df.join(
        resource_utils.get_die_to_radius(pid=pid),
        on=[diex, diey],
        how='left'
    ).rename({'RADIUS': alias})

def with_additional_info(df: pl.DataFrame, waferid: str):
    out_df = df
    for col, val in resource_utils.get_additional_info(waferid=waferid).items():
        out_df = out_df.with_columns(pl.lit(val).cast(pl.Categorical).alias(col))
    return out_df