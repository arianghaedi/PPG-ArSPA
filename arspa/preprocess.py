import numpy as np
from scipy.signal import butter, filtfilt, detrend, savgol_filter

#---------------------------------- Preprocessing Stage of the PPG Signal (STEP 2) ---------------------------

"""
Preprocessing of the PPG signals (STEP 2):
- Bandpass filtering
- Detrending
- Savitzky-Golay smoothing
- Robust scaling
- Derivative calculation
"""


def butter_bandpass_filter(data, lowcut, highcut, fs, order=4):
    """Butterworth bandpass with reflect-padding to reduce edge artefacts."""
    nyquist = 0.5 * fs
    low = lowcut / nyquist
    high = highcut / nyquist

    # reflect pad ~0.1 s to stabilise filtfilt edges
    ext = int(0.1 * fs)
    x = np.pad(np.asarray(data), (ext, ext), mode='reflect')

    b, a = butter(order, [low, high], btype='band')
    y = filtfilt(b, a, x)
    return y[ext:-ext]

def preprocess_ppg(df, fs):
    """Detrend -> bandpass (0.4–3.0 Hz) -> Savitzky-Golay -> robust scaling."""
    raw = df['bvp'].values.astype(float)

    # 1) detrend
    detr = detrend(raw)

    # 2) bandpass
    filt = butter_bandpass_filter(detr, lowcut=0.4, highcut=3.0, fs=fs, order=4)

    # 3) Savitzky–Golay smoothing
    smooth = savgol_filter(filt, window_length=5, polyorder=2)

    # 4) robust scaling to match raw median amplitude scale
    raw_med = np.median(np.abs(raw))
    smooth_med = np.median(np.abs(smooth))
    scale = (raw_med / smooth_med) if smooth_med != 0 else 1.0
    scaled = smooth * scale

    df = df.copy()
    df['scaled_bvp'] = scaled

    # 5) derivative (for peak validation)
    df['dppg'] = savgol_filter(scaled, window_length=5, polyorder=2, deriv=1, delta=1/fs)
    return df
