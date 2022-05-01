import numpy as np
import rangeFinder as rf
import matplotlib.pyplot as plt

csv = rf.RangeFinderCSV(10.05e9, 100e6, 201, True)
# csv = rf.RangeFinderCSV(2.498e9, 30e6, 201, True)

# calibrate at 100 mm or 0.1 m
folder_path = 'results/flexResults2/'
csv.find_range(True, 0.10, f'{folder_path}dist_100mm.csv', 1e9)

actual_dist = np.array([*range(20, 191, 10)])
estimated_dist = []
estimated_dist_fsk = []
phase_diff = []

for dist in actual_dist:
    estimated_dist.append(csv.find_range(False, 0, f'{folder_path}dist_{dist}mm.csv', 1e9)[2]*1000)
    estimated_dist_fsk.append(csv.find_range(False, 0, f'{folder_path}dist_{dist}mm.csv', 1e9)[0] * 1000)
    phase_diff.append(csv.find_range(False, 0, f'{folder_path}dist_{dist}mm.csv', 1e9)[3] * 1000)
estimated_dist = np.array(estimated_dist)
estimated_dist_fsk = np.array(estimated_dist_fsk)

error_dist = estimated_dist - actual_dist
error_dist_fsk = estimated_dist_fsk - actual_dist

plt.figure(1)
plt.plot(actual_dist, estimated_dist)
plt.xlabel('Actual Distance (mm)')
plt.ylabel('Estimated Distance (mm)')
plt.title('Estimated vs Actual Antenna Spacing')
plt.grid(True)

plt.figure(2)
plt.plot(actual_dist, estimated_dist_fsk)
plt.xlabel('Actual Distance (mm)')
plt.ylabel('phase diff')
plt.grid(True)

plt.figure(3)
plt.plot(actual_dist, error_dist_fsk)
plt.axhline(y=15, color="black", linestyle="--")
plt.axhline(y=-15, color="black", linestyle="--")
plt.xlabel('Actual Distance (mm)')
plt.ylabel('Distance Estimation Error (mm)')
plt.title('Error in FSK Measurement')
plt.legend()
plt.grid(True)

plt.show()