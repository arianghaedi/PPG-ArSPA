# STEP 5 - Last part of peak detection and Signal Processing 
"""
main.py
-------
Brings everything together:
1. Patient + time window selection
2. Load BVP data
3. Preprocess
4. Adaptive systolic peak detection
5. IBI calculation
6. Pulse onset detection
7. Plotting results
"""

import matplotlib.pyplot as plt
import numpy as np

from arspa.utils import BASE_DIR, SAMPLING_RATE, subject_paths, prompt_time_window, load_bvp_window, compute_ibis_ms
from arspa.preprocess import preprocess_ppg
from arspa.peaks import systolic_only_peak_detection
from arspa.pulse_onset import detect_pulse_onsets
from arspa.plots import plot_peaks_and_onsets


def main():
    # ---- patient selection
    while True:
        try:
            subject_id = int(input("Enter patient ID (1–16): ").strip())
            if 1 <= subject_id <= 16:
                break
            print("Please enter an integer in [1, 16].")
        except Exception:
            print("Invalid input. Enter an integer 1–16.")

    bvp_path = subject_paths(BASE_DIR, subject_id)
    print(f"Using BVP file: {bvp_path}")

    # ---- time window
    start_time, end_time = prompt_time_window()

    # ---- load data
    bvp_df = load_bvp_window(bvp_path, start_time, end_time)

    # ---- preprocess
    bvp_df = preprocess_ppg(bvp_df, SAMPLING_RATE)

    # ---- systolic peak detection
    peaks = systolic_only_peak_detection(
        bvp_df['scaled_bvp'].values,
        bvp_df['dppg'].values,
        fs=SAMPLING_RATE
    )

    # ---- IBIs
    ibis = compute_ibis_ms(peaks, start_time, SAMPLING_RATE)

    # ---- Pulse Onsets
    results = detect_pulse_onsets(bvp_df, peaks, SAMPLING_RATE)

    # ---- Final Plot
    plot_peaks_and_onsets(bvp_df, peaks, results)


if __name__ == "__main__":
    main()
