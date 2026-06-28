import contextily as cx
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
from scipy.spatial import cKDTree
from shapely.geometry import LineString, Point

from make_mesh import edges_from_knn, jittered_hex_grid_points
from science_park_map import location_coords, location_names, bounds, gdf

'''
# calculating bounds in meters for buffer
minx, miny, maxx, maxy = gdf.total_bounds
buffer = 200 
meter_bounds = (minx - buffer, miny - buffer, maxx + buffer, maxy + buffer)
'''
'''
# generate mesh 
mesh_points = jittered_hex_grid_points(meter_bounds, spacing=100, jitter=0.2)
mesh_edges = edges_from_knn(mesh_points, k=6)
'''

def plot_mesh(coords, micro_links):
    # convert edges into gdf
    edge_lines = [LineString([coords[s], coords[e]]) for s, e in micro_links]
    edges_gdf = gpd.GeoDataFrame(geometry=edge_lines, crs="EPSG:3857")

    point_objects = [Point(xy) for xy in coords]
    points_gdf = gpd.GeoDataFrame(geometry=point_objects, crs="EPSG:3857")

    # plotting 
    fig, ax = plt.subplots(figsize=(13, 11))

    edges_gdf.plot(ax=ax, color="#2b5c8f", linewidth=1.2, alpha=0.4, zorder=2)
    points_gdf.plot(ax=ax, color="#2b5c8f", markersize=8, alpha=0.6, zorder=3)
    gdf.plot(ax=ax, color="red", markersize=50, edgecolor="white", linewidth=1, zorder=4)

    for idx, row in gdf.iterrows():
        ax.text(
            row["geometry"].x + 40,
            row["geometry"].y + 15,
            row["name"],
            fontsize=8,
            fontweight="bold",
            color="black",
            bbox=dict(facecolor="white", alpha=0.8, edgecolor="gray", boxstyle="round,pad=0.2"),
            zorder=5,
        )

    ax.set_xlim(bounds[0], bounds[2])
    ax.set_ylim(bounds[1], bounds[3])

    cx.add_basemap(ax, source=cx.providers.OpenStreetMap.Mapnik, crs="EPSG:3857", zorder=1)

    ax.set_axis_off()
    plt.show()