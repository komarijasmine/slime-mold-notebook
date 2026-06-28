import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from shapely.geometry import LineString, Point

def solve_pressures(num_nodes, link_is, link_js, lengths, D, source_node, sink_node, I0=1.0):
    """
    Solve pressure values at all nodes.

    source_node gets +I0.
    sink_node gets -I0.
    All other nodes get 0.
    """

    conductance = D / lengths

    rows = []
    cols = []
    data = []

    # Build graph Laplacian matrix
    for i, j, g in zip(link_is, link_js, conductance):
        # diagonal terms
        rows.extend([i, j])
        cols.extend([i, j])
        data.extend([g, g])

        # off-diagonal terms
        rows.extend([i, j])
        cols.extend([j, i])
        data.extend([-g, -g])

    L = coo_matrix(
        (data, (rows, cols)),
        shape=(num_nodes, num_nodes)
    ).tocsr()

    b = np.zeros(num_nodes)
    b[source_node] = I0
    b[sink_node] = -I0

    # The pressure system is singular unless we fix one node pressure.
    # We remove node 0 and set its pressure to 0.
    fixed_node = 0

    keep = np.arange(num_nodes) != fixed_node

    L_reduced = L[keep][:, keep]
    b_reduced = b[keep]

    p = np.zeros(num_nodes)
    p[keep] = spsolve(L_reduced, b_reduced)

    return p


def compute_flux(link_is, link_js, lengths, D, pressures):
    p_i = pressures[link_is]
    p_j = pressures[link_js]

    Q = (D / lengths) * (p_i - p_j)

    return Q


def update_conductivity(D, Q, dt=0.1, gamma=1.0, D_min=1e-4):
    D_new = D + dt * (np.abs(Q) ** gamma - D)

    # Prevent conductivities from becoming zero or negative
    D_new = np.maximum(D_new, D_min)

    return D_new


def conductivity_to_linewidths(D, min_width=0.05, max_width=3.0):
    """
    Convert conductivity values into line widths for plotting.
    """

    D = np.asarray(D, dtype=float)
    D = np.maximum(D, 0)

    values = np.log1p(D)

    lo = np.percentile(values, 5)
    hi = np.percentile(values, 99)

    if hi == lo:
        return np.full_like(values, (min_width + max_width) / 2)

    values = np.clip(values, lo, hi)

    widths = min_width + (values - lo) / (hi - lo) * (max_width - min_width)

    return widths


def get_bounds_from_segments_and_points(edge_segments, food_coords):
    """
    Get plot bounds from edge segments and food coordinates.
    """

    segment_points = np.vstack([
        np.asarray(segment)
        for segment in edge_segments
    ])

    food_coords = np.asarray(food_coords)

    all_points = np.vstack([
        segment_points,
        food_coords,
    ])

    minx = all_points[:, 0].min()
    miny = all_points[:, 1].min()
    maxx = all_points[:, 0].max()
    maxy = all_points[:, 1].max()

    return minx, miny, maxx, maxy


def plot_conductivity_snapshots(
    edge_segments,
    food_coords,
    snapshots,
    output_path=None,
    show=True,
    padding=5000,
):
    """
    Make one vertical figure with all conductivity snapshots.

    Parameters
    ----------
    edge_segments:
        List or array of edge coordinate sequences.

        Example:
            [
                [(x1, y1), (x2, y2)],
                [(x3, y3), (x4, y4)],
            ]

    food_coords:
        List or array of food node coordinates.

        Example:
            [
                [x1, y1],
                [x2, y2],
            ]

    snapshots:
        List of dictionaries.

        Each snapshot should look like:
            {
                "step": 0,
                "conductivity": D
            }

        D must have one conductivity value per edge segment.

    output_path:
        Optional path to save the figure.

    show:
        If True, display the plot under a Jupyter notebook cell.
    """

    n_plots = len(snapshots)

    if n_plots == 0:
        print("No snapshots to plot.")
        return

    edge_segments = [
        np.asarray(segment)
        for segment in edge_segments
    ]

    food_coords = np.asarray(food_coords)

    if food_coords.ndim != 2 or food_coords.shape[1] != 2:
        raise ValueError("food_coords must have shape (number_of_food_nodes, 2).")

    fig, axes = plt.subplots(
        n_plots,
        1,
        figsize=(8, 8 * n_plots),
        sharex=True,
        sharey=True,
    )

    if n_plots == 1:
        axes = [axes]

    minx, miny, maxx, maxy = get_bounds_from_segments_and_points(
        edge_segments=edge_segments,
        food_coords=food_coords,
    )

    for ax, snapshot in zip(axes, snapshots):
        t = snapshot["step"]
        D = np.asarray(snapshot["conductivity"])

        if len(D) != len(edge_segments):
            raise ValueError(
                "The conductivity array must have one value per edge segment."
            )

        widths = conductivity_to_linewidths(
            D,
            min_width=0.05,
            max_width=3.0,
        )

        edge_collection = LineCollection(
            edge_segments,
            linewidths=widths,
            alpha=0.8,
        )

        ax.add_collection(edge_collection)

        ax.scatter(
            food_coords[:, 0],
            food_coords[:, 1],
            s=15,
        )

        ax.set_title(f"Step {t}")
        ax.set_xlim(minx - padding, maxx + padding)
        ax.set_ylim(miny - padding, maxy + padding)
        ax.set_aspect("equal")
        ax.set_axis_off()

    plt.tight_layout()

    if output_path is not None:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_path, dpi=300, bbox_inches="tight")
        print(f"Saved conductivity snapshot figure to {output_path}")

    if show:
        plt.show()

    plt.close(fig)