import json
import csv

# Define the path to the JSON file
json_file_path = r'C:\Users\lolic\githubs\JingSpringThing\webxr-graph\processed_files;C\graph-data.json'

# Load JSON data
try:
    with open(json_file_path, 'r') as json_file:
        data = json.load(json_file)
except Exception as e:
    print(f"Error reading JSON file: {e}")
    exit()

# Print the JSON structure for debugging
print("JSON data structure:")
print(json.dumps(data, indent=4))

# Extract edges from the JSON data
if 'edges' in data:
    edges = data['edges']
else:
    print("No 'edges' key found in the JSON data")
    exit()

# Ensure edges is a list of dictionaries
if not isinstance(edges, list):
    print("Edges data is not a list")
    exit()
for edge in edges:
    if not isinstance(edge, dict):
        print(f"Edge is not a dictionary: {edge}")
        exit()

# Define CSV file name
csv_file_path = r'C:\Users\lolic\githubs\JingSpringThing\webxr-graph\processed_files;C\graph-data.csv'

# Write edges data to CSV file
try:
    with open(csv_file_path, 'w', newline='') as csvfile:
        fieldnames = ['source', 'target', 'weight']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for edge in edges:
            # Ensure the edge contains all necessary fields
            if 'source' in edge and 'target' in edge and 'weight' in edge:
                writer.writerow(edge)
            else:
                print(f"Edge missing required fields: {edge}")
except Exception as e:
    print(f"Error writing to CSV file: {e}")

print(f"Data has been successfully written to {csv_file_path}")
