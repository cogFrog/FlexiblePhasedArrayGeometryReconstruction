import rangeFinder as rf

vna = rf.VNAReader(10.05e9, 100e6, 201, 0, 'USB0::0x0957::0x0118::US49010233::0::INSTR')

for d in range(2,20):
    input(f'Set antenna spacing distance to {d} cm \nPress enter when done')
    vna.save_sample(f'dist_{d}0mm.csv', 16)