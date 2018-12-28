#!/bin/bash
#SBATCH -A rrg-rbond-ac
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=40
#SBATCH --time=5:00:00
#SBATCH --job-name filt_planck_noise_maps_$f

# DIRECTORY TO RUN - $PBS_O_WORKDIR is directory job was submitted from         
cd /project/r/rbond/jleung/code/planck_noise_maps/
source /project/r/rbond/spider/module_setup.sh

python make_format_files.py $f $psubset $run
mpirun -n 40 python mpi_filt_planck_noise_maps.py $f $psubset $run

for chunk in 0 1 2 3 4 5 6 7 8 9 10 11 12 13 ; do
    mpirun -n 40 python mpi_make_interleaved_planck_noise_maps.py $f $psubset $run $chunk
done
python coadd_interleaved_planck_noise_maps.py $f $psubset $run
