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
    def __init__(self, group, genera, output, mode, complete, excluded, reference, type_strain, accession):
        self.group = group
        self.genera = genera
        self.output = output
        self.mode = mode
        self.complete = complete
        self.reference = reference
        self.excluded = excluded
        self.type_strain = type_strain
        self.accession = accession

    def check_taxa(self, taxa):
        taxa_list = ['viral', 'bacteria', 'archaea', 'protozoa', 'fungi']
        if taxa.lower() not in taxa_list:
            sys.exit(f"{taxa.lower()} not in list of 'fungi', 'bacteria', 'archaea', 'viral' or 'protozoa'. Please double check spelling and try again")

    def dl_summary(self, taxa):
        if os.path.exists(taxa.lower()+"_assembly_summary.txt"):
            print(f"Assembly summary for {taxa.lower()} already exists, skipping downloading")
        else:
            print(f"Downloading {taxa.lower()} summary")
            subprocess.run(['wget', '-O', taxa.lower()+'_assembly_summary.txt', 'https://ftp.ncbi.nlm.nih.gov/genomes/genbank/'+taxa.lower()+'/assembly_summary.txt', "--no-check-certificate"])

    def find_genera(self, genera, taxa, excluded):
        print(f"Searching {taxa.lower()}_assembly_summary.txt for {genera}")
        df = pd.read_csv(taxa.lower()+"_assembly_summary.txt", sep='\t', header=1, low_memory=False)
        filtered_df = df[df['organism_name'].str.contains(self.genera, na=False)]
        if not excluded:
            filtered_df = filtered_df[(filtered_df.iloc[:, 20] == "na")]
        if self.complete:
            filtered_df = filtered_df[(filtered_df.iloc[:, 11] == "Complete Genome") | (filtered_df.iloc[:, 11] == "Chromosome")]
        if self.reference:
            filtered_df = filtered_df[(filtered_df.iloc[:, 4] == "reference genome")]
        if self.type_strain:
            filtered_df = filtered_df[(filtered_df.iloc[:, 21] == "assembly from type material")]
        return filtered_df[['#assembly_accession','organism_name', 'infraspecific_name', 'ftp_path', 'isolate', 'gbrs_paired_asm', 'excluded_from_refseq']]


    def make_ftp(self, table, https, excluded):
        if https:
            print("Creating paths with https links")

        table_split = table.ftp_path.str.split("/", expand=True)

        if https:
            ftp_list = (
                'https://' + table_split[2].map(str) + '/' + table_split[3].map(str) + '/' +
                table_split[4].map(str) + '/' + table_split[5].map(str) + '/' +
                table_split[6].map(str) + '/' + table_split[7].map(str) + '/' +
                table_split[8].map(str) + '/' + table_split[9].map(str) + '/' +
                table_split[9].map(str) + '_genomic.fna.gz'
            )
        else:
            ftp_list = (
                table_split[0].map(str) + '//' + table_split[2].map(str) + '/' +
                table_split[3].map(str) + '/' + table_split[4].map(str) + '/' +
                table_split[5].map(str) + '/' + table_split[6].map(str) + '/' +
                table_split[7].map(str) + '/' + table_split[8].map(str) + '/' +
                table_split[9].map(str) + '/' + table_split[9].map(str) + '_genomic.fna.gz'
            )

        if excluded:
            return ftp_list

        paired_mask = table['gbrs_paired_asm'].notna() & (table['gbrs_paired_asm'] != 'na')
        ftp_list = ftp_list.where(~paired_mask, ftp_list.str.replace('GCA', 'GCF', regex=False))

        return ftp_list  

    def human_readable(self, table):
        table['organism_name'] = table['organism_name'].str.replace("/", "-").str.replace(" ", "_").str.replace(":", "_").str.replace("_na_", "", case=False).str.replace(",","").str.replace("[","").str.replace("]","")
        table['infraspecific_name'] = table['infraspecific_name'].str.replace('strain=', "").str.replace("/", "-").str.replace(" ", "_").str.replace(":", "_").str.replace("na", "", case=False).str.replace(",","").str.replace("[","").str.replace("]","")
        
        table['isolate'] = table['isolate'].str.replace('strain=', "").str.replace("/", "-").str.replace(" ", "_").str.replace(":", "_").str.replace("na", "", case=False).str.replace(",","").str.replace("[","").str.replace("]","")
        table['isolate'] = table['isolate'].apply(lambda x: "_" + x if x.strip() else "")
       
        table['download_accession'] = table['#assembly_accession']
        paired_mask = table['gbrs_paired_asm'].notna() & (table['gbrs_paired_asm'] != 'na')
        table.loc[paired_mask, 'download_accession'] = table.loc[paired_mask, 'gbrs_paired_asm']
       
        if self.accession:
            df = table.apply(lambda row: '_'.join(filter(None, [row['download_accession'], row['organism_name'], row['infraspecific_name'], row['isolate']])), axis=1)
        else:
            df = table.apply(lambda row: '_'.join(filter(None, [row['organism_name'], row['infraspecific_name'], row['isolate']])), axis=1)
        df = df + '.fna.gz'
        return df

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
    required.add_argument('-g', '--genus', type=str, required=True, help="References to download of selected genus")
    required.add_argument('-o', '--out', type=str, required=True, help="Output directory")

    optional = parser.add_argument_group('Optional Arguments')
    optional.add_argument('-m', '--mode_https', default=False, action='store_true', required=False, help="Runs in HTTPS mode (for networks that are not able to access FTP)")
    optional.add_argument('-c', '--complete', action='store_true', required=False, help="Filter to include only complete genomes or chromosomes")
    optional.add_argument('-s', '--type_strain', action='store_true', required=False, help="Filter to include only assemblies from type material")
    optional.add_argument('-r', '--reference', action='store_true', required=False, help="Filter to include only Refseq reference genomes")
    optional.add_argument("-x", "--excluded_from_refseq", action='store_true', required=False, help="Include genomes excluded from refseq")
    optional.add_argument("-a", "--accession", default=False, action='store_true', required=False, help="Include Accession in filename. Default False")
    optional.add_argument("-h", "--help", action="help", help="Show this help message and exit")

    args = parser.parse_args()
    taxa = os.path.normpath(args.taxa)
    genus = args.genus
    output = args.out
    mode = args.mode_https
    complete = args.complete
    reference = args.reference
    type_strain = args.type_strain
    excluded = args.excluded_from_refseq
    accession = args.accession

    job = NCBI_downloader(taxa, genus, output, mode, complete, excluded, reference, type_strain, accession)
    job.run()

if __name__ == '__main__':
    main()
