#!/bin/bash

# Check if list.txt exists
if [[ ! -f list.txt ]]; then
  echo "Error: The file list.txt does not exist."
  exit 1
fi

# Read each line from list.txt
while IFS= read -r filter_value; do
  # Skip empty lines
  if [[ -z "$filter_value" ]]; then
    continue
  fi
  
  echo "Running the Python script with filter_value: $filter_value"
  
  # Run the Python script with the current filter_value
  python3 app.py --filter_value "$filter_value"
  
  # Check the execution result
  if [[ $? -ne 0 ]]; then
    echo "Error while running Python script with filter_value: $filter_value"
  fi
done < list.txt
