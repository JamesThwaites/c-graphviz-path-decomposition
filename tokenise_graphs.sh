#!/bin/bash

# Check if a directory is provided as an argument
if [ $# -ne 2 ]; then
    echo "Usage: $0 <input_directory> <output_directory>"
    exit 1
fi

# Get the directory names
input_directory=$1
output_directory=$2

# Create the output directory if it doesn't exist
mkdir -p "$output_directory"

# Loop through all files in the input directory
for file in "$input_directory"/*; do
    # Check if the file is a regular file
    if [[ -f "$file" ]]; then
        # Get the base name of the file (without the path)
        base_name=$(basename "$file")

        # Construct the output file path
        output_file="$output_directory/$base_name"

        echo $base_name
        # Execute the Python script on the file and redirect the output to the output file
        python read_dotgraph_tokenise.py "$file" > "$output_file"
    fi
done