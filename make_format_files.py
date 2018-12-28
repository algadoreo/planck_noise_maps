import numpy as np
import spider_analysis as sa
import sys


if len(sys.argv) != 4:
    print('\nUsage: python bespoke_map.py <fpu_no> <planck_subset> <map_no>\n')
    exit(1)

try:
    fpu = np.int8(sys.argv[1])
except:
    print('\nUsage: python bespoke_map.py <fpu_no> <planck_subset> <map_no>\n')
    exit(1)
else:
    if fpu < 1 or fpu > 6:
        print('\nFPU number must be between 1 and 6\n')
        exit(1)


freq = '100' if (fpu % 2 == 0) else '143'
psubset = sys.argv[2]
run = np.int8(sys.argv[3])


# Define output
ROOT_DIR = '/scratch/r/rbond/jleung/output/planck_noise_maps/'
OUTPUT_DIR = ROOT_DIR + 'filt_X{}_{}_noise_sim_{:04d}'.format(fpu, psubset, run)

U = sa.Unifile(verbose='info')
P = U.new_product(OUTPUT_DIR, unifile_version=5, ruleset_version=3, creator='jsyl', encoding=None)
siefrag = P.get_fragment('format.sie', encoding='sie')

good_channels_list = P.good_channels(fpu)

for channel in good_channels_list:
    P.add_raw_field(channel, dtype='float32', isupper=True, spf=20, overwrite=False)
    P.add_raw_field(channel+'_FLAG', fragment=siefrag, dtype='uint8', isupper=True, spf=20, overwrite=False)
