#!/bin/bash
#SBATCH -J test_workflow
#SBATCH -p general
#SBATCH -o %x_%j.txt
#SBATCH -e %x_%j.err
#SBATCH --mail-type=ALL
#SBATCH --mail-user=jmccombs@iu.edu
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --time=05:00:00
#SBATCH --mem=1G
#SBATCH -A r00606

nextflow run ardac_etl_workflow.nf -config nextflow.config -profile conda,workstation --subjects_type clinical

