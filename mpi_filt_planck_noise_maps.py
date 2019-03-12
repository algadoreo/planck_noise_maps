import numpy as np
import spider_analysis as sa
import sys
from mpi4py import MPI


# MPI stuff
comm = MPI.COMM_WORLD
rank = comm.Get_rank()      # process number
size = comm.Get_size()      # total number of processes


if len(sys.argv) != 4:
    print('\nUsage: python mpi_filt_planck_noise_maps.py <fpu_no> <planck_subset> <map_no>\n')
    exit(1)

try:
    fpu = np.int8(sys.argv[1])
except:
    print('\nUsage: python mpi_filt_planck_noise_maps.py <fpu_no> <planck_subset> <map_no>\n')
    exit(1)
else:
    if fpu < 1 or fpu > 6:
        print('\nFPU number must be between 1 and 6\n')
        exit(1)


freq = '100' if (fpu % 2 == 0) else '143'
psubset = sys.argv[2]
run = np.int8(sys.argv[3])

beam = 'beam20'
cal = 'cal_fwhm_29'
net = 'net18'

beam_field = 'X{}_'.format(fpu) + beam.upper()


# Define output
ROOT_DIR = '/scratch/r/rbond/jleung/output/planck_noise_maps/'
OUTPUT_DIR = ROOT_DIR + 'filt_X{}_{}_noise_sim_{:04d}'.format(fpu, psubset, run)

U = sa.Unifile(verbose='info')
P = U.new_product(OUTPUT_DIR, unifile_version=5, ruleset_version=3, creator='jsyl', encoding=None)
siefrag = P.get_fragment('format.sie', encoding='sie')
event = 'all'


# Set up input map
SOURCE_MAP = ROOT_DIR + '{}_{}/planck_hfi_{}_noise_sim_{:04d}.fits'.format(freq, psubset, freq, run)
if rank == 0:
    print('Reading map from\n' + SOURCE_MAP)

S = sa.UnifileSim(default_latest=True, cal=cal, net=net, add_from_map=True)
S.init_source(source_map=SOURCE_MAP, beam_product=beam, beam_field=beam_field, units='K')

sopts = S.event_partition(prefix='hwp_step', event=event)
slices = S.event_partition(prefix='hwp_step', return_slices=True, event=event)

good_channels_list = S.good_channels(fpu)

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
    tod_noise = np.zeros(S.get_sync_count(event=event), dtype='float32')
    for sopt, sli in zip(sopts, slices):
        tod_noise[sli] = S.get_mce_data(channel, product=None, **sopt)

    data = np.zeros(S.get_sync_count(event=event), dtype='float32')
    flags = np.ones(S.get_sync_count(event=event), dtype='uint8')

    for sopt, sli in zip(sopts, slices):
        noise_filt, noise_flag = S.get_filtered_tod(channels=channel, product='dcclean08',
                                        return_flag=True, filter_turnarounds=True, tod=np.atleast_2d(tod_noise[sli]),
                                        flag=None, extra_flag_product=True, extra_flag_mask=0x1FFF,
                                        filter_num_scans=1, filter_dipole=False, scan_cut_adu=5, scan_cut_net=1.5,
                                        scan_cut_min_adu=0.8, az_filter=True, az_product='point_default',
                                        gain_product=True, min_unflagged=0.1, poly_product=True, 
                                        poly_rms_tag='resid05', filter_chunks=False,
                                        chunk_rms_product=None, chunk_rms_tag=None, svd_threshold=-1,
                                        svd_num_modes=-1, svd_product=None, rwn_product='rwn01',
                                        max_chunk_flag_frac=0.5, fourier_filter=None, psd_filter=None, 
                                        fill_nan=True, chunk_cut_net=1.5, cache_poly_coeffs=False,
                                        cache_poly_covmat=False, apply_poly_filter=True, poly_cond_thresh=1.e6,
                                        step_flag_product=None, subtract_yssn=False, filter_yssn=False,
                                        yssn_product=None, yssn_num_modes=1, poly_weight=False,
                                        stepstitch_product='stepstitch07', subtract_dipole=False,
                                        force_scan_flag=False, data_split_flag=None, data_split_pick=None,
                                        **sopt)
        data[sli] = noise_filt
        flags[sli] = noise_flag

    P.add_raw_field(channel, dtype='float32', isupper=True, spf=20)
    P.putdata(channel, data, dtype='float32', create=False, isupper=True)
    
    P.add_raw_field(channel+'_FLAG', fragment=siefrag, dtype='uint8', isupper=True, spf=20)
    P.putdata(channel+'_FLAG', flags, dtype='uint8', create=False, isupper=True)
