import matplotlib.pyplot as plt
import numpy as np
import scipy.signal as sc
from scipy.integrate import cumulative_trapezoid
import Lab3Functions as lf3
import os

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


# Pfade für die .npy-Dateien
files = {
    "mvc_s": "mvc_s.npy",
    "mvc_e": "mvc_e.npy",
    "weights_s": "weights_s.npy",
    "weights_e": "weights_e.npy",
    "fatigue_s": "fatigue_s.npy",
    "fatigue_e": "fatigue_e.npy",
}

# Funktion zum Laden der Arrays
def load_or_compute_bursts():
    # Prüfen, ob alle Dateien existieren
    if all(os.path.exists(files[key]) for key in files):
        # Alle Dateien existieren, Arrays laden
        print("Lade gespeicherte Burst-Daten...")
        mvc_s = np.load(files["mvc_s"])
        mvc_e = np.load(files["mvc_e"])
        weights_s = np.load(files["weights_s"])
        weights_e = np.load(files["weights_e"])
        fatigue_s = np.load(files["fatigue_s"])
        fatigue_e = np.load(files["fatigue_e"])
    else:
        # Dateien existieren nicht, get_bursts aufrufen
        print("Berechne Burst-Daten interaktiv...")
        mvc_s, mvc_e, weights_s, weights_e, fatigue_s, fatigue_e = lf3.get_bursts(
            mvc_emg_filtered, weights_emg_filtered, fatigue_emg_filtered
        )

        # Ergebnisse speichern
        np.save(files["mvc_s"], mvc_s)
        np.save(files["mvc_e"], mvc_e)
        np.save(files["weights_s"], weights_s)
        np.save(files["weights_e"], weights_e)
        np.save(files["fatigue_s"], fatigue_s)
        np.save(files["fatigue_e"], fatigue_e)
        print("Burst-Daten wurden gespeichert.")

    return mvc_s, mvc_e, weights_s, weights_e, fatigue_s, fatigue_e

# Aufruf der Funktion
mvc_s, mvc_e, weights_s, weights_e, fatigue_s, fatigue_e = load_or_compute_bursts()


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

# Anfang des 1. Bursts
fatigue_start = fatigue_emg_filtered[fatigue_s[0]:fatigue_s[0] + burst_duration_samples]
# Anfang des 2. Bursts
fatigue_start2 = fatigue_emg_filtered[fatigue_s[1]:fatigue_s[1] + burst_duration_samples]
# Anfang des 3. Bursts
fatigue_start3 = fatigue_emg_filtered[fatigue_s[2]:fatigue_s[2] + burst_duration_samples]

# Mitte des 1. Bursts
mid_start = int((fatigue_s[0] + fatigue_e[0]) / 2 - burst_duration_samples / 2)
fatigue_middle = fatigue_emg_filtered[mid_start:mid_start + burst_duration_samples]
# Mitte des 2. Bursts
mid_start2 = int((fatigue_s[1] + fatigue_e[1]) / 2 - burst_duration_samples / 2)
fatigue_middle2 = fatigue_emg_filtered[mid_start2:mid_start2 + burst_duration_samples]
# Mitte des 3. Bursts
mid_start3 = int((fatigue_s[2] + fatigue_e[2]) / 2 - burst_duration_samples / 2)
fatigue_middle3 = fatigue_emg_filtered[mid_start3:mid_start3 + burst_duration_samples]

# Ende des 1. Bursts
fatigue_end = fatigue_emg_filtered[fatigue_e[0] - burst_duration_samples:fatigue_e[0]]
# Ende des 2. Bursts
fatigue_end2 = fatigue_emg_filtered[fatigue_e[1] - burst_duration_samples:fatigue_e[1]]
# Ende des 3. Bursts
fatigue_end3 = fatigue_emg_filtered[fatigue_e[2] - burst_duration_samples:fatigue_e[2]]

# Zeitachsen für die roten Markierungen
time_start = fatigue['t'][fatigue_s[0]:fatigue_s[0] + burst_duration_samples]
time_middle = fatigue['t'][mid_start:mid_start + burst_duration_samples]
time_end = fatigue['t'][fatigue_e[0] - burst_duration_samples:fatigue_e[0]]

time_start2 = fatigue['t'][fatigue_s[1]:fatigue_s[1] + burst_duration_samples]
time_middle2 = fatigue['t'][mid_start2:mid_start2 + burst_duration_samples]
time_end2 = fatigue['t'][fatigue_e[1] - burst_duration_samples:fatigue_e[1]]

time_start3 = fatigue['t'][fatigue_s[2]:fatigue_s[2] + burst_duration_samples]
time_middle3 = fatigue['t'][mid_start3:mid_start3 + burst_duration_samples]
time_end3 = fatigue['t'][fatigue_e[2] - burst_duration_samples:fatigue_e[2]]


plt.ioff()
plt.figure(figsize=(10, 6))
plt.plot(fatigue['t'], fatigue_emg_filtered, label="Fatigue EMG (Filtered)")
plt.plot(time_start, fatigue_start, 'r')
plt.plot(time_middle, fatigue_middle, 'r')
plt.plot(time_end, fatigue_end, 'r')
plt.plot(time_start2, fatigue_start2, 'g')
plt.plot(time_middle2, fatigue_middle2, 'g')
plt.plot(time_end2, fatigue_end2, 'g')
plt.plot(time_start3, fatigue_start3, 'b')
plt.plot(time_middle3, fatigue_middle3, 'b')
plt.plot(time_end3, fatigue_end3, 'b')
plt.show()

sfreq = 1000 # Hz

power_start, frequency = lf3.get_power(fatigue_start, sfreq)
power_middle, frequency2 = lf3.get_power(fatigue_middle, sfreq)
power_end, frequency3 = lf3.get_power(fatigue_end, sfreq)

power2_start, frequency4 = lf3.get_power(fatigue_start2, sfreq)
power2_middle, frequency5 = lf3.get_power(fatigue_middle2, sfreq)
power2_end, frequency6 = lf3.get_power(fatigue_end2, sfreq)

power3_start, frequency7 = lf3.get_power(fatigue_start3, sfreq)
power3_middle, frequency8 = lf3.get_power(fatigue_middle3, sfreq)
power3_end, frequency9 = lf3.get_power(fatigue_end3, sfreq)

#Filtern: Tiefpass Grenzfrequenz 40 Hz
b, a = sc.butter(4, 40/500, btype='lowpass')
powerstart_filtered = sc.filtfilt(b, a, power_start)
powermid_filtered = sc.filtfilt(b, a, power_middle)
powerend_filtered = sc.filtfilt(b, a, power_end)




fig, axes = plt.subplots(nrows=1, ncols=3, figsize=(12, 6))
axes[0].plot(frequency, power_start)
axes[0].plot(frequency, powerstart_filtered)
axes[1].plot(frequency2, power_middle)
axes[1].plot(frequency2, powermid_filtered)
axes[2].plot(frequency3, power_end)
axes[2].plot(frequency3, powerend_filtered)
fig.tight_layout()
plt.show()

area_freq = cumulative_trapezoid(powerstart_filtered, frequency, initial=0)
total_power = area_freq[-1]
median_freq = frequency[np.where(area_freq >= total_power / 2)[0][0]]

area_freq_mid = cumulative_trapezoid(power_middle, frequency2, initial=0)
total_power_mid = area_freq_mid[-1]
median_freq_mid = frequency4[np.where(area_freq_mid >= total_power_mid / 2)[0][0]]

area_freq_end = cumulative_trapezoid(power2_end, frequency6, initial=0)
total_power_end = area_freq_end[-1]
median_freq_end = frequency3[np.where(area_freq_end >= total_power_end / 2)[0][0]]


#plot power spectrum with median frequency
plt.plot(frequency, powerstart_filtered, color='r')
plt.plot(frequency2, powermid_filtered, color='g')
plt.plot(frequency3, powerend_filtered, color='b')
plt.axvline(median_freq, color='r')
plt.axvline(median_freq_mid, color='g')
plt.axvline(median_freq_end, color='b')
plt.show()

power2start_filtered = sc.filtfilt(b, a, power2_start)
power2mid_filtered = sc.filtfilt(b, a, power2_middle)
power2end_filtered = sc.filtfilt(b, a, power2_end)

# Frequenzspektren für den zweiten Burst
area_freq2_start = cumulative_trapezoid(power2_start, frequency4, initial=0)
total_power2_start = area_freq2_start[-1]
median_freq2_start = frequency4[np.where(area_freq2_start >= total_power2_start / 2)[0][0]]

area_freq2_mid = cumulative_trapezoid(power2_middle, frequency5, initial=0)
total_power2_mid = area_freq2_mid[-1]
median_freq2_mid = frequency5[np.where(area_freq2_mid >= total_power2_mid / 2)[0][0]]

area_freq2_end = cumulative_trapezoid(power2_end, frequency6, initial=0)
total_power2_end = area_freq2_end[-1]
median_freq2_end = frequency6[np.where(area_freq2_end >= total_power2_end / 2)[0][0]]

#plot power spectrum with median frequency
plt.plot(frequency4, power2start_filtered, color='r')
plt.plot(frequency5, power2mid_filtered, color='g')
plt.plot(frequency6, power2end_filtered, color='b')
plt.axvline(median_freq2_start, color='r')
plt.axvline(median_freq2_mid, color='g')
plt.axvline(median_freq2_end, color='b')
plt.show()

# Frequenzspektren für den dritten Burst
area_freq3_start = cumulative_trapezoid(power3_start, frequency7, initial=0)
total_power3_start = area_freq3_start[-1]
median_freq3_start = frequency7[np.where(area_freq3_start >= total_power3_start / 2)[0][0]]

area_freq3_mid = cumulative_trapezoid(power3_middle, frequency8, initial=0)
total_power3_mid = area_freq3_mid[-1]
median_freq3_mid = frequency8[np.where(area_freq3_mid >= total_power3_mid / 2)[0][0]]

area_freq3_end = cumulative_trapezoid(power3_end, frequency9, initial=0)
total_power3_end = area_freq3_end[-1]
median_freq3_end = frequency9[np.where(area_freq3_end >= total_power3_end / 2)[0][0]]


power3start_filtered = sc.filtfilt(b, a, power3_start)
power3mid_filtered = sc.filtfilt(b, a, power3_middle)
power3end_filtered = sc.filtfilt(b, a, power3_end)

#plot power spectrum with median frequency
plt.plot(frequency7, power3start_filtered, color='r')
plt.plot(frequency8, power3mid_filtered, color='g')
plt.plot(frequency9, power3end_filtered, color='b')
plt.axvline(median_freq3_start, color='r')
plt.axvline(median_freq3_mid, color='g')
plt.axvline(median_freq3_end, color='b')
plt.show()