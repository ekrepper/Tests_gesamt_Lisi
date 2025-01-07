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


#Offset im emg Datensatz entfernen --> NOCH DYNAMISCH MACHEN; NICHT HARD GECODET
mvc_offsetclean = mvc['emg'] - 1485
weights_offsetclean = weights['emg'] - 1480
fatigue_offsetclean = fatigue['emg'] - 1490


#Butterworth Filter (20 Hz bis 450 Hz) anwenden
b, a = sc.butter(4, [20/500, 450/500], btype='bandpass')
mvc_emg_filtered = sc.filtfilt(b, a, mvc_offsetclean)
weights_emg_filtered = sc.filtfilt(b, a, weights_offsetclean)
fatigue_emg_filtered = sc.filtfilt(b, a, fatigue_offsetclean)


#Gleichrichten der Daten
mvc_rectified = np.abs(mvc_emg_filtered)
weights_rectified = np.abs(weights_emg_filtered)
fatigue_rectified = np.abs(fatigue_emg_filtered)

#Einhüllende Bilden: Tiefpass Grenfrequenz 3 Hz 
b, a = sc.butter(4, 3/500, btype='lowpass')
mvc_envelope = sc.filtfilt(b, a, mvc_rectified)
weights_envelope = sc.filtfilt(b, a, weights_rectified)
fatigue_envelope = sc.filtfilt(b, a, fatigue_rectified)

# MVC [emg] als einzelner Plot
plt.figure(figsize=(10, 6))
plt.plot(mvc['t'], mvc['emg'], label="Rohes Signal")
#plt.title("MVC - Rohes EMG Signal")
plt.ylabel("EMG / a.u.")
plt.xlabel("Zeit / s")
plt.legend()
plt.grid()
plt.show()

# MVC - offsetbereinigt, gefiltert, gleichgerichtet, Einhüllende in einem 2x2 Subplot
fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(12, 8))

# MVC - offsetbereinigt
axes[0, 0].plot(mvc['t'], mvc_offsetclean, label="Offsetbereinigtes EMG-Signal", color='blue')
axes[0, 0].set_title("MVC - Offsetbereinigt")
axes[0, 0].set_xlabel("Zeit / s")
axes[0, 0].set_ylabel("EMG / a.u.")
axes[0, 0].grid()
axes[0, 0].legend()

# MVC - gefiltert
axes[0, 1].plot(mvc['t'], mvc_emg_filtered, label="Gefiltertes EMG-Signal", color='orange')
axes[0, 1].set_title("MVC - Gefiltert")
axes[0, 1].set_xlabel("Zeit / s")
axes[0, 1].set_ylabel("EMG / a.u.")
axes[0, 1].grid()
axes[0, 1].legend()

# MVC - gleichgerichtet
axes[1, 0].plot(mvc['t'], mvc_rectified, label="Gleichgerichtetes EMG-Signal", color='green')
axes[1, 0].set_title("MVC - Gleichgerichtet")
axes[1, 0].set_xlabel("Zeit / s")
axes[1, 0].set_ylabel("EMG / a.u.")
axes[1, 0].grid()
axes[1, 0].legend()

# MVC - Einhüllende
axes[1, 1].plot(mvc['t'], mvc_envelope, label="Einhüllende des EMG-Signals", color='red')
axes[1, 1].set_title("MVC - Einhüllende")
axes[1, 1].set_xlabel("Zeit / s")
axes[1, 1].set_ylabel("EMG / a.u.")
axes[1, 1].grid()
axes[1, 1].legend()

# Layout anpassen
fig.tight_layout()
plt.legend()
plt.savefig("Plots-Experiment1-MVC.svg", format="svg")
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

plt.ion()
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
print('MVC Elisabeth',mvc_elisabeth)


#Berechnung der Mittelwerte der einzelnen Weight-Bursts in % des MVC
weights_elisabeth = np.mean(weights_envelope[weights_s[0]:weights_e[0]])/mvc_elisabeth*100
weights_elisabeth2 = np.mean(weights_envelope[weights_s[1]:weights_e[1]])/mvc_elisabeth*100
weights_elisabeth3 = np.mean(weights_envelope[weights_s[2]:weights_e[2]])/mvc_elisabeth*100

print("2.5 kg", weights_elisabeth, "5 kg", weights_elisabeth2, "10 kg", weights_elisabeth3)

weights_elisabeth = [weights_elisabeth, weights_elisabeth2, weights_elisabeth3]  # Anteil % von MVC
weights = [2.5, 5, 10]  # Gewichte in kg

# Erstelle den Balkendiagramm
fig, ax = plt.subplots(figsize=(8, 6))
bars = ax.bar(weights, weights_elisabeth, label='Anteil % von MVC', color='lightblue')

# Prozentsätze in den Balken anzeigen
for bar, value in zip(bars, weights_elisabeth):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width() / 2, height / 2, f'{value:.1f}%', ha='center', va='center', fontsize=12, color='black')

# Achsentitel und Beschriftungen
ax.set_xlabel('Gewicht / kg')
ax.set_ylabel('% von MVC')
ax.set_xticks(weights)
ax.set_ylim(0, 100)
ax.grid()
ax.legend()

# Diagramm anzeigen
plt.tight_layout()
plt.show()

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
plt.plot(fatigue['t'], fatigue_emg_filtered, label="Fatigue-Signal mit Burst-Markierungen")
plt.plot(time_start, fatigue_start, 'r')
plt.plot(time_middle, fatigue_middle, 'r')
plt.plot(time_end, fatigue_end, 'r')
plt.plot(time_start2, fatigue_start2, 'r')
plt.plot(time_middle2, fatigue_middle2, 'r')
plt.plot(time_end2, fatigue_end2, 'r')
plt.plot(time_start3, fatigue_start3, 'r')
plt.plot(time_middle3, fatigue_middle3, 'r')
plt.plot(time_end3, fatigue_end3, 'r')
plt.xlabel("Zeit / s")
plt.ylabel("EMG / a.u.")
plt.legend()
plt.show()

sfreq = 1000 # Hz

# Berechnung des Leistungsspektrums für die drei Abschnitte der Fatigue-Bursts
power_start, frequency = lf3.get_power(fatigue_start, sfreq)
power_middle, frequency2 = lf3.get_power(fatigue_middle, sfreq)
power_end, frequency3 = lf3.get_power(fatigue_end, sfreq)

power2_start, frequency4 = lf3.get_power(fatigue_start2, sfreq)
power2_middle, frequency5 = lf3.get_power(fatigue_middle2, sfreq)
power2_end, frequency6 = lf3.get_power(fatigue_end2, sfreq)

power3_start, frequency7 = lf3.get_power(fatigue_start3, sfreq)
power3_middle, frequency8 = lf3.get_power(fatigue_middle3, sfreq)
power3_end, frequency9 = lf3.get_power(fatigue_end3, sfreq)

# Filtern: Tiefpass Grenzfrequenz 40 Hz
b, a = sc.butter(4, 40/500, btype='lowpass')
powerstart_filtered = sc.filtfilt(b, a, power_start)
powermid_filtered = sc.filtfilt(b, a, power_middle)
powerend_filtered = sc.filtfilt(b, a, power_end)

power2start_filtered = sc.filtfilt(b, a, power2_start)
power2mid_filtered = sc.filtfilt(b, a, power2_middle)
power2end_filtered = sc.filtfilt(b, a, power2_end)

power3start_filtered = sc.filtfilt(b, a, power3_start)
power3mid_filtered = sc.filtfilt(b, a, power3_middle)
power3end_filtered = sc.filtfilt(b, a, power3_end)

# Medianfrequenzen berechnen
area_freq = cumulative_trapezoid(powerstart_filtered, frequency, initial=0)
total_power = area_freq[-1]
median_freq = frequency[np.where(area_freq >= total_power / 2)[0][0]]

area_freq_mid = cumulative_trapezoid(powermid_filtered, frequency2, initial=0)
total_power_mid = area_freq_mid[-1]
median_freq_mid = frequency2[np.where(area_freq_mid >= total_power_mid / 2)[0][0]]

area_freq_end = cumulative_trapezoid(powerend_filtered, frequency3, initial=0)
total_power_end = area_freq_end[-1]
median_freq_end = frequency3[np.where(area_freq_end >= total_power_end / 2)[0][0]]

area_freq2_start = cumulative_trapezoid(power2start_filtered, frequency4, initial=0)
total_power2_start = area_freq2_start[-1]
median_freq2_start = frequency4[np.where(area_freq2_start >= total_power2_start / 2)[0][0]]

area_freq2_mid = cumulative_trapezoid(power2mid_filtered, frequency5, initial=0)
total_power2_mid = area_freq2_mid[-1]
median_freq2_mid = frequency5[np.where(area_freq2_mid >= total_power2_mid / 2)[0][0]]

area_freq2_end = cumulative_trapezoid(power2end_filtered, frequency6, initial=0)
total_power2_end = area_freq2_end[-1]
median_freq2_end = frequency6[np.where(area_freq2_end >= total_power2_end / 2)[0][0]]

area_freq3_start = cumulative_trapezoid(power3start_filtered, frequency7, initial=0)
total_power3_start = area_freq3_start[-1]
median_freq3_start = frequency7[np.where(area_freq3_start >= total_power3_start / 2)[0][0]]

area_freq3_mid = cumulative_trapezoid(power3mid_filtered, frequency8, initial=0)
total_power3_mid = area_freq3_mid[-1]
median_freq3_mid = frequency8[np.where(area_freq3_mid >= total_power3_mid / 2)[0][0]]

area_freq3_end = cumulative_trapezoid(power3end_filtered, frequency9, initial=0)
total_power3_end = area_freq3_end[-1]
median_freq3_end = frequency9[np.where(area_freq3_end >= total_power3_end / 2)[0][0]]

# Plot mit 3 Spalten und 1 Zeile
fig, axes = plt.subplots(nrows=1, ncols=3, figsize=(18, 6))

# Burst 1
axes[0].plot(frequency, powerstart_filtered, label="Burst 1 - Start", color='r')
axes[0].plot(frequency2, powermid_filtered, label="Burst 1 - Mitte", color='g')
axes[0].plot(frequency3, powerend_filtered, label="Burst 1 - Ende", color='b')
axes[0].axvline(median_freq, color='r', linestyle='--')
axes[0].axvline(median_freq_mid, color='g', linestyle='--')
axes[0].axvline(median_freq_end, color='b', linestyle='--')
axes[0].set_title("Burst 1")
axes[0].set_xlabel("Frequenz / Hz")
axes[0].set_ylabel("Leistung / a.u.")
axes[0].legend()
axes[0].grid()

# Burst 2
axes[1].plot(frequency4, power2start_filtered, label="Burst 2 - Start", color='r')
axes[1].plot(frequency5, power2mid_filtered, label="Burst 2 - Mitte", color='g')
axes[1].plot(frequency6, power2end_filtered, label="Burst 2 - Ende", color='b')
axes[1].axvline(median_freq2_start, color='r', linestyle='--')
axes[1].axvline(median_freq2_mid, color='g', linestyle='--')
axes[1].axvline(median_freq2_end, color='b', linestyle='--')
axes[1].set_title("Burst 2")
axes[1].set_xlabel("Frequenz / Hz")
axes[1].legend()
axes[1].grid()

# Burst 3
axes[2].plot(frequency7, power3start_filtered, label="Burst 3 - Start", color='r')
axes[2].plot(frequency8, power3mid_filtered, label="Burst 3 - Mitte", color='g')
axes[2].plot(frequency9, power3end_filtered, label="Burst 3 - Ende", color='b')
axes[2].axvline(median_freq3_start, color='r', linestyle='--')
axes[2].axvline(median_freq3_mid, color='g', linestyle='--')
axes[2].axvline(median_freq3_end, color='b', linestyle='--')
axes[2].set_title("Burst 3")
axes[2].set_xlabel("Frequenz / Hz")
axes[2].legend()
axes[2].grid()

# Layout anpassen
fig.tight_layout()
plt.show()

# Burst 1 - Mitte: Darstellung des rohen Leistungsspektrums, gefilterten Leistungsspektrums und der durchschnittlichen Frequenz
plt.figure(figsize=(12, 6))
plt.plot(frequency2, power_middle, label="Rohes Leistungsspektrum", color='blue')
plt.plot(frequency2, powermid_filtered, linestyle='--', label="Gefiltertes Leistungsspektrum", color='red')

# Durchschnittliche Frequenz berechnen
average_frequency = np.average(frequency2, weights=powermid_filtered)
plt.axvline(average_frequency, color='green', linestyle='-.', label=f"Durchschnittliche Frequenz: {average_frequency:.2f} Hz")

# Plot-Details
#plt.title("Burst 1 - Mitte: Leistungsspektrum roh + gefiltert und Durchschnittliche Frequenz")
plt.xlabel("Frequenz / Hz")
plt.ylabel("Leistung / a.u.")
plt.legend()
plt.grid()
plt.savefig("Plot-Experiment2-Relative-Muskelaktivierung.svg", format="svg")
plt.show()

# Normalisierte relative Zeitpunkte für die Darstellung
time_points_pct = [0.1, 0.5, 0.9]  # Anfang, Mitte, Ende (in Prozent)

# Medianfrequenzen der drei Bursts
median_frequencies = [
    [median_freq, median_freq_mid, median_freq_end],       # Burst 1
    [median_freq2_start, median_freq2_mid, median_freq2_end],  # Burst 2
    [median_freq3_start, median_freq3_mid, median_freq3_end]   # Burst 3
]

# Farben und Marker für die drei Bursts
colors = ['red', 'green', 'blue']
markers = ['o', 's', '^']

# Plot erstellen
plt.figure(figsize=(10, 6))
for i in range(3):  # Für jeden Burst
    plt.plot(
        time_points_pct, 
        median_frequencies[i], 
        label=f'Versuch {i+1}', 
        color=colors[i], 
        marker=markers[i], 
        linestyle='-'
    )

# Achsentitel und Legende
plt.xlabel("Zeitpunkt der Messung / %")
plt.ylabel("Median-Frequenz / Hz")
#plt.title("Change in Median Frequency Over Time for Fatigue Test")
plt.legend()
plt.grid()
plt.savefig("Plot-Experiment2-Median-Frequenz.svg", format="svg")
plt.show()
