#!/bin/bash
#SBATCH --job-name=createdb
#SBATCH --output=logs/%x_%A_%a.out
#SBATCH --error=logs/%x_%A_%a.err
#SBATCH --array=0-4
#SBATCH --cpus-per-task=2
#SBATCH --mem=4G
#SBATCH --time=04:00:00

# Load apptainer
module load apptainer

DATABASE="bacteria.db"

apptainer exec --bind ~/scratch/repos/BIOS270_AU25_aj/Data:/data --bind /farmshare/home/classes/bios/270/data:/shared_data ~/scratch/repos/BIOS270_AU25_aj/Environment/bioinformatics_latest.sif python /data/insert_gff_table.py --database_path $DATABASE
apptainer exec --bind ~/scratch/repos/BIOS270_AU25_aj/Data:/data --bind /farmshare/home/classes/bios/270/data:/shared_data ~/scratch/repos/BIOS270_AU25_aj/Environment/bioinformatics_latest.sif python /data/insert_protein_cluster_table.py --database_path $DATABASE
apptainer exec --bind ~/scratch/repos/BIOS270_AU25_aj/Data:/data --bind /farmshare/home/classes/bios/270/data:/shared_data ~/scratch/repos/BIOS270_AU25_aj/Environment/bioinformatics_latest.sif python /data/insert_metadata_table.py --database_path $DATABASE
