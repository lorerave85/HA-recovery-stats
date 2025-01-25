#!/bin/bash

# Controlla se list.txt esiste
if [[ ! -f list.txt ]]; then
  echo "Errore: Il file list.txt non esiste."
  exit 1
fi

# Leggi ogni riga di list.txt
while IFS= read -r filter_value; do
  # Salta righe vuote
  if [[ -z "$filter_value" ]]; then
    continue
  fi
  
  echo "Esecuzione dello script Python con filter_value: $filter_value"
  
  # Esegui lo script Python con il valore corrente di filter_value
  python3 app.py --filter_value "$filter_value"
  
  # Controlla l'esito dell'esecuzione
  if [[ $? -ne 0 ]]; then
    echo "Errore durante l'esecuzione dello script Python con filter_value: $filter_value"
  fi
done < list.txt
