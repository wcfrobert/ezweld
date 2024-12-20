import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Create subplot with a 3D scene at (row=1, col=2)
fig = make_subplots(
    rows=1, 
    cols=2, 
    specs=[[None, {'type': 'scene'}]],  # Define the second column as 3D
    subplot_titles=("Left Placeholder", "3D Plot with Scatter3D and Cone")
)

# Add scatter3d points to (row=1, col=2)
scatter_points = go.Scatter3d(
    x=[1, 2, 3], 
    y=[2, 3, 4], 
    z=[3, 1, 2], 
    mode='markers',
    marker=dict(size=8, color='red', opacity=0.8)
)
fig.add_trace(scatter_points, row=1, col=2)

# Add cone to (row=1, col=2)
cone = go.Cone(
    x=[0], 
    y=[0], 
    z=[0], 
    u=[1], 
    v=[1], 
    w=[1], 
    sizemode='absolute', 
    sizeref=2, 
    colorscale='Blues',
    opacity=0.9
)
fig.add_trace(cone, row=1, col=2)

# Update layout to control axis ranges
fig.update_layout(
    scene2=dict(  # Scene2 corresponds to (row=1, col=2)
        xaxis_title='X Axis',
        yaxis_title='Y Axis',
        zaxis_title='Z Axis',
        xaxis_range=[-5, 5],
        yaxis_range=[-5, 5],
        zaxis_range=[-5, 5]
    ),
    title_text="3D Plot of Scatter3D and Cone in Subplot",
    showlegend=False
)

# Show the figure
fig.show()
