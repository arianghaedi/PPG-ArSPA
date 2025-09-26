# PPG Pulse Onset (Step 4)

import numpy as np
import matplotlib.pyplot as plt

def detect_pulse_onsets(bvp_df, peaks, fs):
    """
    Detect pulse onsets from a preprocessed PPG signal.
    
    Parameters
    ----------
    bvp_df : pd.DataFrame
        Must include columns:
        - 'scaled_bvp': preprocessed PPG signal
        - 'dppg': first derivative of the PPG
        - 'datetime': timestamps
    peaks : array-like
        Indices of detected systolic peaks.
    fs : int
        Sampling rate (Hz).
    
    Returns
    -------
    dict
        Dictionary with:
        - 'pulse_onsets': indices of detected pulse onsets
        - 'local_mins': indices of local minima
        - 'max_slopes': indices of max slopes
    """

    pulse_onsets = []
    local_mins = []
    max_slopes = []

    window_size = int(0.75 * fs)  # search window (~0.75s)

    for peak in peaks:
        # Find last max slope (dPPG maximum) before the systolic peak
        slope_candidates = np.where(
            (np.r_[False, bvp_df['dppg'].values[1:] > bvp_df['dppg'].values[:-1]] &
             np.r_[bvp_df['dppg'].values[:-1] > bvp_df['dppg'].values[1:], False]) &
            (np.arange(len(bvp_df)) < peak)
        )[0]
        if len(slope_candidates) == 0:
            continue
        max_slope_idx = slope_candidates[-1]

        # Local minimum (trough) before slope
        start_search = max(0, max_slope_idx - window_size)
        local_min_idx = start_search + np.argmin(bvp_df['scaled_bvp'].values[start_search:max_slope_idx])
        trough_amp = bvp_df['scaled_bvp'].values[local_min_idx]

        # Systolic slope point ~30% between trough and slope
        systolic_slope_idx = local_min_idx + int(0.3 * (max_slope_idx - local_min_idx))
        if systolic_slope_idx >= max_slope_idx:
            systolic_slope_idx = max_slope_idx - 1

        # Tangent slope m using centered difference
        T = 1 / fs
        m = (bvp_df['scaled_bvp'].values[systolic_slope_idx + 1] -
             bvp_df['scaled_bvp'].values[systolic_slope_idx - 1]) / (2 * T)
        if abs(m) < 1e-6:
            continue

        # Intercept c
        c = bvp_df['scaled_bvp'].values[systolic_slope_idx] - m * systolic_slope_idx

        # Intersection with horizontal line at trough_amp
        intersection_x = (trough_amp - c) / m

        if local_min_idx <= intersection_x <= max_slope_idx:
            pulse_onsets.append(int(round(intersection_x)))
            local_mins.append(local_min_idx)
            max_slopes.append(max_slope_idx)

    pulse_onsets = np.array(pulse_onsets)
    local_mins = np.array(local_mins)
    max_slopes = np.array(max_slopes)

    return {
        "pulse_onsets": pulse_onsets,
        "local_mins": local_mins,
        "max_slopes": max_slopes,
    }



