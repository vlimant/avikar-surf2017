import os
import sys
import time


kfolding=10
n_opt_point = 5 
n_nodes = kfolding*n_opt_point + 1 ## one for the master

test = True
dir_name = 'Train_%dx%d'% ( kfolding, n_opt_point)
mpi_script = 'mpi_ijet_%dx%d.pbs'%( kfolding, n_opt_point)
mpi_file = open(mpi_script,'w')
mpi_file.write("""#!/bin/bash
#    Begin PBS directives
#PBS -A hep107
#PBS -N mpi_iJet
#PBS -j oe
###PBS -q debug
#PBS -l walltime=120:00,nodes={0:d}
#    End PBS directives and begin shell commands

cd $MEMBERWORK/hep107

export HOME=/lustre/atlas/scratch/vlimant/hep107/
export PYTHONPATH=/ccs/proj/hep107/sft/lib/python3.5/site-packages/
export CUDA_VISIBLE_DEVICES=0

module load python/3.5.1
module load python_mpi4py

export DATADIR=/lustre/atlas/proj-shared/hep107/iJetData/
export OUTDIR=$DATADIR/{2}/
mkdir -p $OUTDIR/checkpoints/
ln -s $DATADIR $OUTDIR/training

cd /lustre/atlas/proj-shared/hep107/iJet/mpi/
date
aprun -n {0:d} -N 1 python skopt_test_mpi.py --path $OUTDIR --epoch 10000 --kfold {1:d} {3}
""".format(n_nodes,
           kfolding,
           dir_name,
           '--test' if test else ''))
mpi_file.close()

fdafsd
current_mpi_job_id = sys.argv[1] if len(sys.argv)>1 else None
n_submissions = 10
while n_submissions>0:
    if current_mpi_job_id != None:
        while os.popen('showq -u vlimant | grep %s '% current_mpi_job_id).read():
            print ("Job %s is still active, keep waiting"% current_mpi_job_id)
            time.sleep( 60 )

    n_submissions -= 1
    print (time.asctime( time.localtime()))
    print ("Submit the mpi job")
    sub = os.popen('qsub %s'%mpi_script)
    current_mpi_job_id = int(sub.read())
    time.sleep(60) ##it takes some time to get the job id in showq
