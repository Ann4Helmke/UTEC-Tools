"""Import und Download von Excel-Dateien"""

import io

import polars as pl
from loguru import logger

import modules.classes as cl
import modules.general_functions as gf


@gf.func_timer
def import_prefab_excel(file: io.BytesIO | None = None) -> pl.DataFrame:
    """Vordefinierte Excel-Datei importieren"""
    phil: io.BytesIO | str = (
        file or "example_files/Auswertung Stromlastgang - einzelnes Jahr.xlsx"
    )
    mark_ind: str = cl.ExcelMarkers(cl.MarkerType.INDEX).marker_string
    df_messy: pl.DataFrame = pl.read_excel(
        phil,
        sheet_name="Daten",
        xlsx2csv_options={"skip_empty_lines": True, "skip_trailing_columns": True},
        read_csv_options={"has_header": False, "row_count_name": "row"},
    )  # type: ignore
    logger.info(df_messy.head())

    for col in df_messy.columns:
        if mark_ind in df_messy.select(pl.col(col)):
            logger.info(f"Marker found in column '{col}'")
    df_messy.row(by_predicate=pl.col("column_2") == "↓ Index ↓")
    return df_messy
