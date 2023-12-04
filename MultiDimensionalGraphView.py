import networkx as nx
import numpy as np
import plotly.graph_objects as go

def create_graph_layer(num_nodes):
    G = nx.DiGraph()
    G.add_nodes_from(range(1, num_nodes + 1))

    for i in range(1, num_nodes + 1):
        j = i + (i & -i)
        if j <= num_nodes:
            G.add_edge(i, j)

    return G

def calculate_3d_positions(G, layer_number):
    positions = {}
    radius = layer_number
    for i in G.nodes():
        angle = 2 * np.pi * i / len(G.nodes())
        x = radius * np.cos(angle)
        y = radius * np.sin(angle)
        z = layer_number
        positions[i] = (x, y, z)

    return positions

all_nodes = []
all_edges = []

for layer_num, num_nodes in enumerate([1, 2, 4, 8, 16, 32, 64, 128, 256], start=1):
    G = create_graph_layer(num_nodes)
    positions = calculate_3d_positions(G, layer_num)

    for node, pos in positions.items():
        all_nodes.append(go.Scatter3d(x=[pos[0]], y=[pos[1]], z=[pos[2]],
                                      mode='markers', marker=dict(size=2),
                                      text=str(node), name=f'Layer {layer_num}'))

    for edge in G.edges():
        start_pos, end_pos = positions[edge[0]], positions[edge[1]]
        all_edges.append(go.Scatter3d(x=[start_pos[0], end_pos[0]],
                                      y=[start_pos[1], end_pos[1]],
                                      z=[start_pos[2], end_pos[2]],
                                      mode='lines', line=dict(width=1),
                                      name=f'Layer {layer_num}'))

fig = go.Figure(data=all_nodes + all_edges)
fig.update_layout(title='Multi-Dimensional Graph Visualization',
                  scene=dict(xaxis=dict(showbackground=False),
                             yaxis=dict(showbackground=False),
                             zaxis=dict(showbackground=False)),
                  showlegend=False)
fig.show()
