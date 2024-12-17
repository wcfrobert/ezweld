import ezweld

# initialize a weld group
weld_group = ezweld.WeldGroup()

# draw welds
# weld_group.add_line(start=(0,0), end=(0,10), thickness=5/16)
# weld_group.add_line(start=(5,0), end=(5,10), thickness=5/16)
# weld_group.add_line(start=(10,0), end=(10,10), thickness=5/16)
# weld_group.add_line(start=(0,0), end=(10,10), thickness=5/16)
weld_group.add_rectangle(xo=0, yo=14, width=10, height=5, thickness=5/16)
# weld_group.add_circle(xo=5, yo=-8, diameter=8, thickness=5/16)
# weld_group.rotate(angle=0.88)

# preview geometry
#weld_group.preview()

# calculate stresses with elastic method
results = weld_group.solve(Vx=0, Vy=100, tension=0, Mx=50, My=50, torsion=0)

# plot results
#weld_group.plot_results()
fig = weld_group.plot_results_3D()
fig.show()
