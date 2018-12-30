import os, shutil

def del_dirs(dir_list, notice):
    del_flag = False    # flag becomes True if any directory is deleted
    exs_list = [os.path.exists(d) for d in dir_list]
    if True in exs_list:
        print(notice)
    for d, e in zip(dir_list, exs_list):
        if e:
            print(d)
            shutil.rmtree(d)
            del_flag = True
    return del_flag


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
            # ... then delete the TODs (if they are still on disk)
            dir_list = [os.path.join(ROOT_DIR, "filt_X{}_full_noise_sim_{:04d}".format(fpu, r)) for fpu in range(1, 7)]
            notice = "\nRun {} complete; removing TODs from:\n".format(r)
            del_count = del_dirs(dir_list, notice)

            # Check for any intermediary maps created by MPI and delete them too
            dir_list = [os.path.join(MAPS_DIR, "filt_X{}_full_noise_sim_{:04d}_interleaved_mpi".format(fpu, r)) for fpu in range(1, 7)]
            notice = "\nRemoving intermediary maps made by each MPI process...\n"
            del_count = del_count + del_dirs(dir_list, notice)
            
            # Check for any detector-specific maps (e.g., X1-only maps) and delete them too
            dir_list = [os.path.join(MAPS_DIR, "filt_X{}_full_noise_sim_{:04d}_interleaved".format(fpu, r)) for fpu in range(1, 7)]
            notice = "\nRemoving detector-specific maps...\n"
            del_count = del_count + del_dirs(dir_list, notice)

            # Print a notice if a run was cleaned
            if del_count > 0:
                print("\nRun {} cleaned\n".format(r))
                print("----------\n")

        # ... or these directories are empty...
        elif len(os.listdir(DIR_PATH_100)) == 0 and len(os.listdir(DIR_PATH_143)) == 0:
            # ... then delete these directories
            print("\nRun {} maps missing; deleting empty directories...\n".format(r))
            os.rmdir(DIR_PATH_100)
            os.rmdir(DIR_PATH_143)
            print("\nRun {} cleaned\n".format(r))
            print("----------\n")

print("Finished!\n")
