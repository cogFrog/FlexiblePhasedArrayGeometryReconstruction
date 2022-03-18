import csv
import numpy as np
import scipy.constants
import pickle

class RangeFinder:
    # RangeFinder is responsible for reading VNA data in and determining the distance between P1 and P2
    # f_c: center frequency in Hz
    # BW: bandwidth in Hz
    # points: number of sample points
    # power in dBm
    def __init__(self, f_c, BW, points, power):
        self.center = int((points - 1) / 2)

        self.y = np.zeros(points)
        self.x = np.linspace(f_c - BW/2, f_c + BW/2, num=points)

        self.distanceCorrectionDiff = 0
        self.distanceCorrectionPhase = 0

    def getSample(self, dist):
        with open(f'Distances/ANGLE_{dist}cm_REAL.csv') as csvFile:
            dat = csv.reader(csvFile, delimiter=',')
            ans = []
            for row in dat:
                try:
                    ans.append(float(row[1]))
                except ValueError:
                    print("")
        return np.array(ans)

    def findRange(self, calMode, initialDistance, dist):
        # get sample of S21 phase across BW, unwrap value
        y = self.getSample(dist)
        y_unwrapped = np.unwrap(y, period=360)
        y_unwrapped += y[self.center] - y_unwrapped[self.center]

        # create best curve for y
        # a, b = np.polyfit(self.x, y, 1)
        # y_fitted = a * self.x + b

        # find range information using FSK radar approach
        phaseDiff = y_unwrapped[0] - y_unwrapped[-1]
        if calMode:
            R_diff = initialDistance
            self.distanceCorrectionDiff = ((phaseDiff * c) / (360 * BW)) - initialDistance
        else:
            R_diff = ((phaseDiff * c) / (360 * BW)) - self.distanceCorrectionDiff
            R_diff = max(R_diff, 0)

        # find phase range (distance from nearest wavelength multiple)
        # TODO: properly wrap found values
        phase_c = y_unwrapped[self.center]  # get middle sample
        if calMode:
            R_phase = initialDistance - round(initialDistance / wl_c) * wl_c
            self.distanceCorrectionPhase = (-(wl_c * phase_c) / 360) - R_phase
        else:
            R_phase = (-(wl_c * phase_c) / 360) - self.distanceCorrectionPhase
            R_phase = (R_phase + (wl_c/2)) % (wl_c) - (wl_c/2) # wrap from (-wl_c/2, wl_c/2)

        # find range by combining center phase and R_diff
        n = max((R_diff - R_phase) / wl_c, 0)  # force n to bottom out at 0 cm
        R_tot = R_phase + round(n) * wl_c

        return [R_diff, R_phase, R_tot, n, phaseDiff, phase_c]

# Start of actual commands. See Keysight command expert for documentation
f_c = 2.498e9            # center freq (Hz)
BW = 30e6              # sample bandwidth (Hz)

c = scipy.constants.c   # speed of light (m/s)
wl_c = c/f_c

rf = RangeFinder(f_c, BW, 111, 0)

# On first pass, allow user to calibrate given known distance
#time.sleep(5)
rf.findRange(True, 0.1, 10)

y = []

for i in range(1, 21):
    newData = rf.findRange(False, 0, i)
    y.append(newData)
    print(f"dist: {newData[2]}")

with open('distancePlotSim.txt', 'wb') as fh:
   pickle.dump(y, fh)