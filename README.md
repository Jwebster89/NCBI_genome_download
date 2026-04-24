# NCBI_genome_download

## Introduction
`NCBI_download.py` creates a bash script for downloading genome assemblies from NCBI for a specified genus within a selected taxonomic group. The script searches the relevant NCBI assembly summary table, filters entries based on the selected options, and writes a `wget` download script with human-readable output filenames.

By default, genomes excluded from RefSeq are omitted. Where a paired RefSeq assembly is available, the script uses the corresponding GCF download path; otherwise it retains the original GCA path.

## Quick Usage

Download all assemblies for *Rhizobium* from the bacterial GenBank summary:

`./NCBI_download.py -t bacteria -g Rhizobium -o Rhizobium_all`

Download complete or chromosome-level assemblies for *Fusarium* using HTTPS:

`./NCBI_download.py -t fungi -g Fusarium -m -c -o Fusarium_complete`

Download only RefSeq reference genomes for *Erwinia* and include the accession in the output filename:

`./NCBI_download.py -t bacteria -g Erwinia -r -a -o Erwinia_reference`

Download only assemblies from type material for a genus:

`./NCBI_download.py -t fungi -g Fusarium -s -o Fusarium_type_material`

Include genomes that have been excluded from RefSeq:

`./NCBI_download.py -t bacteria -g Erwinia -x -o Erwinia_including_excluded`

## HTTPS and FTP

Some networks do not allow FTP access. Use `-m` / `--mode_https` to generate HTTPS download links instead of FTP links.

## Human-readable filenames

Genomes are downloaded with human-readable filenames, for example:

`Erwinia_persicina_CFBP8803` rather than just the accession.

If `-a` / `--accession` is used, the accession being downloaded is added to the front of the filename, for example:

`GCF_014839105.1_Erwinia_persicina_CFBP8803.fna.gz`

The script attempts to clean problematic filename characters such as spaces, commas, colons, slashes, and square brackets. Manual checking is still recommended before running the generated download script.

## Complete genomes only

The `-c` / `--complete` option filters the results to include only assemblies with assembly level:

- `Complete Genome`
- `Chromosome`

## Type material only

The `-s` / `--type_strain` option filters the results to include only assemblies labelled as:

- `assembly from type material` within the assembly summary file.

## Reference genomes only

The `-r` / `--reference` option filters the results to include only assemblies where `refseq_category` is:

- `reference genome`

This is separate from whether the downloaded file is GCA or GCF.

## RefSeq-excluded genomes

Some genomes have been excluded from RefSeq for reasons such as unverified source organism, annotation failures, misassemblies, low-quality sequence, or mixed cultures.

By default, these excluded genomes are omitted. If a paired RefSeq assembly is available for a retained record, the script swaps the GCA-based path to the corresponding GCF-based path. If no paired RefSeq assembly exists, the original GCA path is kept.

The `-x` / `--excluded_from_refseq` flag includes assemblies that would otherwise be excluded.

## Output

`NCBI_download.py` produces a bash script containing `wget` commands. This allows you to:

- inspect how many genomes will be downloaded before starting
- remove entries you do not want
- split the download script into smaller batches if bandwidth is limited

All genomes are downloaded with human-readable names, and the accession can optionally be included in the output filename.

## Options and usage

```text
usage: NCBI_download.py -t TAXA -g GENUS -o OUT [-m] [-c] [-s] [-r] [-x] [-a] [-h]

NCBI Genbank Reference Downloader

Required Arguments:
  -t TAXA, --taxa TAXA
                        One of either 'fungi', 'bacteria', 'archaea', 'viral' or 'protozoa'
  -g GENUS, --genus GENUS
                        References to download of selected genus
  -o OUT, --out OUT     Output directory

Optional Arguments:
  -m, --mode_https      Runs in HTTPS mode (for networks that are not able to access FTP)
  -c, --complete        Filter to include only complete genomes or chromosomes
  -s, --type_strain     Filter to include only assemblies from type material
  -r, --reference       Filter to include only RefSeq reference genomes
  -x, --excluded_from_refseq
                        Include genomes excluded from RefSeq
  -a, --accession       Include accession in filename
  -h, --help            Show this help message and exit
  ```