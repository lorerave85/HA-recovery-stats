import sqlite3
import csv
import argparse
import os

def fetch_ids_with_filters(db_path, table_name, unit_column, unit_value, filter_column, filter_value):
    try:
        # Connessione al database SQLite
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()

        # Query parametrizzata per evitare SQL injection
        query = f"SELECT id FROM {table_name} WHERE {unit_column} = ? AND {filter_column} = ?"
        cursor.execute(query, (unit_value, filter_value))

        # Recupero degli ID
        ids = [row[0] for row in cursor.fetchall()]

        # Chiusura della connessione
        cursor.close()
        connection.close()

        return ids

    except sqlite3.Error as e:
        print(f"Error accessing database: {e}")
        return None

def fetch_statistics_with_metadata_id(db_path, table_name, metadata_id, statistic_id, unit_value):
    try:
        # Connessione al database SQLite
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()

        # Query parametrizzata per filtrare metadata_id e sum non NULL
        query = f"SELECT '{statistic_id}' AS statistic_id, '{unit_value}' AS unit, strftime('%d.%m.%Y %H:%M', start_ts, 'unixepoch') AS start, state, sum FROM {table_name} WHERE metadata_id = ? AND sum IS NOT NULL"
        cursor.execute(query, (metadata_id,))

        # Recupero dei dati
        rows = cursor.fetchall()

        # Recupero dei nomi delle colonne
        column_names = [description[0] for description in cursor.description]

        # Chiusura della connessione
        cursor.close()
        connection.close()

        # Restituzione dei dati come lista di dizionari
        return [dict(zip(column_names, row)) for row in rows]

    except sqlite3.Error as e:
        print(f"Error accessing database: {e}")
        return None

def export_to_tsv(data, output_file):
    try:
        # Creazione della directory di output se non esiste
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        # Scrittura dei dati in formato TSV
        with open(output_file, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=data[0].keys(), delimiter='\t')
            writer.writeheader()
            writer.writerows(data)
        print(f"Data successfully exported to {output_file}.")
    except Exception as e:
        print(f"Error while exporting data: {e}")

if __name__ == "__main__":
    # Parser per i parametri dello script
    parser = argparse.ArgumentParser(description="Extract data from SQLite database and export it to TSV.")
    parser.add_argument("--filter_value", required=True, help="Value of statistic_id parameter to filter (es: sensor.luce_scrivania_energy).")
    
    args = parser.parse_args()

    # Specifica il percorso del database e il nome della tabella
    database_path = "/Users/ravello001/Downloads/old_home-assistant_v2.db"
    table_name_meta = "statistics_meta"
    table_name_stats = "statistics"
    unit_column = "unit_of_measurement"
    unit_value = "kWh"
    filter_column = "statistic_id"

    # Recupera il valore di filter_value dal parametro
    filter_value = args.filter_value

    # Estrai il nome della directory dall'argomento filter_value
    directory_name = filter_value.split(".", 1)[-1]
    output_file = os.path.join(directory_name, "statisticdata.tsv")

    # Recupera gli ID filtrati
    ids = fetch_ids_with_filters(database_path, table_name_meta, unit_column, unit_value, filter_column, filter_value)

    if ids:
        print("ID found with unit_of_measurement = 'kWh' e statistic_id specificato:")
        for id in ids:
            print(id)

        all_stats_data = []
        # Esegui query sulla tabella statistics per ogni ID
        for metadata_id in ids:
            stats_data = fetch_statistics_with_metadata_id(database_path, table_name_stats, metadata_id, filter_value, unit_value)
            if stats_data:
                print(f"Data found for metadata_id = {metadata_id}:")
                #for row in stats_data:
                #    print(row)
                all_stats_data.extend(stats_data)
            else:
                print(f"No data found per metadata_id = {metadata_id}.")

        if all_stats_data:
            export_to_tsv(all_stats_data, output_file)
    else:
        print("No ID found or error while downloading.")
