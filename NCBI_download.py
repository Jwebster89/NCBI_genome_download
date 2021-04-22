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
	def __init__(self,group,genera,output,mode):
		self.group=group
		self.genera=genera
		self.output=output
		self.mode=mode


	def check_taxa(self,taxa):
		taxa_list=['viral', 'bacteria', 'archaea', 'protozoa', 'fungi']
		if taxa.lower() not in taxa_list:
			sys.exit(f"{taxa.lower()} not in list of 'fungi', 'bacteria', 'archaea', 'viral' or 'protozoa'. Please double check spelling and try again")

	def dl_summary(self,taxa):
		if os.path.exists(taxa.lower()+"_assembly_summary.txt"):
			print(f"Assembly summary for {taxa.lower()} already exists, skipping downloading")
		else:
			print(f"Downloading {taxa.lower()} summary")
			subprocess.run(['wget','-O',taxa.lower()+'_assembly_summary.txt','https://ftp.ncbi.nlm.nih.gov/genomes/genbank/'+taxa.lower()+'/assembly_summary.txt'])

	def find_genera(self,genera,taxa):
		print(f"Seaerching {taxa.lower()}_assembly_summary.txt for {genera}")
		df = pd.read_csv(taxa.lower()+"_assembly_summary.txt", sep='\t', header=1,low_memory=False)
		filtered_df=(df[df['organism_name'].str.contains(self.genera)])
		return(filtered_df[['organism_name','infraspecific_name','ftp_path']])

	def make_ftp(self,table,https):
		if https:
			print("Creating paths with https links")
		if https == True:
			table_split=table.ftp_path.str.split("/",expand=True)
			ftp_list='https:' +'/' +'/'+table_split[2].map(str) +'/'+table_split[3].map(str) +'/'+table_split[4].map(str) +'/'+table_split[5].map(str) +'/'+table_split[6].map(str) +'/'+table_split[7].map(str) +'/'+table_split[8].map(str) +'/'+table_split[9].map(str)+'/'+table_split[9].map(str)  +'_genomic.fna.gz'
			return(ftp_list)
		else:
			table_split=table.ftp_path.str.split("/",expand=True)
			ftp_list=table_split[0].map(str) +'/' +'/'+table_split[2].map(str) +'/'+table_split[3].map(str) +'/'+table_split[4].map(str) +'/'+table_split[5].map(str) +'/'+table_split[6].map(str) +'/'+table_split[7].map(str) +'/'+table_split[8].map(str) +'/'+table_split[9].map(str)+'/'+table_split[9].map(str)  +'_genomic.fna.gz'
			return(ftp_list)

	def human_readable(self,table):
		removed_characters=table['organism_name'] = table['organism_name'].str.replace(' ', "_")
		strain=table['infraspecific_name']= table['infraspecific_name'].str.replace(' |strain=', "_")
		df = pd.concat([removed_characters, strain], axis=1)
		df['human_readable'] = df.fillna('').sum(axis=1)
		df['human_readable'] = df['human_readable'].astype(str)+'.fna.gz'
		return(df['human_readable'])
		
	def dl_script(self,id,ftp):
		print("Preparing a download script of selected genera")
		with open('download_script.sh','w') as out_handle:
			out_handle.write("#!/bin/bash\n")
			list=[')', '(', '=', ';']
			for org in range(len(id)):
				line="wget -O "+id.iloc[org]+" "+ftp.iloc[org]+'\n'
				out_handle.write(str(line).translate({ord(x): '-' for x in list}))

	def run(self):
		self.check_taxa(self.group)
		self.dl_summary(self.group)
		table=self.find_genera(self.genera, self.group)
		ftp=self.make_ftp(table,self.mode)
		id=self.human_readable(table)
		self.dl_script(id,ftp)
		

def main():
	parser = argparse.ArgumentParser(description="NCBI Genbank Reference Downloader ", add_help=False)

	required = parser.add_argument_group('Required Arguments')
	required.add_argument('-t', '--taxa', type=str, required=True, help="One of either 'fungi', 'bacteria', 'archaea', 'viral' or 'protozoa'")
	required.add_argument('-g', '--genus', type=str, required=False, help="References to download of selected genus")
	required.add_argument('-o', '--out', type=str, required=False, help="output")
	

	optional = parser.add_argument_group('Optional Arguments')
	optional.add_argument('-m', '--mode_https',default=False, action='store_true',required=False, help="Runs in https mode (for networks that are not able to access ftp)")
	optional.add_argument("-h", "--help", action="help", help="show this help message and exit")

	args=parser.parse_args()
	taxa=os.path.normpath(args.taxa)
	genus=args.genus
	output=args.out
	mode=args.mode_https
	
	job = NCBI_downloader(taxa, genus, output,mode)
	job.run()


if __name__ == '__main__':
	main()
