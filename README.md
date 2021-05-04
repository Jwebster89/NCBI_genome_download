# NCBI_genome_download
## Introduction
NCBI_download.py Creates a bash script for downloading all reference genomes of a specified genus. It takes as input a selected taxonomy and a Genus and will output a download_script.sh that can be executed to download all references from a genus in a human readable format.

## Quick Usage
To download all reference sequences of Rhizobia from Genbank.

`./NCBI_download.py -taxa bacteria -genus Rhizobia`

To download all reference sequences of Fusarium from Genbank, using https instead of ftp.

`./NCBI_download.py -t fungi -g Fusarium -m`

## HTTPS and FTP
Some networks may not allow FTP access, using -m/--mode_https allows downloading of genomes with HTTPS instead.

## Human readable
Genomes will be downloaded with a human readable name, e.g. "Fusarium_fujikuroi_KSU_X-10626.fna.gz" instead of "GCA_001023035.1_ASM102303v1_genomic.fna.gz"

## Output
NCBI_download.py produces a bash script for downloading reference genomes with wget. This allows the user to confirm how many genomes are being downloaded before hand, remove any genomes that are not needed as well as partitioning the download file if bandwith is an issue. All genomes are downloaded in a human readable format and their respective genbank accessions are easily viewed in the download script.

## Options and Usage
```
usage: NCBI_download.py -t TAXA [-g GENUS] [-o OUT] [-m] [-h]

NCBI Genbank Reference Downloader 

Required Arguments:
  -t TAXA, --taxa TAXA  One of either 'fungi', 'bacteria', 'archaea', 'viral' or 'protozoa'
  -g GENUS, --genus GENUS
                        References to download of selected genus
  -o OUT, --out OUT     output

Optional Arguments:
  -m, --mode_https      Runs in https mode (for networks that are not able to access ftp)
  -h, --help            show this help message and exit
```
