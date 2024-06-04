#!/bin/bash

# Check if the number of arguments is correct
if [ "$#" -ne 5 ]; then
    echo "Usage: $0 <search_phrase> <clone_dest> <log_file> <output_file> <script_val>"
    exit 1
fi

# Get the search phrase and output file name from the arguments
phrase="$1"
clone_dest=$2
log_file="$3"
output_file="$4"
script_val=$5

# Check if any files were found
if [ $script_val = "1" ]; then
  
  files=$(grep -rl "$phrase" --include="*.c" --include="*.C" --include="*.cpp" --include="*.F90" $clone_dest)

  if [ -z "$files" ]; then
    echo "No files found containing the phrase '$phrase'."
  else
    # Loop through the list of files
    for file in $files; do
	  echo "Processing file: $file"
	  echo "$filename" >> "$log_file"
      echo "--------------------------" >> "$output_file"
      echo "File: $file" >> "$output_file"
      echo "--------------------------" >> "$output_file"
        # Append the contents of each file to the output file
      cat "$file" >> "$output_file"
      echo "" >> "$output_file"
    
    done
    echo "All content has been concatenated into $output_file (phrase)"
  fi
  
elif [ $script_val = "2" ]; then
  # Find all files that directly include <openacc.h> or <omp.h>
  direct_files=$(grep -rl "$phrase" --include="*.c" --include="*.cpp" --include="*.F90" $clone_dest)

  # Find all header files that include <openacc.h> or <omp.h>
  indirect_headers=$(grep -rl "$phrase" --include="*.h" --include="*.Fh" $clone_dest )

  indirect_files=""

  echo "*******$indirect_headers*******"

  # Find all files that include <openacc.h> via a headerfile
  for header in $indirect_headers; do 
    #basename allows you to get rid of the path and only have the name of the header file
    header_filename=$(basename "$header")
    echo "$header_filename"
    indirect_files+=$(grep -rl "$header_filename" --include="*.c" --include="*.cpp" --include="*.F90" $clone_dest)
    
    echo "$indirect_files"
  done

  all_files=$(echo -e "$indirect_files\n$direct_files" | sort -u)
    
  if [ -z "$all_files" ]; then
  echo "No files found containing the phrase."
  else
    for file in $all_files; do
      echo "Processing file: $file"
      filename=$(basename "$file")
	  if grep -q "$filename" "$log_file"; then
	    echo "Skipping $filename, already processed"
      else
        echo "--------------------------" >> "$output_file"
        echo "File: $file" >> "$output_file"
        echo "--------------------------" >> "$output_file"
        cat "$file" >> "$output_file"
        echo "" >> "$output_file"
	  fi
    done
    echo "All content has been concatenated into $output_file (headers)"
  fi
fi