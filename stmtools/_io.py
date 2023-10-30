"""_io.py
"""
from datetime import datetime
import re
import math
from pathlib import Path
from typing import List, Dict
import logging
import xarray as xr
import numpy as np
import pandas as pd
import dask.dataframe as dd
import dask.array as da

logger = logging.getLogger(__name__)


def from_csv(
    file: str | Path,
    space_pattern: str = "^pnt_",
    spacetime_pattern: Dict[str, str] = None,
    coords_cols: List[str] | Dict[str, str] = None,
    output_chunksize: Dict[str, str] = None,
    blocksize: int | str = 200e6,
) -> xr.Dataset:
    """Initiate an STM instance from a csv file.
    The specified csv file will be loaded using `dask.dataframe.read_csv` with a fixed blocksize.

    The columns of the csv file will be classified into coordinates, and data variables.

    This classification is performed by Regular Expression (RE) pattern matching according to
      three variables: `space_pattern`, `spacetime_pattern` and `coords_cols`.

    The following assumptions are made to the column names of the csv file:
        1. All columns with space-only attributes share the same RE pattern in the column names.
          E.g. Latitude, Longitude and height columns are named as "pnt_lat", "pnt_lon" and
          "pnt_height", sharing the same RE pattern "^pnt_";
        2. Per space-time attribute, a common RE pattern is shared by all columns. E.g. for the
          time-series of amplitude data, the column names are "amp_20100101", "amp_20100110",
          "amp_20100119" ..., where "^amp_" is the common RE pattern;
        3. There is no temporal-only (i.e. 1-row attribute) attribute present in the csv file.

    `from_csv` does not retrieve time stamps based on column names. The `time` coordinate of
      the output STM will be a monotonic integer series starting from 0.

    Args:
        file (str | Path): Path to the csv file.
        space_pattern (str, optional): RE pattern to match space attribute columns.
          Defaults to "^pnt_".
        spacetime_pattern (dict | None, optional): A dictionay mapping RE patterns of each
          space-time attribute to corresponding variable names. Defaults to None, which means
          the following map will be applied:
          {"^d_": "deformation", "^a_": "amplitude", "^h2ph_": "h2ph"}.
        coords_cols (list | dict, optional): List of columns to be used as space coordinates.
          When `coords_cols` is a dictionary, a reaming will be performed per coordinates.
          Defaults to None, then the following renaming will be performed:
          "{"pnt_lat": "lat", "pnt_lon": "lon"}"
        output_chunksize (dict | None, optional): Chunksize of the output. Defaults to None,
          then the size of the first chunk in the DaskDataFrame will be used, up-rounding to
          the next 5000.
        blocksize (int | str | None, optional): Blocksize to load the csv.
          Defaults to 200e6 (in bytes). See the documentation of
          [dask.dataframe.read_csv](https://docs.dask.org/en/stable/generated/dask.dataframe.read_csv.html)

    Returns:
        xr.Dataset: Output STM instance
    """

    # Load csv as Dask DataFrame
    _dtypes = pd.read_csv(
        file, nrows=10
    ).dtypes.to_dict()  # Get dtypes from first 10 columns
    ddf = dd.read_csv(file, blocksize=blocksize, dtype=_dtypes)

    # Assign default space-time pattern
    if spacetime_pattern is None:
        spacetime_pattern = {"^d_": "deformation", "^a_": "amplitude", "^h2ph_": "h2ph"}

    # Check all patterns have at least one match
    flag_s_match = _any_match(space_pattern, ddf.columns)  # Any space patter match
    if not flag_s_match:
        raise ValueError(f'Space pattern "{space_pattern}" does not match any column')
    for k in spacetime_pattern.keys():
        flag_st_match = _any_match(k, ddf.columns)  # Any space-time patter match
        if not flag_st_match:
            raise ValueError(
                f'Pattern "{k}" in spacetime_pattern does not match any column'
            )

    # Take the first column and compute the chunk sizes
    # Then convert ddf to dask array
    da_col0 = ddf[ddf.columns[0]].to_dask_array()
    da_col0.compute_chunk_sizes()
    chunks = da_col0.chunks[0]  # take the first dim, which is space (row direction)
    da_all_cols = ddf.to_dask_array(lengths=chunks)

    # Extract time values
    time_values = _convert_times(spacetime_pattern, ddf.columns)

    # Initiate a template STM
    coords = {
        "space": range(da_col0.shape[0]),
        "time": time_values,
    }
    stmat = xr.Dataset(coords=coords)

    # Read csv by columns
    dict_temp_da = dict()  # Temporary dask array collector
    for k in spacetime_pattern.keys():
        dict_temp_da[k] = []

    # Temporaly save time-series columns to lists in dict_temp_da
    for column in ddf.columns:
        idx_col = ddf.columns.get_loc(
            column
        )  # column index for indexing in coverted da
        if re.match(re.compile(space_pattern), column):
            da_pnt = da_all_cols[:, idx_col]
            stmat = stmat.assign({column: (("space"), da_pnt)})
        else:
            flag_column_match = False
            for k in spacetime_pattern.keys():
                if re.match(re.compile(k), column):
                    da_list = dict_temp_da[k]
                    da_list.append(da_all_cols[:, idx_col])
                    dict_temp_da[k] = da_list
                    flag_column_match = True
            if not flag_column_match:  # warning of unmatched columns
                # ignore if the first column, which is the index
                if column != ddf.columns[0]:
                    logger.warning(
                        f'Column "{column}" in the csv file does not match any specified pattern.'
                    )

    # Stack dask arrays in dict_temp_da, assign to STM
    for k, da_list in dict_temp_da.items():
        da_ts = da.stack(da_list)  # Stack on time dimension
        stmat = stmat.assign({spacetime_pattern[k]: (("time", "space"), da_ts)})

    # Rearrage space and time order
    stmat = stmat.transpose("space", "time")

    # Uniform chunking
    if output_chunksize is None:
        space_chunksize = chunks[0]  # take the size of the first ddf chunk
        if len(chunks) > 1:
            # If more than one chunk, use the first chunk size, round to next 5000
            space_chunksize = _round_chunksize(space_chunksize)
        output_chunksize = {"space": space_chunksize, "time": -1}
    stmat = stmat.chunk(output_chunksize)

    # Set coordinates
    if coords_cols is None:
        coords_cols = {"pnt_lat": "lat", "pnt_lon": "lon"}
    if isinstance(coords_cols, dict):
        stmat = stmat.rename(coords_cols)
        stmat = stmat.set_coords(list(coords_cols.values()))
    else:
        stmat = stmat.set_coords(coords_cols)

    return stmat


def _get_col_dtypes():
    pass


def _round_chunksize(size):
    """round size to next 5000"""
    return math.ceil(size / 5000) * 5000


def _any_match(pattern, columns):
    """If a pattern match any columns"""
    flag_match = False  # Any space-time patter match
    for column in columns:
        if re.match(re.compile(pattern), column):
            flag_match = True
            break

    return flag_match


def _extract_times(pattern, columns):
    """Extract times from column names for each variable in spacetime_pattern"""
    times = []
    for column in columns:
        if re.match(re.compile(pattern), column):
            times.append(column.split("_")[-1])
    return times


def _convert_times(spacetime_pattern, columns_names):
    """Convert time series to datetime objects np.datetime64"""

    # Extract times from column names for each variable in spacetime_pattern
    dict_times = {}
    for k in spacetime_pattern.keys():
        dict_times[k] = _extract_times(k, columns_names)

    # Check if all time series have the same length
    len_times = [len(v[0]) for v in dict_times.values()]
    if any(v != len_times[0] for v in len_times):
        raise ValueError("Time series have different lengths")

    # check if all time values in dict_times are same among keys
    if any(v != dict_times[list(dict_times.keys())[0]] for v in dict_times.values()):
        raise ValueError("Time values are different among variables")

    # Check if time format is in the form of YYYYMMDD
    is_format_valid = True
    for t in dict_times.values():
        for tt in t:
            if not re.match(r"\d{8}", tt):
                is_format_valid = False
                logger.warning(
                    f'Time format "{tt}" is not in the form of YYYYMMDD. '
                    "Time values are converted to integers."
                )
                break

    times = list(dict_times.values())[0]
    if is_format_valid:
        times = [datetime.strptime(t, "%Y%m%d") for t in times]
        times = np.array(times)
        # Convert the values to nanosecond precision
        times = times.astype("datetime64[ns]")
    else:
        times = range(len(times))

    return times
