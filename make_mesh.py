from shapely.geometry import LineString, Point
from shapely.prepared import prep
import geopandas as gpd
import numpy as np
from scipy.spatial import cKDTree

def jittered_hex_grid_points(
    bounds,
    spacing=3000,
    jitter=0.25,
    seed=0
):
    """
    Generate points in a hexagonal/staggered grid pattern.

    Only keep points inside the allowed area.
    """

    rng = np.random.default_rng(seed)

    minx, miny, maxx, maxy = bounds

    row_spacing = spacing * np.sqrt(3) / 2

    points = []

    y = miny
    row = 0

    while y <= maxy:
        # Every other row is shifted half a spacing to the right
        x_offset = 0 if row % 2 == 0 else spacing / 2

        x = minx + x_offset

        while x <= maxx:
            jitter_x = rng.uniform(-jitter, jitter) * spacing
            jitter_y = rng.uniform(-jitter, jitter) * row_spacing

            candidate_x = x + jitter_x
            candidate_y = y + jitter_y

            candidate_point = Point(candidate_x, candidate_y)

            x += spacing

        y += row_spacing
        row += 1

    return np.array(points)


def edges_from_knn(coords, k=6):
    """
    For each coordinate, generate edges between it and its k nearest neighbors.

    Output:
        A set of tuples.
        Each tuple is a pair of node indices into coords.
    """

    tree = cKDTree(coords)

    # In case there are fewer points than k + 1
    query_k = min(k + 1, len(coords))

    # k+1 because the nearest neighbor of each point is itself
    distances, neighbors = tree.query(coords, k=query_k)

    edges = set()

    for i in range(len(coords)):
        # If query_k == 1, neighbors[i] is a single number, not a list
        if query_k == 1:
            continue

        for j in neighbors[i][1:]:
            edge = tuple(sorted((i, int(j))))
            edges.add(edge)

    return edges