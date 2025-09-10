# Adaptive Rule-based Systolic Peak Detection Algorithm (ArSPA) for Photoplethysmography (PPG) signals.

This package provides preprocessing and peak detection utilities for extracting systolic peaks and interbeat intervals (IBIs) from Empatica E4 BVP data or similar PPG recordings.

ArSPA is designed to be:
Dias-resistant: avoids false detection of diastolic/dicrotic peaks.
Adaptive: dynamically scales thresholds based on local amplitude.
Physiologically constrained: enforces heart rate–based temporal limits.

# Features

PPG preprocessing (detrending, bandpass filtering, Savitzky–Golay smoothing, robust scaling).
Derivative calculation (dPPG) for upstroke validation.
Adaptive systolic peak detection (two-stage algorithm with trough-to-trough segmentation).
Interbeat interval (IBI) calculation in milliseconds.
Example plotting of detected peaks overlaid on the processed PPG signal.

# Repository Structure

PPG-ArSPA/
│
├── arspa folder /
│   ├── __init__.py          # Makes package importable
│   ├── preprocess.py        # Preprocessing functions for PPG - Required before Systolic Peak Detection 
│   ├── peaks.py             # Systolic peak detection algorithm
│
├── README.md                # Project overview and instructions
├── .gitignore               # Ignore build/OS-specific files


# Usage Example 

BASE_DIR = "/path/to/big-ideas-dataset"
SAMPLING_RATE = 64  # Hz
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f"
CHUNKSIZE = 10**6

# --------------------- User's ability to choose which and time  -------------------------
def subject_paths(base_dir: str, subject_id: int):
    """Return correct path to BVP CSV given dataset structure .../<ID3>/<BVP_ID3>.csv"""
    sid = f"{subject_id:03d}"
    bvp_path = os.path.join(base_dir, sid, f"BVP_{sid}.csv")
    return bvp_path

def prompt_time_window():
    """Prompt for start timestamp and duration like 30s, 2m, 10m, 1h."""
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
