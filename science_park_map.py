import requests
import json

import matplotlib.pyplot as plt
import geopandas as gpd
from shapely.geometry import Point

# Define the bounding box specifically around your data points (South, West, North, East)
# This tightly hugs the Science Park & Oosterpark coordinates you provided.
bbox = "52.348,4.910,52.368,4.965"

# Overpass API query to fetch roads (highways) within that box
overpass_url = "http://overpass-api.de/api/interpreter"
overpass_query = f"""
[out:json];
(
  way["highway"]({bbox});
);
out geom;
"""

print("Fetching streets from OpenStreetMap Overpass API...")
response = requests.post(overpass_url, data={'data': overpass_query})
data = response.json()

# Convert OpenStreetMap JSON to standard GeoJSON format
geojson = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "geometry": {
                "type": "LineString",
                "coordinates": [[pt["lon"], pt["lat"]] for pt in element["geometry"]]
            },
            "properties": element.get("tags", {})
        }
        for element in data["elements"] if "geometry" in element
    ]
}

# Save it locally as a GeoJSON file
with open("amsterdam_streets.geojson", "w") as f:
    json.dump(geojson, f)

print("Success! 'amsterdam_streets.geojson' has been saved locally. You can go offline now!")

LOCATIONS = {
    "AUC Academic Building": (52.3553, 4.9512), 
    "UvA Science Park Library": (52.3544, 4.9557),
    "USC Universum Gym": (52.3558, 4.9561),
    "Amsterdam Science Park Station": (52.3530, 4.9485),
    "SPAR": (52.3547, 4.9503),
    "Albert Heijn": (52.3577, 4.9393),
    "Lidl": (52.3617, 4.9403),
    "Kruidvat": (52.3637, 4.939),
    "OBA Javaplein": (52.3643, 4.9388),
    "Studio/K": (52.3655, 4.9359),
    "Oosterpark": (52.3604, 4.9204),
    "Flevopark": (52.3590, 4.9482),
    "C&C Asian Market": (52.3639, 4.9275),
    "CREA/UvA Roeterseiland Campus": (52.3634, 4.9130),
    "Action": (52.3572, 4.9315),
    "Q-Factory": (52.3578, 4.9306),
    "Amsterdam Muiderpoort Station": (52.3611, 4.9306),
    "Wereldmuseum": (52.3631, 4.9224),
    "Dappermarkt": (52.3627, 4.9279),
    "Flevoparkbad": (52.3649, 4.9531)
}

# 1. Load the local offline street layer
# If you didn't run Step 1, this will look for the file in your notebook directory
streets_gdf = gpd.read_file("amsterdam_streets.geojson")

# 2. Build your points dataframe
names = list(LOCATIONS.keys())
geometry = [Point(coords[1], coords[0]) for coords in LOCATIONS.values()]
points_gdf = gpd.GeoDataFrame(geometry=geometry, crs="EPSG:4326")
points_gdf['Name'] = names

# 3. Setup the Matplotlib plot layout
fig, ax = plt.subplots(figsize=(16, 12), facecolor='#f5f5f2')
ax.set_facecolor('#f5f5f2')

# 4. Draw the offline street lines first (as the background)
streets_gdf.plot(ax=ax, color='#d0d0d0', linewidth=0.8, alpha=0.7, zorder=1)

# 5. Overlay your specific red coordinate location pins
points_gdf.plot(ax=ax, color='#e63946', markersize=60, zorder=3, edgecolor='black', linewidth=0.5)

# 6. Annotate names onto the map using a clean layout
for idx, row in points_gdf.iterrows():
    lon = row['geometry'].x
    lat = row['geometry'].y
    
    ax.annotate(
        text=row['Name'], 
        xy=(lon, lat),
        xytext=(6, 3), 
        textcoords="offset points", 
        fontsize=8,
        fontweight='bold',
        color='#1d3557',
        bbox=dict(boxstyle="round,pad=0.2", fc="#ffffff", ec="#b0b0b0", lw=0.6, alpha=0.9),
        zorder=4
    )

# Clean up axes and titles
ax.set_title("Amsterdam Science Park & Environs (100% Offline Mode)", fontsize=16, fontweight='bold', color='#1d3557', pad=15)
ax.axis('off') # Hides the latitude/longitude numbers for a cleaner layout

# Set map limits to frame only where your points exist
ax.set_xlim(4.910, 4.965)
ax.set_ylim(52.348, 52.368)

plt.tight_layout()
plt.show()