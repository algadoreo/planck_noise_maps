import numpy as np
import spider_analysis.map as sam
import sys, os, shutil
import glob


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

# Define input and output
ROOT_DIR = "/scratch/r/rbond/jleung/output/planck_noise_maps/filtered_maps/"

product_tag = "filt_X{}_{}_noise_sim_{:04d}".format(fpu, psubset, run)

SOURCE_DIR = os.path.join(ROOT_DIR, product_tag+"_interleaved_mpi")
OUTPUT_DIR = os.path.join(ROOT_DIR, product_tag+"_interleaved")
if not os.path.exists(SOURCE_DIR):
    print("Nothing to coadd; source directory does not exist:")
    print(SOURCE_DIR)
    exit(1)
if len(os.listdir(SOURCE_DIR)) != 2240:
    print("Source directory incomplete:")
    print(SOURCE_DIR)
    print("\nCoadding aborted\n")
    exit(1)
try:
    os.mkdir(OUTPUT_DIR)
except:
    pass


### Main body
print("\nCoadding intermediary maps made by each MPI process\n")
for chunk in range(14):
    print("Now starting FPU {} chunk {:02d}".format(fpu, chunk))
    channel_maps_list = glob.glob(os.path.join(SOURCE_DIR, "vec_"+product_tag+"_chunk{:02d}".format(chunk)+"_*.fits"))
    print("{} maps to coadd".format(len(channel_maps_list)))

    M = sam.unimap_coadd(files=channel_maps_list, mpi=True, tag=product_tag+"_chunk{:02d}".format(chunk), output=OUTPUT_DIR)

# Remove the intermediary maps created by MPI
if os.path.exists(SOURCE_DIR):
    print("\nRemoving intermediary maps made by each MPI process...\n")
    shutil.rmtree(SOURCE_DIR)
    print("Finished!\n")
