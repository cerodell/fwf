from dask_jobqueue import SLURMCluster
from dask.distributed import Client


# compute_node_ip = '10.24.48.1'
# compute_node_host = "pangea01"
cluster = SLURMCluster(
    cores=2,
    memory="4GB",
    processes=1,
    walltime="00:02:00",
    log_directory="/home/crodell/fwf/log",
    job_name="fwf_dask_cluster"  # Custom job name
    # scheduler_options={"host": compute_node_host}
)
cluster.scale(2)

print(cluster.job_script())


client = Client(cluster)
print(client)




import subprocess

# def salloc(nodes=1, ntasks=2, time="00:10:00"):
#     cmd = f"salloc --nodes={nodes} --ntasks-per-node={ntasks} --time={time}"
#     process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#     print(f"SLURM job requested. Process ID: {process.pid}")
#     return process

# # Example call
# salloc()

# cmd = f"squeue -u $USER"

# subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# from dask_jobqueue import SLURMCluster
# from dask.distributed import Client
# import socket

# # Automatically determine the correct IP to bind to
# scheduler_ip = socket.gethostbyname(socket.gethostname())

# cluster = SLURMCluster(
#     cores=2,  
#     memory="32GB",
#     processes=1,
#     walltime="00:10:00",
#     queue="regular",
#     log_directory="/home/crodell/fwf/log",
# )


# cluster.scale(2)  # Scale up to 2 workers
# client = Client(cluster)

# print(client)
# print("Dask Dashboard:", cluster.dashboard_link)



# def salloc(nodes=1, ntasks=2, time="00:30:00", mem="32G"):
#     """Request an interactive SLURM job matching the LocalCluster setup."""
#     cmd = f"salloc --nodes={nodes} --ntasks-per-node={ntasks} --time={time} --mem={mem}"
#     process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

#     # Allow time for SLURM to allocate resources
#     # time.sleep(5)

#     print(f"SLURM interactive job requested with {nodes} nodes, {ntasks} tasks per node, {mem} memory, for {time}.")
#     return process

# # Example call: Match LocalCluster resources
# salloc(nodes=1, ntasks=2, time="00:30:00", mem="32G")

# Start Dask LocalCluster inside the SLURM allocated node