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
file_mode=$5

direct_files=""
indirect_files=""

echo "" >> "$log_file"
echo "" >> "$output_file"

# Section for C files
if [ $file_mode = "1" ]; then
	direct_files=$(grep -rl "$phrase" --include="*.c" --include="*.cpp" $clone_dest)
	indirect_headers=$(grep -rl "$phrase" --include="*.h" $clone_dest )
	indirect_files=""

	echo "*******$indirect_headers*******"

	# Find all files that include <openacc.h> via a headerfile
	for header in $indirect_headers; do 
		#basename allows you to get rid of the path and only have the name of the header file
		header_filename=$(basename "$header")
		echo "$header_filename"
		indirect_files+=$(grep -rl "$header_filename" --include="*.c" --include="*.cpp" $clone_dest)
		indirect_files+="\n"

		#echo "$indirect_files"
	done

#Section for Fortran
else
	direct_files=$(grep -rl "$phrase" --include="*.F90" $clone_dest)
	indirect_headers=$(grep -rl "$phrase" --include="*.Fh" --include="*.FH" $clone_dest )
	indirect_files=""

	echo "*******$indirect_headers*******"

	# Find all files that include <openacc.h> via a headerfile
	for header in $indirect_headers; do 
		#basename allows you to get rid of the path and only have the name of the header file
		header_filename=$(basename "$header")
		echo "$header_filename"
		indirect_files+=$(grep -rl "$header_filename" --include="*.F90" $clone_dest)
		indirect_files+="\n"
		
		#echo "$indirect_files"
	done
fi

all_files=$(echo -e "$indirect_files\n$direct_files")
if [ -z "$all_files" ]; then
	echo "No files found containing the phrase."
	else
	for file in $all_files; do
	  echo "Processing file: $file"
	  filename=$(basename "$file")
	  if grep -q "$file" "$log_file"; then
		echo "Skipping $filename, already processed"
	  else
		echo "$file\n" >> "$log_file"
		echo "--------------------------" >> "$output_file"
		echo "File: $file" >> "$output_file"
		echo "--------------------------" >> "$output_file"
		cat "$file" >> "$output_file"
		echo "" >> "$output_file"
		rm "$file"
	  fi
	done
	echo "All content has been concatenated into $output_file (headers)"
fi