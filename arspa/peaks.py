import numpy as np
from scipy.signal import find_peaks

def systolic_only_peak_detection(signal, dppg, fs,
                                 alpha=0.4, min_threshold=0.1,
                                 hr_min=40, hr_max=180,
                                 early_frac=0.80,    # Accept only first 80% of cycle (avoids diastolic peaks being detected)
                                 lookahead_ms=0,     # not used in this version (kept for signature stability)
                                 dppg_pct=80,        # upstroke gating
                                 guard_ms=40,        # ignore a few samples near troughs
                                 prom_frac=0.25):    # trough prominence fraction of median |amp|
    """
  Two-stage algorithm:
      1) Candidate peaks with adaptive amplitude + derivative gating.
      2) Segment trough→trough; keep ONE tallest early-cycle peak per segment.
         Falls back to global max if no candidates.
    """
    x  = np.asarray(signal)
    d1 = np.asarray(dppg)
    n  = len(x)

    # ---- spacing constraints from HR limits ----
    max_distance = int(fs * (60.0 / hr_min))
    min_distance = int(fs * (60.0 / hr_max) * 1.30)  # 30% buffer

    median_amplitude = np.median(np.abs(x))
    cap_amplitude    = median_amplitude * 3.0

    # ---- Stage 1: initial candidates ----
    candidates = []
    for i in range(1, n - 1):
        if not (x[i] > x[i-1] and x[i] > x[i+1]):  # local maximum
            continue

        ls = max(0, i - 5)
        le = min(n, i + 5)
        local_amp = np.mean(np.abs(x[ls:le]))
        local_amp = min(local_amp, cap_amplitude)
        dyn_thr   = max(alpha * local_amp, min_threshold * 0.5)
        if x[i] <= dyn_thr:
            continue

        if candidates and (i - candidates[-1]) < int(0.8 * min_distance):
            continue
        if candidates and (i - candidates[-1]) > int(1.2 * max_distance) and (i - candidates[-1]) < int(2 * max_distance):
            pass

        wstart = max(0, i - int(0.3 * fs))
        local_d = d1[wstart:i]
        if local_d.size == 0:
            continue
        if np.any(local_d > np.percentile(local_d, dppg_pct)):
            candidates.append(i)

    if len(candidates) == 0:
        return np.array([], dtype=int)
    candidates = np.array(candidates, dtype=int)

    # ---- Stage 2: trough→trough segmentation ----
    trough_prom     = float(prom_frac * median_amplitude) if median_amplitude > 0 else 0.01
    trough_min_dist = int(fs * (60.0 / hr_max) * 0.8)
    troughs, _      = find_peaks(-x, distance=trough_min_dist, prominence=trough_prom)

    if len(troughs) < 2:
        final_peaks = []
        for idx in candidates:
            if not final_peaks or (idx - final_peaks[-1]) >= min_distance:
                final_peaks.append(idx)
        return np.array(final_peaks, dtype=int)

    guard = int((guard_ms / 1000.0) * fs)
    final_peaks = []

    for a, b in zip(troughs[:-1], troughs[1:]):
        start = min(n - 1, a + guard)
        end   = max(start + 1, b - guard)
        if end <= start:
            continue

        early_end = start + int(early_frac * (end - start))
        if early_end <= start:
            continue

        seg_cands = candidates[(candidates >= start) & (candidates < early_end)]

        if seg_cands.size > 0:
            best = seg_cands[np.argmax(x[seg_cands])]
        else:
            rel = np.argmax(x[start:early_end])
            best = start + int(rel)

        if not final_peaks or (best - final_peaks[-1]) >= int(0.8 * min_distance):
            final_peaks.append(int(best))

    return np.array(final_peaks, dtype=int)
