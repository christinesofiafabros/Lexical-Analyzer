import main
import os

# Define the allowed file extension
allowed_extension = ".ms"

# Check if the file exists and has the correct extension
input_file_path = 'test.ms'
output_file_path = 'symbol_table.txt'

if os.path.isfile(input_file_path) and input_file_path.endswith(allowed_extension):
    with open(input_file_path, 'r') as input_file:
        lines = input_file.readlines()  # Read all lines from the file

    # Initialize an empty list to collect all tokens
    all_tokens = []

    # Iterate through each line in the file
    for line_number, line in enumerate(lines, 1):
        line = line.strip()
        result, error = main.run('<stdin>', line)

        if error:
            print(error.as_string())
            break  # Exit loop if an error occurs
        else:
            all_tokens.extend(result)  # Collect tokens from each line

    if not error:
        # Generate symbol table from all collected tokens
        symbol_table = main.generate_symbol_table(all_tokens)

        # Visualize and save the symbol table in a text file
        main.visualize_symbol_table(symbol_table, output_file_path)
else:
    print(f"File '{input_file_path}' either doesn't exist or doesn't have the '{allowed_extension}' extension.")
