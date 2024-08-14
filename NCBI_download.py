#!/usr/bin/env python3

import os
import sys
import subprocess
import pandas as pd
import numpy as np
import argparse

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

class NCBI_downloader():
    def __init__(self, group, genera, output, mode, complete, excluded):
        self.group = group
        self.genera = genera
        self.output = output
        self.mode = mode
        self.complete = complete
        self.excluded = excluded

    def check_taxa(self, taxa):
        taxa_list = ['viral', 'bacteria', 'archaea', 'protozoa', 'fungi']
        if taxa.lower() not in taxa_list:
            sys.exit(f"{taxa.lower()} not in list of 'fungi', 'bacteria', 'archaea', 'viral' or 'protozoa'. Please double check spelling and try again")

    def dl_summary(self, taxa):
        if os.path.exists(taxa.lower()+"_assembly_summary.txt"):
            print(f"Assembly summary for {taxa.lower()} already exists, skipping downloading")
        else:
            print(f"Downloading {taxa.lower()} summary")
            subprocess.run(['wget', '-O', taxa.lower()+'_assembly_summary.txt', 'https://ftp.ncbi.nlm.nih.gov/genomes/genbank/'+taxa.lower()+'/assembly_summary.txt'])

    def find_genera(self, genera, taxa, excluded):
        print(f"Searching {taxa.lower()}_assembly_summary.txt for {genera}")
        df = pd.read_csv(taxa.lower()+"_assembly_summary.txt", sep='\t', header=1, low_memory=False)
        filtered_df = df[df['organism_name'].str.contains(self.genera)]
        if not excluded:
            filtered_df = filtered_df[(filtered_df.iloc[:, 20] == "na")]
        if self.complete:
            filtered_df = filtered_df[(filtered_df.iloc[:, 11] == "Complete Genome") | (filtered_df.iloc[:, 11] == "Chromosome")]
        return filtered_df[['organism_name', 'infraspecific_name', 'ftp_path', 'isolate', 'gbrs_paired_asm', 'excluded_from_refseq']]


    def make_ftp(self, table, https, excluded):
        if https:
            print("Creating paths with https links")
        if excluded:            
            if https == True:
                table_split = table.ftp_path.str.split("/", expand=True)
                ftp_list = 'https:' +'//' + table_split[2].map(str) + '/' + table_split[3].map(str) + '/' + table_split[4].map(str) + '/' + table_split[5].map(str) + '/' + table_split[6].map(str) + '/' + table_split[7].map(str) + '/' + table_split[8].map(str) + '/' + table_split[9].map(str) + '/' + table_split[9].map(str)  + '_genomic.fna.gz'
                return(ftp_list)
            else:
                table_split = table.ftp_path.str.split("/", expand=True)
                ftp_list = table_split[0].map(str) + '//' + table_split[2].map(str) + '/' + table_split[3].map(str) + '/' + table_split[4].map(str) + '/' + table_split[5].map(str) + '/' + table_split[6].map(str) + '/' + table_split[7].map(str) + '/' + table_split[8].map(str) + '/' + table_split[9].map(str) + '/' + table_split[9].map(str)  + '_genomic.fna.gz'
                return(ftp_list)
        else:
            if https == True:
                table_split = table.ftp_path.str.split("/", expand=True)
                ftp_list = 'https:' +'//' + table_split[2].map(str) + '/' + table_split[3].map(str) + '/' + table_split[4].map(str) + '/' + table_split[5].map(str) + '/' + table_split[6].map(str) + '/' + table_split[7].map(str) + '/' + table_split[8].map(str) + '/' + table_split[9].map(str) + '/' + table_split[9].map(str)  + '_genomic.fna.gz'
                return(ftp_list.str.replace('GCA','GCF'))
            else:
                table_split = table.ftp_path.str.split("/", expand=True)
                ftp_list = table_split[0].map(str) + '//' + table_split[2].map(str) + '/' + table_split[3].map(str) + '/' + table_split[4].map(str) + '/' + table_split[5].map(str) + '/' + table_split[6].map(str) + '/' + table_split[7].map(str) + '/' + table_split[8].map(str) + '/' + table_split[9].map(str) + '/' + table_split[9].map(str)  + '_genomic.fna.gz'
                return(ftp_list.str.replace('GCA','GCF'))

    def human_readable(self, table):
        removed_characters = table['organism_name'] = table['organism_name'].str.replace(' ', "_").str.replace("/", "-")
        strain = table['infraspecific_name'] = table['infraspecific_name'].str.replace(' |strain=', "_").str.replace("/", "-")
        isolate = table['isolate'] = table['isolate'].str.replace(' |strain=', "_")
        isolate = table['isolate'] = "_" + table['isolate']
        df = pd.concat([removed_characters, strain, isolate], axis=1)
        df['human_readable'] = df.fillna('').sum(axis=1)
        df['human_readable'] = df['human_readable'].astype(str) + '.fna.gz'
        return(df['human_readable'])

    def dl_script(self, id, ftp, output):
        print("Preparing a download script of selected genera")
        with open(f"{output}_download_script.sh", 'w') as out_handle:
            out_handle.write("#!/bin/bash\n")
            list = [')', '(', '=', ';']
            for org in range(len(id)):
                line = "wget -O " + id.iloc[org] + " " + ftp.iloc[org] + '\n'
                out_handle.write(str(line).translate({ord(x): '-' for x in list}))

    def run(self):
        self.check_taxa(self.group)
        self.dl_summary(self.group)
        table = self.find_genera(self.genera, self.group, self.excluded)
        ftp = self.make_ftp(table, self.mode, self.excluded)
        id = self.human_readable(table)
        self.dl_script(id, ftp, self.output)

def main():
    parser = argparse.ArgumentParser(description="NCBI Genbank Reference Downloader", add_help=False)

    required = parser.add_argument_group('Required Arguments')
    required.add_argument('-t', '--taxa', type=str, required=True, help="One of either 'fungi', 'bacteria', 'archaea', 'viral' or 'protozoa'")
    required.add_argument('-g', '--genus', type=str, required=False, help="References to download of selected genus")
    required.add_argument('-o', '--out', type=str, required=False, help="Output directory")

    optional = parser.add_argument_group('Optional Arguments')
    optional.add_argument('-m', '--mode_https', default=False, action='store_true', required=False, help="Runs in HTTPS mode (for networks that are not able to access FTP)")
    optional.add_argument('-c', '--complete', action='store_true', required=False, help="Filter to include only complete genomes or chromosomes")
    optional.add_argument("-x", "--excluded_from_refseq", action='store_true', required=False, help="Include genomes excluded from refseq")
    optional.add_argument("-h", "--help", action="help", help="Show this help message and exit")

    args = parser.parse_args()
    taxa = os.path.normpath(args.taxa)
    genus = args.genus
    output = args.out
    mode = args.mode_https
    complete = args.complete
    excluded = args.excluded_from_refseq

    job = NCBI_downloader(taxa, genus, output, mode, complete, excluded)
    job.run()

if __name__ == '__main__':
    main()
