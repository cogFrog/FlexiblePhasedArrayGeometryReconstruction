import rangeFinder as rf
import numpy as np

vna = rf.VNAReader(2.505e9, 30e6, 201, 0, 'USB0::0x0957::0x0118::US49010233::INSTR')
# vna = rf.VNAReader(2.498e9, 30e6, 201, 0, 'USB0::0x0957::0x0118::US49010233::0::INSTR')

#for d in range(2,20):
#    input(f'Set antenna spacing distance to {d} cm \nPress enter when done')
#    vna.save_sample(f'dist_{d}0mm.csv', 16)

d = input(f'Set antenna spacing \nProvide distance in cm: ')
done = False

while not done:
    sample = vna.get_sample()
    print(f'angle: {np.max(sample) - np.min(sample)}')

    accept = input(f'y to record good data, n to discard, r to repeat: ')
    if accept == 'y':
        vna.save_sample(f'dist_{d}0mm.csv', 16)
        done = True
    elif accept == 'n':
        done = True
    elif accept == 'r':
        print("trying again")
    else:
        print("incorrect input, try again")

vna.save_sample(f'dist_{d}0mm.csv', 16)