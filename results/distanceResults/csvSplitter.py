import csv
import numpy as np

# For a parametric sweep in HFSS, a single CSV is made for all antenna distances. This splits it into a CSV for each
# distance, allowing for RangeFinderCSV to parse them one at a time.

freq = {}
phase = {}

with open('distE_s12.csv') as csvFile:
    file = csv.reader(csvFile, delimiter=',')
    next(file, None)  # skip header
    for row in file:
        try:
            if row[0] in freq:
                freq[row[0]].append(float(row[1]))
                phase[row[0]].append(float(row[2]))
            else:
                freq[row[0]] = [float(row[1])]
                phase[row[0]] = [float(row[2])]
        except ValueError:
            print("")

distances = freq.keys()
for d in distances:
    f = np.array(freq[d])
    p = np.array(phase[d])

    data = np.concatenate(([f], [p]), axis=0).T
    with open(f'dist_{d}mm.csv', 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['Frequency (GHz)', 'Phase (deg)'])
        csvwriter.writerows(data)
