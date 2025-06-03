import os
import pandas as pd

def merge_tsv_files(input_dir, output_file):
    all_dfs = []
    
    # Scansiona tutte le cartelle nella directory principale
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if file.endswith(".tsv"):  # Controlla se il file è un TSV
                file_path = os.path.join(root, file)
                print(f"Reading: {file_path}")
                df = pd.read_csv(file_path, sep='\t', low_memory=False)
                all_dfs.append(df)
    
    if all_dfs:
        merged_df = pd.concat(all_dfs, ignore_index=True)
        merged_df.to_csv(output_file, sep='\t', index=False)
        print(f"Merged file saved as: {output_file}")
    else:
        print("No .tsv files found!")

# Imposta la cartella principale e il nome del file di output
input_directory = "stats"  # Modifica con il percorso corretto
output_file = "statisticdata.tsv"

merge_tsv_files(input_directory, output_file)
