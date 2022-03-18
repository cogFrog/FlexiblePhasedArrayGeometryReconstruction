import pyvisa
import time
import numpy as np
import scipy.constants
from scipy.ndimage.interpolation import shift
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

        # setup vna connection
        self.rm = pyvisa.ResourceManager()
        self.vna = self.rm.open_resource('USB0::0x0957::0x0118::US49010233::INSTR')
        self.vna.read_termination = '\n'
        self.vna.write_termination = '\n'

        # reset display, start measurement (select S21 for given f_c and BW)
        self.vna.write("SYSTem:FPReset")
        self.vna.write("DISPlay:WINDow1:STATE ON")
        self.vna.write("CALCulate:PARameter:DEFine 'meas',S21")
        self.vna.write("DISPlay:WINDow1:TRACe1:FEED 'meas'")
        self.vna.write(f"SENSe:FREQuency:CENTer {f_c} Hz")
        self.vna.write(f"SENSe:FREQuency:SPAN {BW} Hz")
        self.vna.write(f"SENSe1:SWEep:POINts {points}")
        self.vna.write(f"SOURce:POWer:LEVel:IMMediate:AMPLitude {power}")

        # Allow user to block program until VNA is calibrated
        input("Calibrate VNA now or select saved calibration \nPress enter when done")

        # Finalize VNA capture parameters
        self.vna.write("CALCulate:PARameter:MODify S21")
        self.vna.write("CALCulate:FORMat PHASe")
        self.vna.write(f"SENSe1:SWEep:POINts {points}")
        self.vna.write("SENSe1:AVERage:COUNt 16")
        self.vna.write("SENSe1:AVERage:CLEar")
        self.vna.write("SENSe1:AVERage:MODE SWEep")
        self.vna.write("SENSe1:AVERage:STATe 1")

        # short delay to allow values to settle
        time.sleep(0.5)

    def getSample(self):
        self.vna.write("CALCulate1:PARameter:SELect 'meas'")
        self.vna.write("FORMat:DATA REAL,64")
        return np.array(self.vna.query_binary_values("CALCulate1:DATA? FDATA", datatype='d', is_big_endian=True))

    def findRange(self, calMode, initialDistance):
        # get sample of S21 phase across BW, unwrap value
        y = self.getSample()
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
            R_diff = min(R_diff, 0.18)

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
f_c = 2.5e9            # center freq (Hz)
BW = 50e6              # sample bandwidth (Hz)

c = scipy.constants.c   # speed of light (m/s)
wl_c = c/f_c

rf = RangeFinder(f_c, BW, 111, 0)

# On first pass, allow user to calibrate given known distance
initialRange = float(input("Input current distance in m: "))
#time.sleep(5)
rf.findRange(True, initialRange)

y = []

for i in range(1, 8):
    input(f"Press enter when ready to measure with {i} cm seperation")
    newData = rf.findRange(False, 0)
    y.append(newData)
    print(f"dist: {100*newData[2]}")

with open('distancePlot.txt', 'wb') as fh:
   pickle.dump(y, fh)