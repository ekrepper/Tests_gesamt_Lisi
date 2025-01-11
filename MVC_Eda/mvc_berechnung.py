import matplotlib.pyplot as plt
import numpy as np
import scipy.signal as sc
from scipy.integrate import cumulative_trapezoid
import Lab3Functions as lf3
import os

#Importieren der Daten
mvc = lf3.import_data('\t')

#Umrechnen der Zeit in Sekunden (Abtastrate 1000Hz)
mvc['t'] = mvc['t']/1000

print(mvc)

#Offset im emg Datensatz entfernen --> NOCH DYNAMISCH MACHEN; NICHT HARD GECODET
mvc_offsetclean = mvc['emg'] - np.mean(mvc['emg'])


#Butterworth Filter (20 Hz bis 450 Hz) anwenden
b, a = sc.butter(4, [20/500, 450/500], btype='bandpass')
mvc_emg_filtered = sc.filtfilt(b, a, mvc_offsetclean)


#Gleichrichten der Daten
mvc_rectified = np.abs(mvc_emg_filtered)


#Einhüllende Bilden: Tiefpass Grenfrequenz 3 Hz 
b, a = sc.butter(4, 3/500, btype='lowpass')
mvc_envelope = sc.filtfilt(b, a, mvc_rectified)



# Pfade für die .npy-Dateien
files = {
    "mvc_s": "mvc_s.npy",
    "mvc_e": "mvc_e.npy"
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
    else:
        # Dateien existieren nicht, get_bursts aufrufen
        print("Berechne Burst-Daten interaktiv...")
        mvc_s, mvc_e = lf3.get_bursts(
            mvc_emg_filtered
        )

        # Ergebnisse speichern
        np.save(files["mvc_s"], mvc_s)
        np.save(files["mvc_e"], mvc_e)
        print("Burst-Daten wurden gespeichert.")

    return mvc_s, mvc_e

# Aufruf der Funktion
mvc_s, mvc_e = load_or_compute_bursts()


mvc_eda = np.mean(np.mean(mvc_envelope[mvc_s[0]:mvc_e[0]]) + np.mean(mvc_envelope[mvc_s[1]:mvc_e[1]]) + np.mean(mvc_envelope[mvc_s[2]:mvc_e[2]]))
print('MVC Eda', mvc_eda)

#hier nur "mvc_greta = " / mvc_eda =" als Variablennamen nehmen und print('MVC Elisabeth',mvc_elisabeth) hier ändern, alle anderen variablen können gleich bleiben