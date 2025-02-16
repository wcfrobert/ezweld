import ezweld

# # Example 1
# example1 = ezweld.WeldGroup()
# example1.add_line(start=(0,0), end=(0,8), thickness=5/16)
# example1.add_line(start=(6,0), end=(6,8), thickness=5/16)
# results = example1.solve(Vx=0, Vy=-50, Vz=0, Mx=120, My=0, Mz=0)
# example1.plot_results()



# # Example 2
# example2 = ezweld.WeldGroup()
# example2.add_rectangle(xo=-2, yo=-3, width=4, height=6, thickness=5/16)
# results = example2.solve(Vx=0, Vy=0, Vz=0, Mx=240, My=120, Mz=0)
# example2.plot_results()



# # Example 3
# example3 = ezweld.WeldGroup()
# example3.add_line(start=(0,0), end=(3,0), thickness=5/16)
# example3.add_line(start=(0,10), end=(3,10), thickness=5/16)
# example3.add_line(start=(0,0), end=(0,10), thickness=5/16)
# results = example3.solve(Vx=0, Vy=-50, Vz=0, Mx=0, My=0, Mz=200)
# example3.plot_results()



# Example 4
example4 = ezweld.WeldGroup()
example4.add_circle(xo=0, yo=0, diameter=12, thickness=5/16)
results = example4.solve(Vx=0, Vy=-50, Vz=0, Mx=120, My=0, Mz=0)
example4.plot_results()