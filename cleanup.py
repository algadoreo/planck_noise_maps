import os, shutil


ROOT_DIR = "/scratch/r/rbond/jleung/output/planck_noise_maps/"
MAPS_DIR = os.path.join(ROOT_DIR, "filtered_maps")

# Check that the process has finished for a particular noise sim
for r in range(100):
    dir_name_100 = "filt_100_full_noise_sim_{:04d}_interleaved".format(r)
    DIR_PATH_100 = os.path.join(MAPS_DIR, dir_name_100)
    dir_name_143 = "filt_143_full_noise_sim_{:04d}_interleaved".format(r)
    DIR_PATH_143 = os.path.join(MAPS_DIR, dir_name_143)

    # If both 100 and 143 GHz directories exist...
    if os.path.exists(DIR_PATH_100) and os.path.exists(DIR_PATH_143):
        # ... and their maps are all present...
        if len(os.listdir(DIR_PATH_100)) == 56 and len(os.listdir(DIR_PATH_143)) == 56:
            # ... then delete the TODs
            print("\nRun {} complete; removing TODs from:\n".format(r))
            dir_list = [os.path.join(ROOT_DIR, "filt_X{}_full_noise_sim_{:04d}".format(fpu, r)) for fpu in range(1, 7)]
            for d in dir_list:
                if os.path.exists(d):
                    print(d)
                    shutil.rmtree(d)

            # Check for any intermediary maps created by MPI and delete them too
            dir_list = [os.path.join(MAPS_DIR, "filt_X{}_full_noise_sim_{:04d}_interleaved_mpi".format(fpu, r)) for fpu in range(1, 7)]
            print("\nRemoving intermediary maps made by each MPI process...\n")
            for d in dir_list:
                if os.path.exists(d):
                    print(d)
                    shutil.rmtree(d)
            
            dir_list = [os.path.join(MAPS_DIR, "filt_X{}_full_noise_sim_{:04d}_interleaved".format(fpu, r)) for fpu in range(1, 7)]
            print("\nRemoving the per-detector maps...\n")
            for d in dir_list:
                if os.path.exists(d):
                    print(d)
                    shutil.rmtree(d)

            print("Run {} cleaned\n".format(r))
            print("----------\n")

        # ... or these directories are empty...
        elif len(os.listdir(DIR_PATH_100)) == 0 and len(os.listdir(DIR_PATH_143)) == 0:
            # ... then delete these directories
            print("\nRun {} maps missing; deleting empty directories...\n".format(r))
            os.rmdir(DIR_PATH_100)
            os.rmdir(DIR_PATH_143)
            print("Run {} cleaned\n".format(r))
            print("----------\n")

print("Finished!\n")
