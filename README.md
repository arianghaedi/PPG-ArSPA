# Adaptive Rule-based Systolic Peak Detection Algorithm (ArSPA) for Photoplethysmography (PPG) signals

This overall package provides preprocessing and fiducial peak detection of the PPG Signal, which is originally collected from the Empatica E4 BVP device. It includes step-by-step code and functions for detecting systolic peaks, troughs, and pulse onsets, as well as extracting important cardiovascular features such as:

- Pulse Amplitude  
- Rise Time  
- Decay Time  
- AUC Systole  
- AUC Diastole  
- AUC S/D Ratio  
- AUC Total  

---

## ArSPA Peak detection is designed to be

- **Diastolic-Resistant**: avoids false detection of diastolic/dicrotic peaks.  
- **Adaptive**: dynamically scales thresholds based on local amplitude.  
- **Physiologically constrained**: enforces heart rate–based temporal limits.  

---

## Features

- PPG preprocessing (detrending, bandpass filtering, Savitzky–Golay smoothing, robust scaling).  
- Derivative calculation (dPPG) for upstroke validation.  
- Adaptive systolic peak detection (two-stage algorithm with trough-to-trough segmentation).  
- Interbeat interval (IBI) calculation in milliseconds.  
- Example plotting of detected peaks overlaid on the processed PPG signal.  


## IMPORTANT TO LOOK AT AND IMPLEMENT IN YOUR SCRIPT
# All libraries used throughout the Signal Processing and Peak detection (Step 1)

- import pandas as pd
- import matplotlib.pyplot as plt
- from scipy.signal import butter, filtfilt, detrend,cheby2
- import numpy as np
- from scipy.signal import find_peaks, correlate,savgol_filter
- from sklearn.metrics import mean_absolute_error, mean_squared_error
- from scipy.ndimage import gaussian_filter1d
- import mplcursors
- import seaborn as sns
- from datetime import timedelta
- from sklearn.linear_model import LinearRegression
- from scipy.stats import kruskal
- from scipy.ndimage import binary_dilation
- from scipy.stats import spearmanr
- from scipy.stats import entropy
- from scipy.signal import welch

# Usage Example (Step 2) 

BASE_DIR = "/path/to/big-ideas-dataset"
SAMPLING_RATE = 64  # Hz
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f"
CHUNKSIZE = 10**6

# User's ability to choose which Patient's PPG/BVP Data to look at, along with data and duration they want 

Because the dataset is large and consists of 16 Patients' PPG data measured continuously for 8-10 days, this is done to speed up and look at specific segments more quickly and efficiently 

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
