import numpy as np
import rangeFinder as rf
import matplotlib.pyplot as plt

csv = rf.RangeFinderCSV(10e9, 100e6, 101, True)
# csv = rf.RangeFinderCSV(2.498e9, 30e6, 201, True)

# calibrate at 100 mm or 0.1 m
folder_path = 'results/flexResults3/'
csv.find_range(True, 0.045, f'{folder_path}flat.csv', 1e9)

paths = ['40concave', '30concave', '20concave', '10concave', 'flat', '10convex', '20convex', '30convex', '40convex']
curvatures = [40, 30, 20, 10, 0, -10, -20, -30, -40]
actual_dist = [44.09, 44.49, 44.77, 44.94, 45, 44.94, 44.77, 44.49, 44.09]
estimated_dist = []

for i in range(len(paths)):
    estimated_dist.append(csv.find_range(False, 0, f'{folder_path}{paths[i]}.csv', 1e9)[2]*1000)
estimated_dist = np.array(estimated_dist)

error_dist = (estimated_dist - actual_dist)/15

plt.figure(1)
plt.plot(curvatures, estimated_dist, label='Measured Distance')
plt.plot(curvatures, actual_dist, label='Actual Distance')

plt.xlabel('Angle of Curvature (°, + is concave)')
plt.ylabel('Distance (mm)')
plt.title('1x4 Flexible Array Test: Measured 2')
plt.legend()
plt.grid(True)

#plt.figure(2)
#plt.plot(curvatures, error_dist)
#plt.xlabel('Actual Distance (mm)')
#plt.ylabel('measurement error')
#plt.grid(True)

plt.show()