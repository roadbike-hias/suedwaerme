import os
import json
import pandas as pd
from shapely.geometry import shape, Point

# Relative path to the folder containing the GeoJSON files
folder_path = os.path.join(os.path.dirname(__file__), "..", "gebieteCC")

# Load the CSV file
csv_file_path = "Stromerzeuger.csv"  # Replace with the path to your CSV file
df = pd.read_csv(csv_file_path, delimiter=";", decimal=",")

# Check the column names in the CSV file
print(df.columns)  # Ensure the column names match your CSV file

# Extract latitude and longitude columns
# Replace "Koordinate: Breitengrad (WGS84)" and "Koordinate: Längengrad (WGS84)" with the actual column names
latitude_column = "Koordinate: Breitengrad (WGS84)"
longitude_column = "Koordinate: Längengrad (WGS84)"

# Create a list of Shapely Point objects from the coordinates
points = []
for index, row in df.iterrows():
    lat = row[latitude_column]
    lon = row[longitude_column]
    point = Point(lon, lat)  # Shapely Point takes (longitude, latitude)
    points.append(point)

# Print the first few points to verify
for point in points[:5]:
    print(point)

# List to store all loaded GeoJSON features
all_features = []

# Iterate over all files in the folder
for filename in os.listdir(folder_path):
    if filename.endswith(".geojson"):
        file_path = os.path.join(folder_path, filename)

        # Load the GeoJSON file
        with open(file_path, "r") as f:
            geojson_data = json.load(f)

        # Extract features and add them to the list
        if geojson_data["type"] == "FeatureCollection":
            all_features.extend(geojson_data["features"])
        elif geojson_data["type"] == "Feature":
            all_features.append(geojson_data)

# Check if the point is inside any of the polygons
for point in points:
    for feature in all_features:
        polygon = shape(feature['geometry'])
        if polygon.contains(point):
            print(f"The point is inside a polygon from CC: {feature['properties']['CC']}")
            break
    else:
        print("The point is not inside any polygon.")