#!/bin/bash                                                                     
#run via: >bash mpi_launcher.sh                                         
#requires mpi_example.sh and mpi_example.py to work                             
psubset='full'
run='0000'
for f in 1 2 3 4 5 6 ; do     #which fpu to run
    echo sbatch mpi_filt_planck_noise_maps.sh $f $psubset $run
    sbatch --job-name="filt_planck_noise_maps_x$f.run$run" --export="f=$f,psubset=$psubset,run=$run" mpi_filt_planck_noise_maps.sh
    sleep 1
done
