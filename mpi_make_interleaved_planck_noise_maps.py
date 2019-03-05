import numpy as np
import spider_analysis as sa
import sys, os
from mpi4py import MPI


# MPI stuff
comm = MPI.COMM_WORLD
rank = comm.Get_rank()      # process number
size = comm.Get_size()      # total number of processes


if len(sys.argv) != 5:
    print('\nUsage: python mpi_make_interleaved_planck_noise_maps.py <fpu_no> <planck_subset> <map_no> <chunk_no>\n')
    exit(1)

try:
    fpu = np.int8(sys.argv[1])
except:
    print('\nUsage: python mpi_make_interleaved_planck_noise_maps.py <fpu_no> <planck_subset> <map_no> <chunk_no>\n')
    exit(1)
else:
    if fpu < 1 or fpu > 6:
        print('\nFPU number must be between 1 and 6\n')
        exit(1)


freq = '100' if (fpu % 2 == 0) else '143'
psubset = sys.argv[2]
run = np.int8(sys.argv[3])
chunk = np.int8(sys.argv[4])

# Define input and output
ROOT_DIR = '/scratch/r/rbond/jleung/output/planck_noise_maps/'
SOURCE_DIR = os.path.join(ROOT_DIR, 'filtered_maps/')

product_tag = 'filt_X{}_{}_noise_sim_{:04d}'.format(fpu, psubset, run)
product = os.path.join(ROOT_DIR, product_tag)
tod_suffix = '_' + product_tag.upper()

OUTPUT_DIR = os.path.join(SOURCE_DIR, product_tag+'_interleaved_mpi')
try:
    os.mkdir(OUTPUT_DIR)
except:
    pass


### Main body
M = sa.UnifileMap(default_latest=True, cal='cal', net='net')

sample_opts_list = M.hwp_partition(event='full_flight', chunk_event_file="events_time_chunk_3min", chunk_set=(chunk, -1, 14))

good_channels_list = M.good_channels(fpu=fpu)

vec, proj = M.init_dest(nside=512, pol=True, reset=True)

# Use MPI to divide the job into segments
seg_len = int(len(good_channels_list)/size)
seg_mod = len(good_channels_list) % size
if rank < seg_mod:
    seg_len = seg_len + 1
    seg_start = seg_len * rank
    seg_stop = seg_len * (rank + 1)
else:
    seg_start = seg_len * rank + seg_mod
    seg_stop = seg_len * (rank + 1) + seg_mod

channels_list_segment = good_channels_list[seg_start:seg_stop]

for channel in channels_list_segment:
    
    for sample_opts in sample_opts_list:
        sopt = M.extract_sample_opts(sample_opts)

        tod = M.getdata(product=product, isupper=True, field=channel.upper()+tod_suffix, **sopt)
        flag = M.getdata(product=product, isupper=True, field=channel.upper()+'_FLAG'+tod_suffix, **sopt)

        vec, proj = M.from_tod(channel, tod=tod, flag=flag,
                extra_flag_product=False,
                filter_turnarounds=False, filter_dipole=False, 
                scan_cut_adu=None, scan_cut_net=None,
                gain_product=True, poly_product=False,
                max_chunk_flag_frac=0.5, weights_product=False,
                apply_poly_filter=False, **sopt)

bespoke_map = M.solve_map()

map_tag = product_tag + '_chunk{:02d}_{:02d}'.format(chunk, rank)
try:
    M.write_dest(output=OUTPUT_DIR, tag=map_tag)
    M.write_map(bespoke_map, output=OUTPUT_DIR, tag=map_tag)
except:
    print('Rank {} failed'.format(rank))
