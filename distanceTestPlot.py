import numpy as np
import rangeFinder as rf
import matplotlib.pyplot as plt

csv = rf.RangeFinderCSV(10e9, 100e6, 101)

# calibrate at 100 mm or 0.1 m
csv.find_range(True, 0.1, f'results\\distanceResults\\dist_100mm.csv', 1e9)

actual_dist = np.array([*range(10, 201, 1)])
estimated_dist = []
estimated_dist_fsk = []

for dist in range(10, 201, 1):
    estimated_dist.append(csv.find_range(False, 0, f'results\\distanceResults\\dist_{dist}mm.csv', 1e9)[2]*1000)
    estimated_dist_fsk.append(csv.find_range(False, 0, f'results\\distanceResults\\dist_{dist}mm.csv', 1e9)[0] * 1000)
estimated_dist = np.array(estimated_dist)
estimated_dist_fsk = np.array(estimated_dist_fsk)

error_dist = estimated_dist - actual_dist
error_dist_fsk = estimated_dist_fsk - actual_dist

print(estimated_dist)

plt.figure(1)
plt.plot(actual_dist, estimated_dist)
plt.xlabel('Actual Distance (mm)')
plt.ylabel('Estimated Distance (mm)')
plt.grid(True)

plt.figure(2)
plt.plot(actual_dist, error_dist)
plt.xlabel('Actual Distance (mm)')
plt.ylabel('Distance Estimation Error (mm)')
plt.grid(True)

plt.figure(3)
plt.plot(actual_dist, error_dist_fsk)
plt.axhline(y=15, color="black", linestyle="--")
plt.axhline(y=-15, color="black", linestyle="--")
plt.xlabel('Actual Distance (mm)')
plt.ylabel('Distance Estimation Error (mm)')
plt.grid(True)

plt.show()