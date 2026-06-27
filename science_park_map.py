import contextily as cx
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Point

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
    "Flevoparkbad": (52.3649, 4.9531),
}

location_names = ["AUC Academic Building", "UvA Science Park Library", "USC Universum Gym", "Amsterdam Science Park Station", "SPAR",
   "Albert Heijn", "Lidl", "Kruidvat", "OBA Javaplein", "Studio/K", "Oosterpark", "Flevopark", "C&C Asian Market", "CREA/UvA Roeterseiland Campus",
   "Action", "Q-Factory", "Amsterdam Muiderpoort Station", "Wereldmuseum", "Dappermarkt", "Flevoparkbad"]

location_coords = [(52.3553, 4.9512), (52.3544, 4.9557), (52.3558, 4.9561), (52.3530, 4.9485), (52.3547, 4.9503), (52.3577, 4.9393), (52.3617, 4.9403),
(52.3637, 4.939), (52.3643, 4.9388), (52.3655, 4.9359), (52.3604, 4.9204), (52.3590, 4.9482), (52.3639, 4.9275), (52.3634, 4.9130), (52.3572, 4.9315),
(52.3578, 4.9306), (52.3611, 4.9306), (52.3631, 4.9224), (52.3627, 4.9279), (52.3649, 4.9531)]

bounds = (52.35, 4.91, 52.37, 4.96)


# 1. Convert your dictionary into lists for GeoDataFrame
names = list(LOCATIONS.keys())
# Note: Shapely Points use (longitude, latitude) order
geometry = [Point(lon, lat) for lat, lon in LOCATIONS.values()]

# 2. Create the GeoDataFrame (using standard GPS coordinates EPSG:4326)
gdf = gpd.GeoDataFrame({"name": names, "geometry": geometry}, crs="EPSG:4326")

# 3. Web maps use Web Mercator (EPSG:3857). We must reproject it so the basemap fits perfectly
gdf = gdf.to_crs(epsg=3857)

# 4. Set up the Matplotlib plot
fig, ax = plt.subplots(figsize=(12, 10))

# Plot the coordinates as red dots
gdf.plot(ax=ax, color="red", markersize=40, zorder=2)

# 5. Add text labels over the image next to the dots
for idx, row in gdf.iterrows():
    # Offset text slightly so it doesn't overlap the dot
    ax.text(
        row["geometry"].x + 60,
        row["geometry"].y + 20,
        row["name"],
        fontsize=8,
        fontweight="bold",
        color="black",
        bbox=dict(
            facecolor="white", alpha=0.7, edgecolor="gray", boxstyle="round,pad=0.2"
        ),
        zorder=3,
    )

# 6. Fetch the background image tiles and download them seamlessly
# You can change the provider to cx.providers.CartoDB.Positron for a light map
cx.add_basemap(ax, source=cx.providers.OpenStreetMap.Mapnik, zorder=1)

# Clean up axes so it looks like a clean, professional image
ax.set_axis_off()

# 7. Save directly to a local image file
output_image = "science_park_geopandas.png"
plt.savefig(output_image, bbox_inches="tight", dpi=200)
plt.close()

print(f"Static map image saved successfully to {output_image}!")