import main
import os

# Define the allowed file extension
allowed_extension = ".ms"

# Check if the file exists and has the correct extension
file_path = 'test.ms' 
if os.path.isfile(file_path) and file_path.endswith(allowed_extension):
    with open(file_path, 'r') as file:
        lines = file.readlines()  # Read all lines from the file

    # Iterate through each line in the file
    for line in lines:
        line = line.strip()  
        result, error = main.run('<stdin>', line)

        if error:
            print(error.as_string())
        else:
            print(result)
else:
    print(f"File '{file_path}' doesn't have the '{allowed_extension}' extension.")

