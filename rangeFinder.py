import numpy as np
import scipy.constants
from abc import ABC, abstractmethod
import csv
import time
import pyvisa


class RangeFinderBase(ABC):
    # RangeFinderBase is abstract class defining basic range finder behavior, implements algorithm in one place.
    #
    # f_c: center frequency in Hz
    # bw: bandwidth in Hz
    # points: number of sample points used
    def __init__(self, f_c, bw, points):
        self.f_c = f_c
        self.bw = bw
        self.points = points
        self.c = scipy.constants.c
        self.wl_c = self.c / self.f_c

        self.center = int((points - 1) / 2)
        self.phase = np.zeros(points)
        self.freq = np.linspace(f_c - bw / 2, f_c + bw / 2, num=points)

        self.k_fsk = 0
        self.k_phase = 0

    @abstractmethod
    def get_sample(self, path):
        pass

    def find_range(self, cal_mode, init_dist, path, max_output):
        # get sample of S21 phase across BW, unwrap value
        phase = self.get_sample(path)
        phase_unwrapped = np.unwrap(phase, period=360)
        phase_unwrapped += phase[self.center] - phase_unwrapped[self.center]

        # find range information using FSK radar approach
        phase_diff = phase_unwrapped[0] - phase_unwrapped[-1]
        if cal_mode:  # if in calibration mode, use init_dist value to find correction factor k_fsk
            r_fsk = init_dist
            self.k_fsk = ((phase_diff * self.c) / (360 * self.bw)) - init_dist
        else:
            r_fsk = ((phase_diff * self.c) / (360 * self.bw)) - self.k_fsk
            r_fsk = min(max(r_fsk, 0), max_output)

        # find phase range (distance from the nearest wavelength multiple)
        phase_cent = phase_unwrapped[self.center]  # get middle sample
        if cal_mode:  # if in calibration mode, use init_dist value to find correction factor k_phase
            r_phase = init_dist - round(init_dist / self.wl_c) * self.wl_c
            self.k_phase = (-(self.wl_c * phase_cent) / 360) - r_phase
        else:
            r_phase = (-(self.wl_c * phase_cent) / 360) - self.k_phase
            r_phase = (r_phase + (self.wl_c / 2)) % self.wl_c - (self.wl_c / 2)  # wrap from (-wl_c/2, wl_c/2)

        # find range by combining center phase and R_diff
        n = max((r_fsk - r_phase) / self.wl_c, 0)  # approximate range in number of wavelengths
        r_tot = max(r_phase + round(n) * self.wl_c, 0)
        #if (r_tot > max_output):
        #    r_tot = 2 * max_output - r_tot

        return [r_fsk, r_phase, r_tot, n, phase_diff, phase_cent]


class RangeFinderCSV(RangeFinderBase):
    # RangeFinderCSV reads phase data from a csv file for use in distance estimation
    #
    # f_c: center frequency in Hz
    # bw: bandwidth in Hz
    # points: number of sample points
    # file_path: path to csv file "{file_path}_{dist}cm.csv with recorded data
    def __init__(self, f_c, bw, points, average_mode):
        super().__init__(f_c, bw, points)
        self.average_mode = average_mode

    # converts csv files (expected {frequency, phase} for each row) into np array of phases
    def get_sample(self, path):
        if not self.average_mode:
            with open(path) as csvFile:
                file = csv.reader(csvFile, delimiter=',')
                data = []
                next(file, None)  # skip header
                for row in file:
                    try:
                        data.append(float(row[1]))
                    except ValueError:
                        print(f"Error: could not read line")
        else:
            with open(path) as csvFile:
                file = csv.reader(csvFile, delimiter=',')
                data = None
                next(file, None)  # skip header
                for row in file:
                    try:
                        array = np.array(row[1:])
                        array = array.astype(float)
                        if data is None:
                            data = array
                        else:
                            data = np.block([[data], [array]])
                    except ValueError:
                        print(f"Error: could not read line")
        # ave = np.average(array)
        # array = array.astype(float)
        data = np.unwrap(data, period=360, axis=0)
        data = np.average(data, axis=1)
        margin = int((len(data) - self.points) / 2)
        data = data[margin:len(data) - margin]
        return np.array(data)


class RangeFinderVNA(RangeFinderBase):
    # RangeFinderVNA reads phase data directly from VNA for use in distance estimation
    #
    # f_c: center frequency in Hz
    # bw: bandwidth in Hz
    # points: number of sample points
    # power: VNA transmit power in dBm
    # resource: VNA's resource code, use pyvisa.ResourceManager().list_resources() to find connected instruments
    def __init__(self, f_c, bw, points, power, resource):
        super().__init__(f_c, bw, points)
        self.vna_reader = VNAReader(f_c, bw, points, power, resource)

    def get_sample(self, path):
        return self.vna_reader.get_sample()


class VNAReader:
    # RangeFinderVNA reads phase data directly from VNA for use in distance estimation
    #
    # f_c: center frequency in Hz
    # bw: bandwidth in Hz
    # points: number of sample points
    # power: VNA transmit power in dBm
    # resource: VNA's resource code, use pyvisa.ResourceManager().list_resources() to find connected instruments
    def __init__(self, f_c, bw, points, power, resource):
        self.f_c = f_c
        self.bw = bw
        self.points = points

        # setup vna connection
        self.rm = pyvisa.ResourceManager()
        self.vna = self.rm.open_resource(resource)
        self.vna.read_termination = '\n'
        self.vna.write_termination = '\n'

        # reset display, start measurement (select S21 for given f_c and BW)
        self.vna.write("SYSTem:FPReset")
        self.vna.write("DISPlay:WINDow1:STATE ON")
        self.vna.write("CALCulate:PARameter:DEFine 'meas',S21")
        self.vna.write("DISPlay:WINDow1:TRACe1:FEED 'meas'")
        self.vna.write(f"SENSe:FREQuency:CENTer {f_c} Hz")
        self.vna.write(f"SENSe:FREQuency:SPAN {bw} Hz")
        self.vna.write(f"SENSe1:SWEep:POINts {points}")
        self.vna.write(f"SOURce:POWer:LEVel:IMMediate:AMPLitude {power}")

        # Allow user to block program until VNA is calibrated
        input("Calibrate VNA now or select saved calibration \nPress enter when done")

        # Finalize VNA capture parameters
        self.vna.write("CALCulate:PARameter:MODify S21")
        self.vna.write("CALCulate:FORMat PHASe")
        self.vna.write(f"SENSe1:SWEep:POINts {points}")
        self.vna.write("SENSe1:AVERage:COUNt 1")
        self.vna.write("SENSe1:AVERage:CLEar")
        self.vna.write("SENSe1:AVERage:MODE SWEep")
        self.vna.write("SENSe1:AVERage:STATe 1")

        # short delay allows values to settle
        time.sleep(0.5)

    def get_sample(self):
        self.vna.write("CALCulate1:PARameter:SELect 'meas'")
        self.vna.write("FORMat:DATA REAL,64")
        return np.array(self.vna.query_binary_values("CALCulate1:DATA? FDATA", datatype='d', is_big_endian=True))

    # Takes a sample and saves it in a CSV file for future use. Each column follows {frequency, phase} format
    # TODO: test this function in particular for compatibility with RangeFinderCSV's get_sample()
    def save_sample(self, filename, samples):
        phases = np.zeros([self.points,samples])
        data = np.zeros([self.points, samples + 1])
        freqs = np.linspace(self.f_c - self.bw / 2, self.f_c + self.bw / 2, num=self.points) / 1e9

        for sample in range(samples):
            phases[:,sample] =self.get_sample()
            time.sleep(0.1)

        data[:,0] = freqs
        data[:, 1:] = phases

        with open(filename, 'w', newline='') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(['Frequency (GHz)', 'Phase (deg)'])
            csvwriter.writerows(data)
