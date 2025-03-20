#!/bin/bash
#SBATCH --job-name=fwf-climo
#SBATCH --output=/home/crodell/fwf/log/climo_%j.out
#SBATCH --error=/home/crodell/fwf/log/climo_%j.err
#SBATCH --partition=icelake
#SBATCH --nodes=1
#SBATCH --ntasks=2  # Match Dask `jobs=2`
#SBATCH --cpus-per-task=2  # Match Dask `cores=2`
#SBATCH --mem=8GB  # 2 workers * 4GB each = 8GB
#SBATCH --time=00:10:00
#SBATCH --mail-type=END,FAIL

# Ensure log directory exists
mkdir -p /home/crodell/fwf/log/

# Activate Conda
source /home/crodell/miniforge3/bin/activate fwx

# Set threading variables
export OMP_NUM_THREADS=1  
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1

# Run the Python script
python -u /home/crodell/fwf/scripts/test/climo/create-climatology-fa.py
