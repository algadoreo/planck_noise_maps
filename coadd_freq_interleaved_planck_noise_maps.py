import numpy as np
import spider_analysis.map as sam
import sys, os, shutil


if len(sys.argv) != 4:
    print('\nUsage: python bespoke_map.py <frequency> <planck_subset> <map_no>\n')
    exit(1)

try:
    freq = np.uint8(sys.argv[1])
except:
    print('\nUsage: python bespoke_map.py <frequency> <planck_subset> <map_no>\n')
    exit(1)
else:
    if freq != 100 and freq != 143:
        print('\nPlanck frequency must be either 100 or 143\n')
        exit(1)

fpu_list = {143: ['X1', 'X3', 'X5'], 100: ['X2', 'X4', 'X6']}
psubset = sys.argv[2]
run = np.int8(sys.argv[3])

# Define input and output
ROOT_DIR = "/scratch/r/rbond/jleung/output/planck_noise_maps/filtered_maps/"

product_tag_list = ["filt_{}_{}_noise_sim_{:04d}".format(fpu, psubset, run) for fpu in fpu_list[freq]]

SOURCE_DIR_LIST = [os.path.join(ROOT_DIR, product_tag+"_interleaved") for product_tag in product_tag_list]
output_tag = "filt_{}_{}_noise_sim_{:04d}".format(freq, psubset, run)
OUTPUT_DIR = os.path.join(ROOT_DIR, output_tag+"_interleaved")
if not os.path.exists(OUTPUT_DIR):
    os.mkdir(OUTPUT_DIR)

### Main body
print("\nCoadding maps from the {} GHz detectors\n".format(freq))
for chunk in range(14):
    channel_maps_list = []
    
    # Check if the source directory containing the maps exists and
    # if so, get the maps
    for SOURCE_DIR, product_tag in zip(SOURCE_DIR_LIST, product_tag_list):
        if not os.path.exists(SOURCE_DIR):
            print("Source directory does not exist:")
            print(SOURCE_DIR)
            if os.path.exists(OUTPUT_DIR) and (len(os.listdir(OUTPUT_DIR)) == 0):
                shutil.rmtree(OUTPUT_DIR)
            exit(1)
        channel_maps_list.append(os.path.join(SOURCE_DIR, "vec_"+product_tag+"_chunk{:02d}.fits".format(chunk)))
    
    if len(channel_maps_list) == 3:
        print("Now starting chunk {:02d}: {} maps to coadd".format(chunk, len(channel_maps_list)))

        M = sam.unimap_coadd(files=channel_maps_list, mpi=True, tag=output_tag+"_chunk{:02d}".format(chunk), output=OUTPUT_DIR)
        print("Chunk {:02d} complete".format(chunk))
    else:
        print("Source directory incomplete:")
        print(SOURCE_DIR)
        print("\nCoadding aborted\n")
        continue
