def plot_peaks_and_onsets(bvp_df, peaks, results):
    """
    Plot scaled PPG signal with systolic peaks, local minima, max slopes, and pulse onsets.
    """
    pulse_onsets = results["pulse_onsets"]
    local_mins = results["local_mins"]
    max_slopes = results["max_slopes"]

    plt.figure(figsize=(14, 6))
    plt.plot(bvp_df['datetime'], bvp_df['scaled_bvp'], color='black', label='Scaled PPG')

    if len(peaks) > 0:
        plt.scatter(bvp_df['datetime'].iloc[peaks],
                    bvp_df['scaled_bvp'].iloc[peaks],
                    color='red', s=18, label='Systolic Peaks')

    if len(local_mins) > 0:
        plt.scatter(bvp_df['datetime'].iloc[local_mins],
                    bvp_df['scaled_bvp'].iloc[local_mins],
                    color='blue', marker='o', label='Local Minima')

    if len(max_slopes) > 0:
        plt.scatter(bvp_df['datetime'].iloc[max_slopes],
                    bvp_df['scaled_bvp'].iloc[max_slopes],
                    color='green', marker='x', label='Max Slopes')

    if len(pulse_onsets) > 0:
        plt.scatter(bvp_df['datetime'].iloc[pulse_onsets],
                    bvp_df['scaled_bvp'].iloc[pulse_onsets],
                    color='orange', marker='d', label='Pulse Onsets')

    plt.title("PPG with Systolic Peaks & Pulse Onsets")
    plt.xlabel("Time")
    plt.ylabel("Amplitude")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()
