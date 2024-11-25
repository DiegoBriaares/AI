import networkx as nx
import numpy as np
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output, State

# Create a directed graph for a given layer and edge rule
def create_graph_layer(num_nodes, edge_rule="add"):
    G = nx.DiGraph()
    G.add_nodes_from(range(num_nodes))  # Include 0 as a node

    for i in range(num_nodes):
        if edge_rule == "add":
            j = i + (i & -i)
        elif edge_rule == "subtract":
            j = i - (i & -i)
        else:
            raise ValueError("Invalid edge_rule. Choose 'add' or 'subtract'.")
        
        if 0 <= j < num_nodes:
            G.add_edge(i, j)

    return G

# Calculate 3D positions for nodes in a layer
def calculate_3d_positions(G, layer_number, layer_separation=10):
    positions = {}
    radius = layer_number
    z = layer_number * layer_separation
    for i in G.nodes():
        angle = 2 * np.pi * i / len(G.nodes())
        x = radius * np.cos(angle)
        y = radius * np.sin(angle)
        positions[i] = (x, y, z)

    return positions

# Create a 3D visualization for layers
def visualize_layers(selected_layer, edge_rule="add", lower=4, upper=32):
    all_nodes = []
    all_edges = []

    # Determine layer sizes based on user inputs
    layers = []
    current_nodes = lower + 1  # Account for vertex 0
    while current_nodes <= upper + 1:
        layers.append((len(layers) + 1, current_nodes))
        current_nodes = 2 * (current_nodes - 1) + 1  # Ensure 2^n + 1 structure

    selected_layers = [layers[selected_layer - 1]] if selected_layer != 0 else layers

    for layer_num, num_nodes in selected_layers:
        G = create_graph_layer(num_nodes, edge_rule)
        positions = calculate_3d_positions(G, layer_num)

        # Add nodes
        for node, pos in positions.items():
            all_nodes.append(go.Scatter3d(
                x=[pos[0]], y=[pos[1]], z=[pos[2]],
                mode='markers+text',
                marker=dict(size=5),
                text=str(node),
                textfont=dict(size=10),  # Smaller font size
                textposition='top center',
                name=f'Layer {layer_num}'
            ))

        # Add edges
        for edge in G.edges():
            start_pos, end_pos = positions[edge[0]], positions[edge[1]]
            all_edges.append(go.Scatter3d(
                x=[start_pos[0], end_pos[0], None],
                y=[start_pos[1], end_pos[1], None],
                z=[start_pos[2], end_pos[2], None],
                mode='lines',
                line=dict(width=2),
                name=f'Layer {layer_num}'
            ))

    # Combine nodes and edges
    fig = go.Figure(data=all_nodes + all_edges)

    # Customize layout
    fig.update_layout(
        title=f'Visualization of Layers {"All" if selected_layer == 0 else selected_layer} with {edge_rule} edge rule',
        scene=dict(
            xaxis=dict(showbackground=False),
            yaxis=dict(showbackground=False),
            zaxis=dict(showbackground=False)
        ),
        showlegend=False
    )
    return fig

# Dash App
app = Dash(__name__)

app.layout = html.Div([
    html.H1("Interactive Graph Visualization", style={'textAlign': 'center'}),
    html.Div([
        html.Label("Lower Bound (Min Nodes):"),
        dcc.Input(id='lower-bound', type='number', value=4, min=1),
        html.Label("Upper Bound (Max Nodes):"),
        dcc.Input(id='upper-bound', type='number', value=32, min=1),
        html.Button('Update Layers', id='update-button', n_clicks=0)
    ], style={'marginBottom': '20px'}),
    html.Div([
        html.Label("Select Layer:"),
        dcc.Dropdown(
            id='layer-selector',
            options=[
                {'label': 'All Layers', 'value': 0},
                {'label': 'Layer 1', 'value': 1},
                {'label': 'Layer 2', 'value': 2},
                {'label': 'Layer 3', 'value': 3},
                {'label': 'Layer 4', 'value': 4},
            ],
            value=0,
            clearable=False
        ),
        html.Label("Edge Rule:"),
        dcc.RadioItems(
            id='edge-rule-selector',
            options=[
                {'label': 'Add (j = i + (i & -i))', 'value': 'add'},
                {'label': 'Subtract (j = i - (i & -i))', 'value': 'subtract'},
            ],
            value='add',
            inline=True
        )
    ], style={'marginBottom': '20px'}),
    dcc.Graph(id='graph-visualization')
])

@app.callback(
    [Output('graph-visualization', 'figure'),
     Output('layer-selector', 'options')],
    [Input('update-button', 'n_clicks')],
    [State('lower-bound', 'value'),
     State('upper-bound', 'value'),
     State('layer-selector', 'value'),
     State('edge-rule-selector', 'value')]
)
def update_graph(n_clicks, lower, upper, selected_layer, edge_rule):
    lower = max(1, lower)  # Ensure minimum 1 node
    upper = max(lower, upper)  # Ensure upper >= lower
    fig = visualize_layers(selected_layer, edge_rule, lower, upper)

    # Dynamically update dropdown options for layers
    options = [{'label': 'All Layers', 'value': 0}]
    current_nodes = lower + 1
    layer_num = 1
    while current_nodes <= upper + 1:
        options.append({'label': f'Layer {layer_num} ({current_nodes} nodes)', 'value': layer_num})
        current_nodes = 2 * (current_nodes - 1) + 1
        layer_num += 1

    return fig, options

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
