import numpy as np
import rangeFinder as rf
import matplotlib.pyplot as plt

csv = rf.RangeFinderCSV(10e9, 100e6, 101)

# calibrate at 100 mm or 0.1 m
csv.find_range(True, 45e-3, 'results\\flexResults\\flat_s14.csv')

order = ['40concave', '30concave', '20concave', '10concave', 'flat', '10convex', '20convex', '30convex', '40convex']

curvature = np.array([*range(-40,41,10)])
estimated_dist = []

for curv in order:
    estimated_dist.append(csv.find_range(False, 0, f'results\\flexResults\\{curv}_s14.csv')[2]*1000)
estimated_dist = np.array(estimated_dist)

plt.figure(1)
plt.plot(curvature, estimated_dist)
plt.xlabel('Actual Distance (mm)')
plt.ylabel('Distance Estimation Error (mm)')

plt.show()
