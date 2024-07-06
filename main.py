"""
TODO LIST:
    - implement plotly result plot with colormap
    - create function to add arrows to a plotly figure
    - implement cone and arrow to show stress vector
    - write docstring for methods
    - write docstrings for class
"""
import ezweld
import numpy as np

# initialize a weld group
weld_group = ezweld.WeldGroup()

# draw welds
weld_group.add_line(start=[0,0], end=[0,10], segments=15, thickness=10/16)
weld_group.add_line(start=[5,0], end=[5,10], segments=15, thickness=5/16)
weld_group.add_line(start=[10,0], end=[10,10], segments=15, thickness=5/16)

#weld_group.add_line(start=[0,0], end=[10,10], segments=10, thickness=5/16)
#weld_group.add_rectangle(xo=0, yo=14, width=10, height=5, xsegments=10, ysegments=5)
#weld_group.add_circle(xo=5, yo=-8, diameter=8, segments=100, thickness=5/16)
#weld_group.rotate(10.79)

# preview geometry
weld_group.preview()

# calculate stresses with elastic method
results = weld_group.solve(Vx=100,Vy=100,tension=100,Mx=100,My=100,torsion=100)

# print(np.array(results["vx_direct"]/results["thickness"]) - np.array(results["tauX_direct"]))
# print(np.array(results["vy_direct"]/results["thickness"]) - np.array(results["tauY_direct"]))
# print(np.array(results["vz_direct"]/results["thickness"]) - np.array(results["tauZ_direct"]))

# plot weld stress
#weld_group.plot_results(weld_group)



