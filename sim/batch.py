"""
batch.py 

Batch simulation for S1 mouse model using NetPyNE

Contributors: salvadordura@gmail.com, fernandodasilvaborges@gmail.com, joaovvitor@gmail.com
"""
from netpyne.batch import Batch
from netpyne import specs
import numpy as np

# ----------------------------------------------------------------------------------------------
# Custom
# ----------------------------------------------------------------------------------------------
def custom():
    params = specs.ODict()
    
    # params[('seeds', 'conn')] =  [1234]

    params[('rateStimI')] = [5.0]
    params[('rateStimE')] = [25.0]

    b = Batch(params=params, netParamsFile='netParams.py', cfgFile='cfg.py')

    return b

# ----------------------------------------------------------------------------------------------
# Run configurations
# ----------------------------------------------------------------------------------------------
def setRunCfg(b, type='mpi_bulletin'):
    if type=='mpi_bulletin' or type=='mpi':
        b.runCfg = {'type': 'mpi_bulletin', 
            'script': 'init.py', 
            'skip': True}

    elif type=='mpi_direct2': 
        b.runCfg = {'type': 'mpi_direct',
            'mpiCommand': 'mpirun -n 8 ./x86_64/special -mpi -python init.py', # --use-hwthread-cpus # coreneuron
            'skip': True}

    elif type=='mpi_direct':
        b.runCfg = {'type': 'mpi_direct',
            'cores': 8,
            'script': 'init.py',
            'mpiCommand': 'mpiexec', # --use-hwthread-cpus
            'skip': True}

    elif type=='hpc_slurm_gcp':
        b.runCfg = {'type': 'hpc_slurm', 
            'allocation': 'default',
            'walltime': '24:00:00', 
            'nodes': 1,
            'coresPerNode': 40,
            'email': 'fernandodasilvaborges@gmail.com',
            'folder': '/home/ext_fernandodasilvaborges_gmail_/S1_mouse/sim/', 
            'script': 'init.py', 
            'mpiCommand': 'mpirun',
            'skipCustom': '_raster.png'}

    elif type == 'hpc_slurm_Expanse':
        b.runCfg = {'type': 'hpc_slurm',
                    'allocation': 'TG-IBN140002',
                    'partition': 'compute',
                    'walltime': '1:00:00',
                    'nodes': 1,
                    'coresPerNode': 128,
                    'email': 'fernandodasilvaborges@gmail.com',
                    'folder': '/home/fborges/S1_mouse/sim/',
                    'script': 'init.py',
                    'mpiCommand': 'mpirun',
                    'custom': '#SBATCH --mem=249325M\n#SBATCH --export=ALL\n#SBATCH --partition=compute',
                    'skip': True}

# ----------------------------------------------------------------------------------------------
# Main code
# ----------------------------------------------------------------------------------------------
if __name__ == '__main__': 
    b = custom() #

    b.batchLabel = 'v100_batch1'  
    b.saveFolder = '../data/'+b.batchLabel
    b.method = 'grid'
    setRunCfg(b, 'mpi_direct2')
    b.run() # run batch
