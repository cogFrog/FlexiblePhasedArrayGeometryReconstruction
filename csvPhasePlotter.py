import csv
import numpy as np
import matplotlib.pyplot as plt

path = "results\\distanceResultsMeas4\\dist_50mm.csv"
with open(path) as csvFile:
    file = csv.reader(csvFile, delimiter=',')
    data = []
    next(file, None)  # skip header
    for row in file:
        try:
            data.append(float(row[1]))
        except ValueError:
            print(f"Error: could not read line:")

phase = np.array(data)
phase_unwrapped = np.unwrap(phase, period=360)
phase_diff = phase_unwrapped[0] - phase_unwrapped[-1]
print(phase_diff)

freq = np.linspace(10, 10.1, num=201)

plt.plot(freq, phase_unwrapped)
plt.xlabel('Actual Distance (mm)')
plt.ylabel('Estimated Distance (mm)')
plt.title('Estimated vs Actual Antenna Spacing')
plt.grid(True)

plt.show()