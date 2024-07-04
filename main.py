"""
TODO LIST:
    - warn user about weld group rotation
    - modify preview() to show weld group geometric properties
    - implement solution method to all applied forces
    - implement plotly result plot with colormap
    - create function to add arrows to a plotly figure
    - implement cone and arrow to show stress vector
    - figure out signs
    - write docstring for methods
    - write docstrings for class
"""
import ezweld


# initialize a weld group
weld_group = ezweld.weldgroup.WeldGroup()

# draw welds
weld_group.add_line(start=[0,0], end=[0,10], segments=10)
weld_group.add_line(start=[10,0], end=[10,10], segments=10)
weld_group.add_line(start=[0,0], end=[10,10], segments=10)
# weld_group.add_rectangle(xo=0, yo=14, width=10, height=5, xsegments=10, ysegments=5)
# weld_group.add_circle(xo=5, yo=-8, diameter=8, segments=100)

#weld_group.rotate(-17.43)

# preview geometry
weld_group.preview()

weld_group.print_properties()


# calculate stresses with elastic method
# results = weld_group.solve(Vx=0,
#                            Vy=0,
#                            tension=0,
#                            Mx=0,
#                            My=0,
#                            torsion=0)

# plot weld stress
#weld_group.plot_results(weld_group)



