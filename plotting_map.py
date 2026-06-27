import osmnx as ox
import matplotlib.pyplot as plt

# 1. Download the street network directly from OSM using a central point and a radius
# This creates a graph of the streets surrounding your data points
center_point = (52.3590, 4.9380) # Centered near East Amsterdam / Science Park
graph = ox.graph_from_point(center_point, dist=2500, network_type='all')

# 2. Convert the graph into GeoDataFrames (one for streets/edges, one for intersections/nodes)
nodes_gdf, streets_gdf = ox.graph_to_gdfs(graph)

# Now 'streets_gdf' is a standard GeoDataFrame you can inspect or plot!
print(type(streets_gdf))
print(streets_gdf.head(2))

# Quick interactive plot using osmnx's built-in feature:
ox.plot_graph(graph, node_size=0, edge_color='#d0d0d0', edge_linewidth=0.8)