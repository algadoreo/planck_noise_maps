# Generate and filter _Planck_ noise realizations

#### Jason Leung, as part of the SPIDER collaboration

## Overview

This suite turns a _Planck_ noise realization map into a filtered SPIDER map.

For each detector on SPIDER, the steps are:
1. Reobserve with the detector’s beam to obtain a time-ordered product (TOD), a.k.a. a timestream
2. Filter the TOD with a polynomial filter (`polyfilter`) to get rid off scan-synchronous noise
3. Produce a series of maps for each 3-minute chunkset (“interleaving”)
4. (Optional) Co-add the maps for detectors within the same frequency band

## Pre-requisites

Other than having the latest versions of `numpy` and `spider_tools`, this suite makes extensive use of MPI to speed up computations – specifically the `mpi4py` package.

## Usage

If you are on a system with a SLURM scheduler, `mpi_launcher.sh` is your job-submitting script. Modify it as needed. For maximum efficiency, use a loop inside this script to avoid having to manually submit multiple jobs.

It runs through steps 1–3 above in one go by calling `mpi_filt_planck_noise_maps.sh`. Be sure to check the `SBATCH` options first!
