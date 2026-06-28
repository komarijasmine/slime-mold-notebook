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


def make_edge_segments(edges_gdf):
    """
    Convert edge LineString geometries into coordinate arrays for LineCollection.
    """

    segments = []

    for geom in edges_gdf.geometry:
        segments.append(np.asarray(geom.coords))

    return segments


def plot_conductivity_snapshots(
    edges_gdf,
    food_nodes_gdf,
    snapshots,
    output_path=None,
    show=True,
):
    """
    Make one vertical figure with all conductivity snapshots.

    If show=True, display the figure under a Jupyter notebook code cell.

    If output_path is given, save the figure.
    If output_path is None, only display it.
    """

    n_plots = len(snapshots)

    if n_plots == 0:
        print("No snapshots to plot.")
        return

    segments = make_edge_segments(edges_gdf)

    fig, axes = plt.subplots(
        n_plots,
        1,
        figsize=(8, 8 * n_plots),
        sharex=True,
        sharey=True,
    )

    if n_plots == 1:
        axes = [axes]

    minx, miny, maxx, maxy = edges_gdf.total_bounds
    padding = 5000

    for ax, snapshot in zip(axes, snapshots):
        t = snapshot["step"]
        D = snapshot["conductivity"]

        widths = conductivity_to_linewidths(
            D,
            min_width=0.05,
            max_width=3.0,
        )

        edge_collection = LineCollection(
            segments,
            linewidths=widths,
            alpha=0.8,
        )

        ax.add_collection(edge_collection)

        food_nodes_gdf.plot(
            ax=ax,
            markersize=15,
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

def run_simulation(coords,
                   micro_links,
                   n_steps=1000,
                   seed=0,
                   t_btwn_snapshots=100,
                   I0=1.0,
                   gamma=1.0):
    
    rng = np.random.default_rng(seed)

    num_links = len(micro_links)
    num_nodes = len(coords)

    link_is = micro_links["node_i"].to_numpy(dtype=int)
    link_js = micro_links["node_j"].to_numpy(dtype=int)
    lengths = micro_links["length_m"].to_numpy(dtype=float)

    # make array for keeping track of conductivities
    D = np.ones(num_links)

    snapshots = [{"step": 0,
                "conductivity": D.copy(),
                }]
    
    node_indices = range(len(coords))
    
    for t in range(n_steps):
        # choose source and sink node indices randomly
        source_node, sink_node = rng.choice(
            node_indices,
            size=2,
            replace=False,
        )

        # create array of pressures corresponding to ...
        pressures = solve_pressures(
            num_nodes=num_nodes,
            link_is=link_is,
            link_js=link_js,
            lengths=lengths,
            D=D,
            source_node=source_node,
            sink_node=sink_node,
            I0=I0,
        )

        Q = compute_flux(
            link_is=link_is,
            link_js=link_js,
            lengths=lengths,
            D=D,
            pressures=pressures,
        )

        D = update_conductivity(
            D=D,
            Q=Q,
            dt=0.1,
            gamma=gamma,
            D_min=1e-4,
        )

        if t % t_btwn_snapshots == 0:
            print(
                "step",
                t,
                "source",
                source_node,
                "sink",
                sink_node,
                "D min/max",
                D.min(),
                D.max(),
            )

        snapshots.append({
                "step": t,
                "conductivity": D.copy(),
            })
        
        plot_conductivity_snapshots(
        edges_gdf=edges_gdf,
        food_nodes_gdf=food_nodes_gdf,
        snapshots=snapshots,
        output_path=output_path,
        )
    
    return