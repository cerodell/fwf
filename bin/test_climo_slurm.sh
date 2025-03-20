#!/usr/bin/env bash

#SBATCH -J dask-worker
#SBATCH --output=/home/crodell/fwf/log/climo_%j.out
#SBATCH --error=/home/crodell/fwf/log/climo_%j.err
#SBATCH -p icelake
#SBATCH -n 1
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G
#SBATCH -t 00:02:00
#SBATCH --export=ALL

/home/crodell/miniforge3/envs/fwx/bin/python -m distributed.cli.dask_worker tcp://192.168.8.150:8786 --name dummy-name --nthreads 2 --memory-limit 3.73GiB --nanny --death-timeout 60 --interface eno8303
