# Comprehensive Photoplethysmography (PPG) Signal Processing and Fiducial Point Detection Framework (ArSPA)

This package provides a complete framework for PPG signal preprocessing, adaptive systolic peak detection (ArSPA), and pulse onset identification. It was originally developed for signals collected using the Empatica E4 BVP sensor as part of the 'Big Ideas Lab Glycemic Variability and Wearable Device Dataset'.

## Section 1 - About the Algorithm and Feature Extraction

ArSPA performs physiologically constrained, adaptive detection of fiducial points in the PPG waveform (systolic peaks, troughs, and pulse onsets), enabling accurate derivation of cardiovascular PPG features such as:

1 - Pulse Amplitude: The vertical distance between the systolic peak and its preceding trough, reflecting the change in blood volume per pulse. Reduced amplitude may indicate vasoconstriction or impaired perfusion linked to glucose-induced vascular stiffness.

2 - Rise Time: The time from pulse onset to systolic peak, representing arterial elasticity and the velocity of blood ejection. Prolonged rise time can suggest reduced arterial compliance associated with hyperglycaemia.

3 - Decay Time: The time from systolic peak back to the following trough, indicating venous return and vascular relaxation. Abnormal decay time reflects altered vascular tone influenced by glucose fluctuations.

4 - AUC Systole: The area under the PPG curve from pulse onset to systolic peak, quantifying total blood inflow during systole. It relates to stroke volume and vascular compliance changes under varying glucose levels.

5 - AUC Diastole: The area from systolic peak to the next pulse onset, representing blood outflow and vascular recoil. It provides insight into diastolic function, which can be impaired in early diabetic states.

6 - AUC S/D Ratio: The ratio of systolic to diastolic area, reflecting the balance between cardiac ejection and vascular relaxation. Deviations in this ratio can indicate glucose-related hemodynamic imbalance.

7 - AUC Total: The total area under one full pulse cycle, corresponding to total blood volume change per beat. It integrates systolic and diastolic effects, providing a global marker of vascular responsiveness to glucose dynamics.

---

## Section 2A - Adaptive Systolic Peak Detection Algorithm (ArSPA) Design

- **Diastolic-Resistant**: avoids false detection of diastolic/dicrotic peaks.  
- **Adaptive**: dynamically scales thresholds based on local amplitude.  
- **Physiologically constrained**: enforces heart rate–based temporal limits.  

---

## Section 2B - Key Processing Steps of the Systolic Peak Detection Algorithm 

- PPG preprocessing (detrending, bandpass filtering, Savitzky–Golay smoothing, robust scaling).  
- Derivative calculation (dPPG) for upstroke validation.  
- Adaptive systolic peak detection (two-stage algorithm with trough-to-trough segmentation).  
- Interbeat interval (IBI) calculation in milliseconds.  
- Example plotting of detected peaks overlaid on the processed PPG signal.

## Section 3A -  Folder and File Structure - (Important) 

Your working directory should look like this, where inside a project you have already created in Python, you need to have 7 scripts and a folder named 'arspa'. Now, 6 of the scripts will be inside this folder, which are the following

arspa/

1 -: __init__.py            # Required so Python recognises this as a module
2 - utils.py               # Handles loading data, user input, and IBI calculation
3 - preprocess.py          # Cleans the PPG signal (detrending, filtering, scaling)
4 - peaks.py               # Finds systolic peaks (Adaptive Rule-based Systolic Peak Algorithm)
5 - pulse_onset.py         # Detects pulse onset points using tangent method
6 - plots.py               # Creates plots of peaks and onsets

- big-ideas-dataset/  Example dataset folder (used in this particular project)

Outside this folder, you will then have a script named 'main.py', which is the Main file to run the entire process

## Section 3B - How it works

- main.py is the only script you run. It connects everything together — from loading the PPG data to preprocessing, detecting peaks and onsets, calculating interbeat intervals (IBIs), and finally plotting the results.

- The folder arspa/ contains all supporting scripts. Each script has its own purpose (data handling, signal filtering, peak detection, etc.) and is automatically used when you run main.py.
  
- The folder big-ideas-dataset/ contains the sample PPG data used here, measured from 16 subjects over 8–10 days by the Empatica E4 device.
  
- Sampling rate = 64 Hz, which is already set in the code.

## Section 3C - If You Want to Use a Different Dataset (Please read this Section) 

You can use your own PPG dataset instead of the one provided.
To do that safely, make sure to:

1. Keep the same folder structure.
Just replace 'big-ideas-dataset/' with your dataset folder.

2. Update the dataset path in utils.py: BASE_DIR = "/path/to/your/dataset"
Make sure each subject file follows the same pattern — e.g. 001/BVP_001.csv.
If not, rename them or edit subject_paths() in utils.py to match your folder and file names.

3. Adjust the sampling rate (if needed):
Change this line inside utils.py: SAMPLING_RATE = 64
Replace 64 with the correct sampling frequency of your data.

4. Check column names in your CSV.
The code expects a column called bvp and one for timestamps (like datetime).
If your dataset uses different names (e.g. signal or time), open utils.py and change those column names in the data-loading section (load_bvp_window()).

5. If timestamps look different, adjust: DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f" to match your timestamp format.

6. Once you’ve updated those few lines, you can run: python main.py. And the rest of the processing (preprocessing, peak detection, pulse onset, plotting) will work automatically.


## Section 3D All libraries used throughout the Signal Processing and Peak detection

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


## Section 4 - How to Run the whole Package

1. Open your PyCharm project
2. Make sure your folder structure matches Section 3A
3. Set your dataset path in arspa/utils.py. Look at the lines below in the utils.py 

- BASE_DIR = "/absolute/path/to/big-ideas-dataset"
- SAMPLING_RATE = 64  # Hz for Empatica E4

4. Run main.py.
You’ll be prompted for:

- The subject ID (1–16) - you can choose the specific patient you would like to analyse
- A start time (e.g., 2020-03-06 03:15:00.000000) - this is the format you should write in the terminal window
- A duration (e.g., 10m), you can choose any time, but it is advised for it to be anywhere from 10s to 30m

5. The code will:

- Load only that segment of BVP data.
- Preprocess the signal.
- Detect systolic peaks (ArSPA).
- Compute IBIs.
- Detect pulse onsets.
- Plot peaks and pulse onsets over the waveform.

## Section 5 - Summary of Each Script

1. utils.py: Dataset loading, user input (subject/time), IBI computation
2. preprocess.py: Detrending, bandpass filtering (0.4–3 Hz), Savitzky–Golay smoothing, normalisation
3. peaks.py: ArSPA adaptive systolic peak detection (local maxima, thresholding, HR constraints)
4. pulse_onset.py: Tangent-based pulse onset detection and return of key fiducial points
5. plots.py: Generates publication-ready visualisations of peaks and onsets
6. init.py: Initialises the arspa module for import
7. main.py: Orchestrates entire pipeline from data load to plotting

## Section 6 - Citations

If you use or adapt this repository, please cite:
Ghaedi, A. (2025). Adaptive Rule-based Systolic Peak Detection Algorithm (ArSPA) for Photoplethysmography (PPG) Signals. GitHub Repository. https://github.com/arianghaedi/PPG-ArSPA

## Author and Acknowledgements

This project was conducted as part of the Final-year Biomedical Engineering research project by Arian Ghaedi, under the supervision of Professor Panicos A. Kyriacou at the Research Centre for Biomedical Engineering (RCBE), City, University of London – St George’s, University of London.

Arian Ghaedi is currently a Postgraduate Researcher in the Department of Bioengineering, Imperial College London, based at the South Kensington and White City campuses, London, England, United Kingdom 

City, University of London – St George’s, University of London
Northampton Square, London EC1V 0HB, United Kingdom

Imperial College London, Department of Bioengineering
White City Campus, 80 Wood Lane, London W12 0BZ, United Kingdom

For any questions, collaborations, or requests regarding this work, please contact:
Arian Ghaedi – a.ghaedi25@imperial.ac.uk



Developed for research use in PPG-based cardiovascular and glucose-related feature analysis.
  
