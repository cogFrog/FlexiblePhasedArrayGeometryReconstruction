import numpy as np
import rangeFinder as rf
import matplotlib.pyplot as plt

base_bw = 100e6
base_points = 101

fractional_bws = [1, 0.5, 0.24, 0.1]

for frac_bw in fractional_bws:
    bw = base_bw*frac_bw
    points = int((base_points - 1)*frac_bw)

    csv = rf.RangeFinderCSV(10e9, bw, points)

    # calibrate at 100 mm or 0.1 m
    csv.find_range(True, 0.1, f'results\\distanceResults\\dist_100mm.csv', 1e9)

    actual_dist = np.array([*range(10, 301, 5)])
    estimated_dist_fsk = []

    for dist in range(10, 301, 5):
        estimated_dist_fsk.append(csv.find_range(False, 0, f'results\\distanceResults\\dist_{dist}mm.csv',1e9)[0] * 1000)
    estimated_dist_fsk = np.array(estimated_dist_fsk)

    error_dist_fsk = estimated_dist_fsk - actual_dist
    print(estimated_dist_fsk)

    plt.plot(actual_dist, error_dist_fsk, label=f'bw={bw / 1e6} MHz')

plt.axhline(y=15, color="black", linestyle="--")
plt.axhline(y=-15, color="black", linestyle="--")
plt.xlabel('Actual Distance (mm)')
plt.ylabel('Distance Estimation Error (mm)')
plt.legend()
plt.show()
