import contextily as cx
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import LineString, Point

from make_mesh import edges_from_knn, jittered_hex_grid_points
from science_park_map import location_coords, location_names, gdf, bounds

def plot_mesh(coords, micro_links):
    # convert edges into gdf
    edge_lines = [LineString([coords[s], coords[e]]) for s, e in micro_links]
    edges_gdf = gpd.GeoDataFrame(geometry=edge_lines, crs="EPSG:4326")

    point_objects = [Point(xy) for xy in coords]
    points_gdf = gpd.GeoDataFrame(geometry=point_objects, crs="EPSG:4326")
    gdf_4326 = gdf.to_crs(epsg=4326) if gdf.crs != "EPSG:4326" else gdf


    edges_3857  = edges_gdf.to_crs(epsg=3857)
    points_3857 = points_gdf.to_crs(epsg=3857)
    gdf_3857    = gdf_4326.to_crs(epsg=3857)

    # plotting 
    fig, ax = plt.subplots(figsize=(13, 11))

    edges_3857.plot(ax=ax, color="#2b5c8f", linewidth=1.2, alpha=0.4, zorder=2)
    points_3857.plot(ax=ax, color="#2b5c8f", markersize=8, alpha=0.6, zorder=3)
    gdf_3857.plot(ax=ax, color="red", markersize=50, edgecolor="white", linewidth=1, zorder=4)

    for idx, row in gdf.iterrows():
        ax.text(
            row["geometry"].x + 0.0004,
            row["geometry"].y + 0.0001,
            row["name"],
            fontsize=8,
            fontweight="bold",
            color="black",
            bbox=dict(facecolor="white", alpha=0.8, edgecolor="gray", boxstyle="round,pad=0.2"),
            zorder=5,
        )

    cx.add_basemap(ax, source=cx.providers.OpenStreetMap.Mapnik, zorder=1)

    ax.set_axis_off()
    plt.show()