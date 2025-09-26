import os
import numpy as np
import pandas as pd

# -------------------------------------- User Configuration STEP (1)  -------------------------------------------

BASE_DIR = "/path/to/big-ideas-dataset"
SAMPLING_RATE = 64  # That is the Sampling rate (Hz) at which the raw PPG signal was acquired 
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f"
CHUNKSIZE = 10**6


# ----------------------------------Subject + time window selection ------------------------------------

def subject_paths(base_dir: str, subject_id: int):
    """
    Return correct path to BVP CSV given dataset structure .../<ID3>/<BVP_ID3>.csv
    """
    sid = f"{subject_id:03d}"
    bvp_path = os.path.join(base_dir, sid, f"BVP_{sid}.csv")
    return bvp_path


def prompt_time_window():
    """
    Prompt for start timestamp and duration like 30s, 2m, 10m, 1h.
    """
    while True:
        try:
            start_str = input("Enter start time (YYYY-MM-DD HH:MM:SS.ffffff): ").strip()
            start_time = pd.to_datetime(start_str, format=DATETIME_FORMAT)

            duration_str = input("Enter duration (e.g., 30s, 2m, 10m, 1h): ").strip().lower()
            if duration_str.endswith("s"):
                seconds = int(duration_str[:-1])
            elif duration_str.endswith("m"):
                seconds = int(duration_str[:-1]) * 60
            elif duration_str.endswith("h"):
                seconds = int(duration_str[:-1]) * 3600
            else:
                print("Invalid duration. Use 's', 'm', or 'h'.")
                continue

            end_time = start_time + pd.to_timedelta(seconds, unit="s")
            print(f"Filtering data from {start_time} to {end_time}.")
            return start_time, end_time
        except Exception as e:
            print(f"Error: {e}. Try again.")


def load_bvp_window(bvp_path, start_time, end_time):
    """
    Chunked load of BVP CSV with columns ['datetime','bvp'] filtered to [start,end].
    """
    df = pd.DataFrame()
    try:
        for chunk in pd.read_csv(
            bvp_path,
            chunksize=CHUNKSIZE,
            parse_dates=['datetime'],
            date_format=DATETIME_FORMAT
        ):
            chunk.columns = chunk.columns.str.strip()
            # Basic column sanity
            if 'datetime' not in chunk.columns or 'bvp' not in chunk.columns:
                raise ValueError(f"Expected columns ['datetime','bvp'] in {bvp_path}. Found {list(chunk.columns)}")

            mask = (chunk['datetime'] >= start_time) & (chunk['datetime'] <= end_time)
            part = chunk.loc[mask]
            if not part.empty:
                df = pd.concat([df, part], ignore_index=True)
    except FileNotFoundError:
        raise FileNotFoundError(f"BVP file not found: {bvp_path}")
    except Exception as e:
        raise RuntimeError(f"Error loading BVP: {e}")

    if df.empty:
        raise ValueError("No BVP data found in the specified time range.")

    return df


def compute_ibis_ms(peak_indices, start_time, fs):
    """
    Compute Interbeat Intervals (IBIs) in milliseconds from detected systolic peaks.
    
    Parameters
    ----------
    peak_indices : array-like
        Indices of detected systolic peaks in the PPG signal.
    start_time : pd.Timestamp
        Starting datetime of the analysed segment.
    fs : int
        Sampling rate of the PPG signal (Hz).
    
    Returns
    -------
    pd.DataFrame
        DataFrame with columns:
        - 'timestamp': beat timestamps (datetime)
        - 'ibi_ppg_ms': interbeat interval in milliseconds
    """
    if len(peak_indices) < 2:
        return pd.DataFrame(columns=['timestamp', 'ibi_ppg_ms'])

    peak_times = start_time + pd.to_timedelta(peak_indices / fs, unit="s")
    ibis_ms = pd.Series(peak_times).diff().dt.total_seconds() * 1000.0

    out = pd.DataFrame({
        'timestamp': peak_times[1:],         # skip the first because diff() is NaN
        'ibi_ppg_ms': ibis_ms[1:].round(2)   # round to 2 decimals
    }).reset_index(drop=True)

    return out
