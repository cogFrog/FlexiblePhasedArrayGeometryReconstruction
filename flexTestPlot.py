import numpy as np
import rangeFinder as rf
import matplotlib.pyplot as plt

csv = rf.RangeFinderCSV(10e9, 100e6, 101)

l = 45e-3

# calibrate at 100 mm or 0.1 m
csv.find_range(True, l, 'results\\flexResults\\flat.csv', l)

order = ['40concave', '30concave', '20concave', '10concave', 'flat', '10convex', '20convex', '30convex', '40convex']

curvature = np.array([*range(-40,41,10)])
estimated_dist_phase = []
estimated_dist_fsk = []
estimated_dist_total = []

for curv in order:
    estimated_dist_phase.append(csv.find_range(False, 0, f'results\\flexResults\\{curv}_s14.csv', l)[1] * 1000)
    estimated_dist_fsk.append(csv.find_range(False, 0, f'results\\flexResults\\{curv}_s14.csv', l)[0] * 1000)
    estimated_dist_total.append(csv.find_range(False, 0, f'results\\flexResults\\{curv}_s14.csv', l)[2] * 1000)

estimated_dist_phase = np.array(estimated_dist_phase)
estimated_dist_fsk = np.array(estimated_dist_fsk)
estimated_dist_total = np.array(estimated_dist_total)

theta = np.deg2rad(abs(curvature))
r = l / abs(theta)
d = 2*r*np.sin(theta/2)
d[4] = 45e-3
print(d)

plt.figure(1)
plt.plot(curvature, estimated_dist_phase)
plt.plot(curvature, d*1000)
plt.xlabel('Curvature (deg)')
plt.ylabel('Estimated Curvature - Phase (mm)')

plt.figure(2)
plt.plot(curvature, estimated_dist_fsk)
plt.plot(curvature, d*1000)
plt.xlabel('Curvature (deg)')
plt.ylabel('Estimated Curvature - FSK (mm)')

plt.figure(3)
plt.plot(curvature, estimated_dist_total)
plt.plot(curvature, d*1000)
plt.xlabel('Curvature (deg)')
plt.ylabel('Estimated Curvature - Total (mm)')

plt.show()
