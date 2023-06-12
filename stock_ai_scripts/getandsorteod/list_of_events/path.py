import os

# Get the directory of the script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Set n to the number of levels you want to go up
n = 2

# Get the parent directory of the script directory n times
for i in range(n):
    script_dir = os.path.abspath(os.path.join(script_dir, os.pardir))

with open(script_dir+"/path_names.txt", "r") as file:
    # Read the contents of the file
    contents = file.read()

    # Split the contents into lines
    lines = contents.split("\n")

    # Extract the values of script_path and data_path
    script_path = lines[0].split(" = ")[1]
    data_path = lines[1].split(" = ")[1]  