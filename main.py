import ezweld


# initialize a weld group
weld_group = ezweld.weldgroup.WeldGroup()

# draw welds
# weld_group.add_line(start=[0,0], end=[0,10], segments=100)
# weld_group.add_line(start=[0,0], end=[10,10], segments=10)
# weld_group.add_line(start=[10,0], end=[10,10], segments=100)
# weld_group.add_rectangle(xo=0, yo=14, width=10, height=5, xsegments=10, ysegments=5)
weld_group.add_circle(xo=5, yo=-8, diameter=8, segments=100, thickness=5/16)

# preview geometry
weld_group.preview()

# weld group properties
print(f"area: {weld_group.A:.1f} in^2")
print(f"x_cg: {weld_group.x_centroid:.1f} in")
print(f"y_cg: {weld_group.y_centroid:.1f} in")

print(f"Ix: {weld_group.Ix:.1f} in^4")
print(f"Iy: {weld_group.Iy:.1f} in^4")
print(f"Ixy: {weld_group.Ixy:.1f} in^4")
print(f"Iz: {weld_group.Iz:.1f} in^4")

print(f"Sx1: {weld_group.Sx1:.1f} in^3")
print(f"Sx2: {weld_group.Sx2:.1f} in^3")
print(f"Sy1: {weld_group.Sy1:.1f} in^3")
print(f"Sy2: {weld_group.Sy2:.1f} in^3")


# calculate stresses with elastic method
# results = weld_group.solve(Vx=0,
#                            Vy=0,
#                            tension=0,
#                            Mx=0,
#                            My=0,
#                            torsion=0)

# plot weld stress
#weld_group.plot_results(weld_group)



