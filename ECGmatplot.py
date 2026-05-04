import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks

# Step 1: Load ECG Data
data = pd.read_csv("heart_rate_raw.csv")  # Read the csv file which is written by Processing
time = data["Time (ms)"] / 1000 * 1.37 # Convert time. 1.35 is for calibration of data time to real time.
ecg_signal = data["Heart Signal"]

# Step 2: Normalize the Signal
ecg_signal = (ecg_signal - np.min(ecg_signal)) / (np.max(ecg_signal) - np.min(ecg_signal))

# Step 3: R-peaks detection algorithm
peaks, properties = find_peaks(
    ecg_signal,
    distance=90,  # Minimum distance between peaks (in samples), ~0.5s or BPM < 120 (91.24 for more precision)
    prominence=0.1  # Sensitivity of peak heights
)

# Extract R-peak times and values as arrays
r_peaks_times = np.array(time[peaks])
r_peaks_values = np.array(ecg_signal[peaks])

# Step 4: Calculate BPM with R-peaks
if len(r_peaks_times) > 1:
    r_intervals = np.diff(r_peaks_times)  # Time intervals between R-peaks (in seconds)
    bpm = 60 / r_intervals  # Calculate BPM for each interval
    average_bpm = np.mean(bpm)
    print(f"Average BPM: {average_bpm:.2f}")
else:
    print("Not enough R-peaks detected to calculate BPM.") # Sends error message if R-peaks are not detected
    bpm = []
    r_intervals = []

# Step 5: Detect Arrhythmia Risks
tachycardia_threshold = 100  # BPM > 100
bradycardia_threshold = 60   # BPM < 60
irregular_threshold = 0.16    # Indicating AF. Ranging 3.25% to 16% R-R interval irregularity (pRRx)
premature_threshold = 0.8    # Premature beats indicating contraction if R-R interval < 80% of mean****
skipped_threshold = 1.9      # Skipped beats if R-R interval > 190% of mean (5% margin of error on both R's)

# Analyze risks
arrhythmia_risks = {
    "Tachycardia": False,
    "Bradycardia": False,
    "Atrial Fibrillation (Irregular Rhythm)": False,
    "Premature Beats (PVCs or PACs)": False,
    "Skipped Beats": False
}

# Lists to store specific events
irregular_indices = []
premature_indices = []
skipped_indices = []

# Tachycardia/Bradycardia Detection
for rate in bpm:
    if rate > tachycardia_threshold:
        arrhythmia_risks["Tachycardia"] = True
    elif rate < bradycardia_threshold:
        arrhythmia_risks["Bradycardia"] = True

# Irregular Rhythm (Atrial Fibrillation) Detection
if len(r_intervals) > 1:
    rr_mean = np.mean(r_intervals)
    for i, rr in enumerate(r_intervals):
        if abs(rr - rr_mean) > irregular_threshold * rr_mean:
            irregular_indices.append(i)
    if len(irregular_indices) > 0.16 * len(r_intervals):  # If >20% intervals are irregular
        arrhythmia_risks["Atrial Fibrillation (Irregular Rhythm)"] = True

# Premature Beats Detection
for i, rr in enumerate(r_intervals):
    if rr < premature_threshold * rr_mean:
        premature_indices.append(i)
if premature_indices:
    arrhythmia_risks["Premature Beats (PVCs or PACs)"] = True

# Skipped Beats Detection
for i, rr in enumerate(r_intervals):
    if rr > skipped_threshold * rr_mean:
        skipped_indices.append(i)
if skipped_indices:
    arrhythmia_risks["Skipped Beats"] = True

# Step 6: Output Risk Analysis
print("\nHeart Rate Abnormalities and Arrhythmia Risk Analysis:")
for arrhythmia, risk in arrhythmia_risks.items():
    status = "At Risk" if risk else "No Risk"
    print(f"{arrhythmia}: {status}")

plt.figure(figsize=(12, 7))  # Increase figure size for better visualization

# Subplot 1: Raw Heart Signal (Custom grid, black signal, red grid lines)
plt.subplot(2, 1, 1)  # 2 rows, 1 column, position 1
plt.plot(time, data["Heart Signal"], label="Raw Heart Signal", color="black")
plt.title("Raw Heart Signal")
plt.xlabel("Time (s)")
plt.ylabel("Amplitude")
plt.ylim(0, 800)  # Adjust based on raw signal range (e.g., 10-bit ADC range)

# Custom gridlines for the raw ECG signal plot
plt.grid(True, which='both', axis='both', linestyle='-', color='red', linewidth=0.5)

# Custom gridlines for real ECG behavior (0.05s for small cubes, 0.2s for thick cubes)
plt.xticks(np.arange(0, max(time), 0.05))  # Small grid cubes at every 0.05 seconds
plt.yticks(np.arange(0, 1025, 100))  # Adjust as per signal range
plt.gca().set_xticklabels(np.arange(0, max(time), 0.05), fontsize=10)

# Thick gridlines every 0.2 seconds
for i in range(1, int(max(time) / 0.2) + 1):
    plt.axvline(x=i * 0.2, color='black', linewidth=2, linestyle='--')

plt.legend(loc="upper right")

# Subplot 2: Normalized ECG Signal with R-Peaks
plt.subplot(2, 1, 2)  # 2 rows, 1 column, position 2
plt.plot(time, ecg_signal, label="Normalized ECG Signal", color="blue")
plt.scatter(r_peaks_times, r_peaks_values, color="red", label="R-peaks", zorder=5)

# Mark irregular intervals
for i in irregular_indices:
    plt.axvspan(r_peaks_times[i], r_peaks_times[i + 1], color="orange", alpha=0.3, label="Irregular Interval")

# Mark premature beats
for i in premature_indices:
    plt.axvline(r_peaks_times[i + 1], color="purple", linestyle="--", label="Premature Beat")

# Mark skipped beats
for i in skipped_indices:
    plt.axvline(r_peaks_times[i + 1], color="green", linestyle="--", label="Skipped Beat")

plt.title("Normalized ECG Signal with Detected R-Peaks and Arrhythmias")
plt.xlabel("Time (s)")
plt.ylabel("Normalized Amplitude")
plt.ylim(0, 1)  # Normalized range
plt.grid()
plt.legend(loc="upper right")

# Show the plots
plt.tight_layout()  # Adjust layout to prevent overlap
plt.show()
