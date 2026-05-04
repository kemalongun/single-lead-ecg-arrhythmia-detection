import pandas as pd
import numpy as np
import plotly.graph_objects as go
from scipy.signal import find_peaks

# Step 1: Load ECG Data
data = pd.read_csv("heart_rate_raw.csv")  # Replace with your file name
time = data["Time (ms)"] / 1000 * 1.37 # Convert time. 1.35 is for calibration of data time to real time.
ecg_signal = data["Heart Signal"]

# Step 2: Normalize the Signal
ecg_signal_normalized = (ecg_signal - np.min(ecg_signal)) / (np.max(ecg_signal) - np.min(ecg_signal))

# Step 3: Detect R-Peaks
peaks, properties = find_peaks(
    ecg_signal_normalized,
    distance=90,  # # Minimum distance between peaks (in samples), ~0.5s or BPM < 120 (91.24  for more precision)
    prominence=0.1  # Adjust for sensitivity to peak heights
)

# Extract R-peak times and values as NumPy arrays
r_peaks_times = np.array(time[peaks])
r_peaks_values = np.array(ecg_signal_normalized[peaks])

# Step 4: Calculate BPM
if len(r_peaks_times) > 1:
    r_intervals = np.diff(r_peaks_times)  # Time intervals between R-peaks (in seconds)
    bpm = 60 / r_intervals  # Calculate BPM for each interval
    average_bpm = np.mean(bpm)
    print(f"Average BPM: {average_bpm:.2f}")
else:
    print("Not enough R-peaks detected to calculate BPM.")
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

# Step 7: Create Interactive Plot for Raw ECG Signal

# Create the figure for the raw signal
fig_raw = go.Figure()

# Add the raw ECG signal trace (for comparison)
fig_raw.add_trace(go.Scatter(
    x=time,
    y=ecg_signal,
    mode='lines',
    name='Raw Heart Signal',
    line=dict(color='gray')
))

# Add markers for R-peaks on the raw signal
fig_raw.add_trace(go.Scatter(
    x=r_peaks_times,
    y=ecg_signal.loc[peaks],  # Raw signal R-peaks
    mode='markers',
    name='R-peaks',
    marker=dict(color='red', size=8)
))

# Customize layout for raw ECG plot
fig_raw.update_layout(
    title="Raw ECG Signal with R-Peaks",
    xaxis_title="Time (s)",
    yaxis_title="Signal Amplitude",
    showlegend=True,
    hovermode="x unified",  # Display data on hover
    template="plotly_dark",  # Optional: dark theme
    margin=dict(l=40, r=40, t=40, b=40)
)

# Show the raw ECG plot
fig_raw.show()

# Step 8: Create Interactive Plot for Normalized ECG Signal

# Create the figure for the normalized signal
fig_normalized = go.Figure()

# Add the normalized ECG signal trace
fig_normalized.add_trace(go.Scatter(
    x=time,
    y=ecg_signal_normalized,
    mode='lines',
    name='Normalized ECG Signal',
    line=dict(color='blue')
))

# Add markers for R-peaks on the normalized signal
fig_normalized.add_trace(go.Scatter(
    x=r_peaks_times,
    y=r_peaks_values,  # Normalized signal R-peaks
    mode='markers',
    name='R-peaks',
    marker=dict(color='red', size=8)
))

# Customize layout for normalized ECG plot
fig_normalized.update_layout(
    title="Normalized ECG Signal with R-Peaks",
    xaxis_title="Time (s)",
    yaxis_title="Signal Amplitude",
    showlegend=True,
    hovermode="x unified",  # Display data on hover
    template="plotly_dark",  # Optional: dark theme
    margin=dict(l=40, r=40, t=40, b=40)
)

# Show the normalized ECG plot
fig_normalized.show()
