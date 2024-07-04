import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import math


class WeldGroup:
    """
    WeldGroup object definition.
    
    Input Arguments:
        None               
        
    Attributes: 
        
    Public Methods:
        add_line()
        add_rectangle()
        add_circle()
        solve()
        preview()
        plot_results()
    """
    def __init__(self):
        # applied force
        self.Vx = None
        self.Vy = None
        self.tension = None
        self.Mx = None
        self.My = None
        self.torsion = None
        
        # centroid
        self.x_centroid = None
        self.y_centroid = None
        
        # section geometric properties
        self.A = None
        self.Ix = None
        self.Iy = None
        self.Iz = None
        self.Ixy = None
        self.theta_p = None
        self.Sx1 = None
        self.Sx2 = None
        self.Sy1 = None
        self.Sy2 = None
        
        # geometric properties (force per unit length)
        self.Lw_plf = None
        self.Lw_effective_plf = None
        self.Ix_plf = None
        self.Iy_plf = None
        self.Ixy_plf = None
        self.Iz_plf = None
        self.Sx1_plf = None
        self.Sx2_plf = None
        self.Sy1_plf = None
        self.Sy2_plf = None
        
        # dictionary storing discretization of weld group
        self.dict_welds = {"x_centroid":[],
                           "y_centroid":[],
                           "x_start":[],
                           "y_start":[],
                           "x_end":[],
                           "y_end":[],
                           "thickness":[],
                           "length":[],
                           "area":[]}
        self.df_welds = None
    
    
    def add_rectangle(self, xo, yo, width, height, xsegments, ysegments, thickness=None):
        """
        Add a rectangular weld group by specifying the bottom left corner + width and height
        """
        pt1 = [xo, yo]
        pt2 = [xo+width, yo]
        pt3 = [xo+width, yo+height]
        pt4 = [xo, yo+height]
        
        self.add_line(start=pt1, end=pt2, segments=xsegments, thickness=thickness)
        self.add_line(start=pt4, end=pt3, segments=xsegments, thickness=thickness)
        self.add_line(start=pt1, end=pt4, segments=ysegments, thickness=thickness)
        self.add_line(start=pt2, end=pt3, segments=ysegments, thickness=thickness)
            
        
    def add_circle(self, xo, yo, diameter, segments, thickness=None):
        """
        Add a circular weld group by specifying the center + a diameter
        """
        # handles exception where segment < 4
        if segments < 4:
            print("Warning: circular patch must have 4 segments or more!")
            segments = 4
        
        # divide into angle increments from 0 to 360
        theta_list = np.linspace(0,360,segments+1)
        theta_list = [x*math.pi/180 for x in theta_list]
        
        # get x and y coordinate with equation of circle
        x_list = [xo+diameter/2*math.cos(theta) for theta in theta_list]
        y_list = [yo+diameter/2*math.sin(theta) for theta in theta_list]
        
        # plot segments
        for i in range(len(x_list)-1):
            pt1 = [x_list[i], y_list[i]]
            pt2 = [x_list[i+1], y_list[i+1]]
            self.add_line(start=pt1, end=pt2, segments=1, thickness=thickness)
    
    
    def add_line(self, start, end, segments, thickness=None):
        """
        Add a weld strip to the weld group by specifying two points. 
        
        Arguments:
            start           list:: [x, y] coordinate of first point
            end             list:: [x, y] coordiante of the second point
            segments        int:: number of weld patches to draw along the line
            thickness       float:: size of the weld line. Effective throat thickness for PJPs and Leg thickness for fillet
            
        Return:
            None
        """
        # convert into numpy arrays
        start = np.array(start)
        end = np.array(end)
        position_vector = end-start
        
        # discretize into N segments (N+1 end points)
        alpha = np.linspace(0, 1, segments+1)
        x_ends = start[0] + alpha * position_vector[0]
        y_ends = start[1] + alpha * position_vector[1]
        x_center = [(x_ends[i] + x_ends[i+1]) / 2 for i in range(len(x_ends)-1)]
        y_center = [(y_ends[i] + y_ends[i+1]) / 2 for i in range(len(y_ends)-1)]
        
        # calculate lengths
        length_total = np.linalg.norm(position_vector)
        length_segments = length_total / (segments)
        
        # add to dictionary storing discretization
        self.dict_welds["x_centroid"] = self.dict_welds["x_centroid"] + list(x_center)
        self.dict_welds["y_centroid"] = self.dict_welds["y_centroid"] + list(y_center)
        self.dict_welds["x_start"] = self.dict_welds["x_start"] + list(x_ends[:-1])
        self.dict_welds["y_start"] = self.dict_welds["y_start"] + list(y_ends[:-1])
        self.dict_welds["x_end"] = self.dict_welds["x_end"] + list(x_ends[1:])
        self.dict_welds["y_end"] = self.dict_welds["y_end"] + list(y_ends[1:])
        self.dict_welds["thickness"] = self.dict_welds["thickness"] + [thickness] * segments
        self.dict_welds["length"] = self.dict_welds["length"] + [length_segments] * segments
        self.dict_welds["area"] = self.dict_welds["area"] + [thickness * length_segments] * segments
    
    
    def rotate(self, angle):
        """rotate all meshes by a user-specified angle in degrees"""
        # rotation matrix
        rotation_rad = angle * math.pi / 180
        T = np.array([
            [math.cos(rotation_rad), -math.sin(rotation_rad)],
            [math.sin(rotation_rad), math.cos(rotation_rad)]
            ])
        
        # apply to each patch
        x_centroid_new = []
        y_centroid_new = []
        x_start_new = []
        x_end_new = []
        y_start_new = []
        y_end_new = []
        for i in range(len(self.dict_welds["x_centroid"])):
            center = np.array([self.dict_welds["x_centroid"][i], self.dict_welds["y_centroid"][i]])
            start = np.array([self.dict_welds["x_start"][i], self.dict_welds["y_start"][i]])
            end = np.array([self.dict_welds["x_end"][i], self.dict_welds["y_end"][i]])
            
            center_r = T @ center
            start_r = T @ start
            end_r = T @ end
            
            x_centroid_new.append(center_r[0])
            y_centroid_new.append(center_r[1])
            x_start_new.append(start_r[0])
            x_end_new.append(end_r[0])
            y_start_new.append(start_r[1])
            y_end_new.append(end_r[1])
        
        # override coordinate information
        self.dict_welds["x_centroid"] = x_centroid_new
        self.dict_welds["y_centroid"] = y_centroid_new
        self.dict_welds["x_start"] = x_start_new
        self.dict_welds["y_start"] = y_start_new
        self.dict_welds["x_end"] = x_end_new
        self.dict_welds["y_end"] = y_end_new
        
        # re-calculate geometric properties
        self.update_geometric_properties()
    
    
    def update_geometric_properties(self):
        """
        calculate geometric properties of bolt group.
        """
        # calculate depths
        all_x = self.dict_welds["x_centroid"] + self.dict_welds["x_start"] + self.dict_welds["x_end"]
        all_y = self.dict_welds["y_centroid"] + self.dict_welds["y_start"] + self.dict_welds["y_end"]
        
        # calculate centroid using moment of area equation
        xA = sum([x*A for x,A in zip(self.dict_welds["x_centroid"],self.dict_welds["area"])])
        yA = sum([y*A for y,A in zip(self.dict_welds["y_centroid"],self.dict_welds["area"])])
        self.A = sum(self.dict_welds["area"])
        self.x_centroid = xA / self.A
        self.y_centroid = yA / self.A
        
        # moment of inertia
        self.Ix = sum([ A * (y - self.y_centroid)**2 for y,A in zip(self.dict_welds["y_centroid"],self.dict_welds["area"]) ])
        self.Iy = sum([ A * (x - self.x_centroid)**2 for x,A in zip(self.dict_welds["x_centroid"],self.dict_welds["area"]) ])
        self.Ixy = sum([ A * (y - self.y_centroid) * (x - self.x_centroid) for x,y,A in zip(self.dict_welds["x_centroid"],self.dict_welds["y_centroid"],self.dict_welds["area"]) ])
        self.Iz = self.Ix + self.Iy
        
        # section modulus
        self.Sx1 = self.Ix / abs(max(all_y) - self.y_centroid)
        self.Sx2 = self.Ix / abs(min(all_y) - self.y_centroid)
        self.Sy1 = self.Iy / abs(max(all_x) - self.x_centroid)
        self.Sy2 = self.Iy / abs(min(all_x) - self.x_centroid)
        
        # principal axes via Mohr's circle
        if self.Ix==self.Iy:
            self.theta_p = 0
        else:
            self.theta_p = (  math.atan((self.Ixy)/((self.Ix-self.Iy)/2)) / 2) * 180 / math.pi
            if abs(self.theta_p) > 0.1:
                print("WARNING: Weld group should be rotated to its principal orientation ", end="")
                print("before solving. Otherwise normal stress due to flexure will be incorrectly superimposed.")
                print(f"Please rotate the weld group by {self.theta_p:.2f} degrees by calling the .rotate() method")
                

        # now repeat the calculation above with one-dimension less.
        # modify length to account for variable thickness
        t_min = min(self.dict_welds["thickness"])
        modified_length = [t/t_min * L for t,L in zip(self.dict_welds["thickness"], self.dict_welds["length"])]
        
        # lengths
        self.Lw_plf = sum(self.dict_welds["length"])
        self.Lw_effective_plf = sum(modified_length)
        
        # moment of inertia
        self.Ix_plf = sum([ L * (y - self.y_centroid)**2 for y,L in zip(self.dict_welds["y_centroid"],modified_length) ])
        self.Iy_plf = sum([ L * (x - self.x_centroid)**2 for x,L in zip(self.dict_welds["x_centroid"],modified_length) ])
        self.Ixy_plf = sum([ L * (y - self.y_centroid) * (x - self.x_centroid) for x,y,L in zip(self.dict_welds["x_centroid"],self.dict_welds["y_centroid"],modified_length) ])
        self.Iz_plf = self.Ix_plf + self.Iy_plf
        
        # section modulus
        self.Sx1_plf = self.Ix_plf / abs(max(all_y) - self.y_centroid)
        self.Sx2_plf = self.Ix_plf / abs(min(all_y) - self.y_centroid)
        self.Sy1_plf = self.Iy_plf / abs(max(all_x) - self.x_centroid)
        self.Sy2_plf = self.Iy_plf / abs(min(all_x) - self.x_centroid)
        
        
        
    def solve(self, Vx=0, Vy=0, Mx=0, My=0, torsion=0, tension=0):
        pass
    
    
    def preview(self):
        """
        preview weld group defined by user.
        """
        DEFAULT_THICKNESS = 0.25
        
        # update geometric property in case it was not run previously
        self.update_geometric_properties()
        
        # normalize thickness
        t_min = min(self.dict_welds["thickness"])
        line_thicknesses = [t/t_min * DEFAULT_THICKNESS for t in self.dict_welds["thickness"]]
        
        # initialize figure
        fig, axs = plt.subplots(figsize=(8,8))
        
        # plot weld mesh with polygon patches
        for i in range(len(self.dict_welds["x_start"])):
            x0 = self.dict_welds["x_start"][i]
            x1 = self.dict_welds["x_end"][i]
            y0 = self.dict_welds["y_start"][i]
            y1 = self.dict_welds["y_end"][i]
            xc = self.dict_welds["x_centroid"][i]
            yc = self.dict_welds["y_centroid"][i]
            
            # calculate perpendicular direction vector to offset by thickness
            u = np.array([x1,y1]) - np.array([x0,y0])
            u_unit = u / np.linalg.norm(u)
            v_unit = np.array([u_unit[1], -u_unit[0]])
            
            # plot using polygon patches
            pt1 = np.array([x0, y0]) + v_unit * line_thicknesses[i]
            pt2 = np.array([x0, y0]) - v_unit * line_thicknesses[i]
            pt3 = np.array([x1, y1]) - v_unit * line_thicknesses[i]
            pt4 = np.array([x1, y1]) + v_unit * line_thicknesses[i]
            vertices = [pt1, pt2, pt3, pt4, pt1]
            axs.add_patch(patches.Polygon(np.array(vertices), closed=True, facecolor="steelblue",
                                          alpha=0.8, edgecolor="black", zorder=1, lw=0.5))
            # xlim and ylim do not adjust properly with only patches. plot the centroids as well but make them invisible
            axs.plot([xc],[yc],c="black",marker="o",markersize=2, alpha=0)
            
        # plot Cog
        axs.plot(self.x_centroid, self.y_centroid, marker="*",c="red",markersize=8,zorder=2,linestyle="none")
        axs.annotate("CoG",xy=(self.x_centroid, self.y_centroid), xycoords='data', color="red",
                     xytext=(5, -5), textcoords='offset points', fontsize=14, va="top", zorder=3)
        
        # # annotation for bolt group properties
        # information_text = "Ix: {} \n".format(self.Ix)
        # axs.annotate(information_text, (0.1,0.6), xycoords='axes fraction', fontsize=14, va="top", ha="left")
            
        # styling
        axs.set_aspect('equal', 'datalim')
        fig.suptitle("Weld Group Preview", fontweight="bold", fontsize=16)
        axs.set_axisbelow(True)
        plt.tight_layout()
        
    def print_properties(self):
        # weld group properties
        print("Geometric properties for computing stresses")
        print(f" \tarea: {self.A:.1f} in^2")
        print(f" \tx_cg: {self.x_centroid:.1f} in")
        print(f" \ty_cg: {self.y_centroid:.1f} in")

        print(f" \tIx: {self.Ix:.1f} in^4")
        print(f" \tIy: {self.Iy:.1f} in^4")
        print(f" \tIz: {self.Iz:.1f} in^4")
        print(f" \tIxy: {self.Ixy:.1f} in^4")

        print(f" \tSx1: {self.Sx1:.1f} in^3")
        print(f" \tSx2: {self.Sx2:.1f} in^3")
        print(f" \tSy1: {self.Sy1:.1f} in^3")
        print(f" \tSy2: {self.Sy2:.1f} in^3")
        
        print("Geometric properties for computing force/length")
        print(f" \tlength: {self.Lw_effective_plf:.1f} in")

        print(f" \tIx: {self.Ix_plf:.1f} in^3")
        print(f" \tIy: {self.Iy_plf:.1f} in^3")
        print(f" \tIz: {self.Iz_plf:.1f} in^3")
        print(f" \tIxy: {self.Ixy_plf:.1f} in^3")
        
        print(f" \tSx1: {self.Sx1_plf:.1f} in^2")
        print(f" \tSx2: {self.Sx2_plf:.1f} in^2")
        print(f" \tSy1: {self.Sy1_plf:.1f} in^2")
        print(f" \tSy2: {self.Sy2_plf:.1f} in^2")
        
        
        
    def plot_results(self):
        pass






















