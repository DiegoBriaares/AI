import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

def draw_circular_graph(n):
    """
    Creates a directed circular graph with n vertices.
    Each vertex i (from 1 to n-1) is connected to vertex i - (i & -i).
    Vertex 0 is positioned at the center with no outgoing edges.
    """
    G = nx.DiGraph()
    positions = {}
    labels = {}
    
    # Add vertices and edges
    for i in range(n):
        G.add_node(i)
        labels[i] = i
        if i != 0:
            G.add_edge(i, i - (i & -i))
        angle = 2 * np.pi * i / n
        positions[i] = (np.cos(angle), np.sin(angle))
    
    return G, positions, labels

def draw_expanding_circular_graphs(start, end):
    """
    Draws a series of expanding circular graphs from 'start' vertices to 'end' vertices.
    Each subsequent circle doubles the number of vertices.
    """
    plt.figure(figsize=(15, 15))
    current_n = start

    # Starting from the innermost circle to the outermost
    while current_n <= end:
        G, pos, labels = draw_circular_graph(current_n)

        # Scale positions for outer circles
        scale_factor = current_n / start
        for k in pos:
            pos[k] = (scale_factor * pos[k][0], scale_factor * pos[k][1])

        nx.draw(G, pos, with_labels=True, labels=labels, node_size=1024, arrows=True)
        current_n *= 2

# Drawing graphs from 33 vertices to 1024 vertices
draw_expanding_circular_graphs(33, 256)
plt.show()
