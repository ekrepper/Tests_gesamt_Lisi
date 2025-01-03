import matplotlib.pyplot as plt
import numpy as np
import scipy.signal as sc
import Lab3Functions as lf3


#Importieren der Daten
weights, mvc, fatigue = lf3.import_data('\t')

#Umrechnen der Zeit in Sekunden (Abtastrate 1000Hz)
weights['t'] = weights['t']/1000
mvc['t'] = mvc['t']/1000
fatigue['t'] = fatigue['t']/1000


#Offset im emg Datensatz entfernen --> ENTWEDER NOCH DYNAMISCH MACHEN; NICHT HARD GECODET
mvc_offsetclean = mvc['emg'] - 1485
weights_offsetclean = weights['emg'] - 1480
fatigue_offsetclean = fatigue['emg'] - 1490

fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(8, 4))
axes[0].plot(mvc['t'], mvc['emg'])
axes[1].plot(mvc['t'], mvc_offsetclean)
fig.tight_layout()

#Butterworth Filter (20 Hz bis 450 Hz) anwenden
b, a = sc.butter(4, [20/500, 450/500], btype='bandpass')
mvc_emg_filtered = sc.filtfilt(b, a, mvc_offsetclean)
weights_emg_filtered = sc.filtfilt(b, a, weights_offsetclean)
fatigue_emg_filtered = sc.filtfilt(b, a, fatigue_offsetclean)


fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(8, 4))
axes[0].plot(mvc['t'], mvc_offsetclean)
axes[1].plot(mvc['t'], mvc_emg_filtered)
fig.tight_layout()

#Gleichrichten der Daten
mvc_rectified = np.abs(mvc_emg_filtered)
weights_rectified = np.abs(weights_emg_filtered)
fatigue_rectified = np.abs(fatigue_emg_filtered)

fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(8, 4))
axes[0].plot(mvc['t'], mvc_emg_filtered)
axes[1].plot(mvc['t'], mvc_rectified)
fig.tight_layout()

#Einhüllende Bilden: Tiefpass Grenfrequenz 3 Hz 
b, a = sc.butter(4, 3/500, btype='lowpass')
mvc_envelope = sc.filtfilt(b, a, mvc_rectified)
weights_envelope = sc.filtfilt(b, a, weights_rectified)
fatigue_envelope = sc.filtfilt(b, a, fatigue_rectified)

fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(8, 4))
axes[0].plot(mvc['t'], mvc_rectified)
axes[1].plot(mvc['t'], mvc_envelope)
fig.tight_layout()
plt.show()


#Beschriftungen!

#Interaktiv Start und Ende der MVC-Bursts bestimmen
plt.ion()
plt.plot(mvc['t'], mvc_emg_filtered)
plt.show()

mvc_s, mvc_e, weights_s, weights_e, fatigue_s, fatigue_e = lf3.get_bursts(mvc_emg_filtered, weights_emg_filtered, fatigue_emg_filtered)

print(mvc_s, mvc_e, weights_s, weights_e, fatigue_s, fatigue_e)

mvc_elisabeth = np.mean(np.mean(mvc_envelope[mvc_s[0]:mvc_e[0]]) + np.mean(mvc_envelope[mvc_s[1]:mvc_e[1]]) + np.mean(mvc_envelope[mvc_s[2]:mvc_e[2]]))
print(mvc_elisabeth)


#Berechnung der Mittelwerte der einzelnen Weight-Bursts in % des MVC
weights_elisabeth = np.mean(weights_envelope[weights_s[0]:weights_e[0]])/mvc_elisabeth*100
weights_elisabeth2 = np.mean(weights_envelope[weights_s[1]:weights_e[1]])/mvc_elisabeth*100
weights_elisabeth3 = np.mean(weights_envelope[weights_s[2]:weights_e[2]])/mvc_elisabeth*100

print(weights_elisabeth, weights_elisabeth2, weights_elisabeth3)

#Berechnung der Mittelwerte der einzelnen Fatigue-Bursts in % des MVC
fatigue_elisabeth = np.mean(fatigue_envelope[fatigue_s[0]:fatigue_e[0]])/mvc_elisabeth*100
fatigue_elisabeth2 = np.mean(fatigue_envelope[fatigue_s[1]:fatigue_e[1]])/mvc_elisabeth*100
fatigue_elisabeth3 = np.mean(fatigue_envelope[fatigue_s[2]:fatigue_e[2]])/mvc_elisabeth*100

print(fatigue_elisabeth, fatigue_elisabeth2, fatigue_elisabeth3)


# Konstante für die Abtastrate (1000 Hz = 1 ms pro Sample)
sampling_rate = 1000  # Hz

# Isolieren von 0,5 Sekunden am Anfang, in der Mitte und am Ende der Fatigue-Bursts
burst_duration_samples = int(0.5 * sampling_rate)  # 0.5 Sekunden in Samples

# Anfang des Bursts
fatigue_start = fatigue_emg_filtered[fatigue_s[0]:fatigue_s[0] + burst_duration_samples]

# Mitte des Bursts
mid_start = int((fatigue_s[0] + fatigue_e[0]) / 2 - burst_duration_samples / 2)
fatigue_middle = fatigue_emg_filtered[mid_start:mid_start + burst_duration_samples]

# Ende des Bursts
fatigue_end = fatigue_emg_filtered[fatigue_e[0] - burst_duration_samples:fatigue_e[0]]

# Zeitachsen für die roten Markierungen
time_start = fatigue['t'][fatigue_s[0]:fatigue_s[0] + burst_duration_samples]
time_middle = fatigue['t'][mid_start:mid_start + burst_duration_samples]
time_end = fatigue['t'][fatigue_e[0] - burst_duration_samples:fatigue_e[0]]

# Plotten des gesamten EMG-Signals mit hervorgehobenen Intervallen
plt.figure(figsize=(10, 6))
plt.plot(fatigue['t'], fatigue_emg_filtered, label="Fatigue EMG (Filtered)")
plt.plot(time_start, fatigue_start, 'r', label="Start (0.5 s)")
plt.plot(time_middle, fatigue_middle, 'r', label="Middle (0.5 s)")
plt.plot(time_end, fatigue_end, 'r', label="End (0.5 s)")

# Achsenbeschriftung und Legende
plt.xlabel("Time (s)")
plt.ylabel("EMG (a.u.)")
plt.title("Fatigue Filtered EMG Burst Isolated")
plt.legend()
plt.grid()
plt.show()

sfreq = 1000 # Hz
fatigue_combi = np.concatenate((fatigue_start, fatigue_middle, fatigue_end))

power = lf3.get_power(fatigue_combi, sfreq)

#plot power
plt.figure(figsize=(10, 6))
plt.plot(power)
plt.show()
