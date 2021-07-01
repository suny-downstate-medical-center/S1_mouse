#!/bin/bash
#SBATCH --job-name=v1_batch5_1_1
#SBATCH -A default
#SBATCH -t 24:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=80
#SBATCH -o ../data/v1_batch5/v1_batch5_1_1.run
#SBATCH -e ../data/v1_batch5/v1_batch5_1_1.err
#SBATCH --mail-user=salvadordura@gmail.com
#SBATCH --mail-type=end



source ~/.bashrc
cd /home/ext_fernandodasilvaborges_gmail_/S1_mouse/sim/
mpirun -n 80 nrniv -python -mpi init.py simConfig=../data/v1_batch5/v1_batch5_1_1_cfg.json netParams=../data/v1_batch5/v1_batch5_netParams.py
wait
                    