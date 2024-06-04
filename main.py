import ezweld


# initialize a weld group
weld_group = ezweld.weldgroup.WeldGroup()

# add two vertical strips of weld
weld_group.add_strip(start=[0,0], end=[0,10])
weld_group.add_strip(start=[10,0], end=[10,10])

# preview geometry
#weld_group.preview(weld_group)

# calculate stresses with elastic method
# results = weld_group.solve(Vx=0,
#                            Vy=0,
#                            tension=0,
#                            Mx=0,
#                            My=0,
#                            torsion=0)

# plot weld stress
#weld_group.plot_results(weld_group)



