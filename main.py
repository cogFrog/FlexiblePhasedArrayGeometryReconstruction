import rangeFinder as rf

# Just some tests, probably not going as far as making unit tests for this project
csv = rf.RangeFinderCSV(10e9, 50e6, 101)
print(csv.find_range(False, 0, 'HFSSdat.csv'))

vna = rf.VNAReader(10.05e9, 50e6, 201, 0, 'USB0::0x0957::0x0118::US49010233::0::INSTR')
print(vna.get_sample())

vna.save_sample('pain.csv')

csv2 = rf.RangeFinderCSV(10e9, 50e6, 201)
print(csv2.find_range(False, 0, 'pain.csv'))

vna2 = rf.RangeFinderVNA(10.05e9, 50e6, 201, 0, 'USB0::0x0957::0x0118::US49010233::0::INSTR')
print(vna2.get_sample(''))