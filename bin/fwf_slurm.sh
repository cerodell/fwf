#!/bin/bash
#SBATCH --job-name=fwf  # Job name
#SBATCH --output=/home/crodell/fwf/log/fwf%j.out  # Standard output log
#SBATCH --error=/home/crodell/fwf/log/fwf%j.err   # Error log
#SBATCH --partition=icelake  # Use the correct partition
#SBATCH --nodes=1  # Run on a single node
#SBATCH --ntasks=1 # Number of tasks (workers)
#SBATCH --mem=32G  # Allocate memory (adjust based on needs)
#SBATCH --time=5:00:00   # Time limit (hh:mm:ss)
#SBATCH --mail-type=END,FAIL

# Ensure log directory exists
mkdir -p /home/crodell/fwf/log/

# Activate the Conda environment
source /home/crodell/miniforge3/bin/activate fwx

# Set threading environment variables for optimal performance
export OMP_NUM_THREADS=1  # Prevent interference with ThreadPoolExecutor
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1

# Run the Python script
python -u /home/crodell/fwf/scripts/run-multi-dates.py
