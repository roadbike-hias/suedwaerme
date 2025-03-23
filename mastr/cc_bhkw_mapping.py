import os
import json
from shapely.geometry import shape, Point

# Relative path to the folder containing the GeoJSON files
# Assuming the folder is named "geojson_files" and is in the parent directory
folder_path = os.path.join(os.path.dirname(__file__), "..", "gebieteCC")

# Example coordinate (replace with your actual coordinate)
latitude = 48.83523710565451
longitude = 10.082093268238632
point = Point(longitude, latitude)

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
for feature in all_features:
    polygon = shape(feature['geometry'])
    if polygon.contains(point):
        print(f"The point is inside a polygon from CC: {feature['properties']['CC']}")
        break
else:
    print("The point is not inside any polygon.")