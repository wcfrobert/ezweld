import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.colors as mcolors
import matplotlib.cm as mcm
import math
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots
pio.renderers.default = "browser"


MIN_PATCH_SIZE = 0.25  # inches


class WeldGroup:
    """
    WeldGroup objects are numerical representation of welded connections.
    
    Input Arguments:
        None               
        
    Public Methods:
        add_line()
        add_rectangle()
        add_circle()
        rotate()
        solve()
        preview()
        plot_results()
        plot_results_3D()
    """
    def __init__(self):
        # applied force
        self.Vx = None                  # applied shear horizontal X
        self.Vy = None                  # applied shear vertical Y
        self.tension = None             # applied axial tension
        self.Mx = None                  # applied out of plane moment about X
        self.My = None                  # applied out of plane moment about Y
        self.torsion = None             # applied in-plane torsion about Z
        
        # geometric properties (stress)
        self.x_centroid = None          # centroid x
        self.y_centroid = None          # centroid y
        self.A = None                   # total area of welds
        self.Ix = None                  # moment of inertia X
        self.Iy = None                  # moment of inertia Y
        self.Iz = None                  # polar moment of inertia = Ix + Iy
        self.Ixy = None                 # product moment of inertia
        self.theta_p = None             # angle offset to principal axis
        self.Sx1 = None                 # elastic modulus top fiber
        self.Sx2 = None                 # elastic modulus bottom fiber
        self.Sy1 = None                 # elastic modulus right fiber
        self.Sy2 = None                 # elastic modulus left fiber
        
        # geometric properties (unit force)
        self.x_centroid_force = None    # centroid x. Same as above but added for consistency
        self.y_centroid_force = None    # centroid y. Same as above but added for consistency
        self.L_force = None             # total length of weld
        self.Le_force = None            # adjusted total length of weld (when welds are same not the thickness)
        self.Ix_force = None            # SAME AS ABOVE but with one length dimension less
        self.Iy_force = None            # SAME AS ABOVE but with one length dimension less
        self.Iz_force = None            # SAME AS ABOVE but with one length dimension less
        self.Ixy_force = None           # SAME AS ABOVE but with one length dimension less
        self.theta_p_force = None       # angle offset to principal axis same as above for consistency
        self.Sx1_force = None           # SAME AS ABOVE but with one length dimension less
        self.Sx2_force = None           # SAME AS ABOVE but with one length dimension less
        self.Sy1_force = None           # SAME AS ABOVE but with one length dimension less
        self.Sy2_force = None           # SAME AS ABOVE but with one length dimension less
        
        # weld group could contain multiple weld lines. Each weld line could in turn contain many small weld patches (discretization)
        # the dict below stores every patch of weld in our weld group
        self.dict_welds = {"x_centroid":[],              # x coordinate of centroid of patch
                           "y_centroid":[],              # y coordinate of centroid of patch
                           "x_start":[],                 # x coordinate of start node
                           "y_start":[],                 # y coordinate of start node
                           "x_end":[],                   # x coordinate of end node
                           "y_end":[],                   # y coordinate of end node
                           "thickness":[],               # patch throat thickness
                           "length":[],                  # patch length
                           "area":[],                    # patch area = length * thickness
                           "length_effective":[],        # adjusted length (for variable thickness weld groups)
                           
                           "vx_direct": [],              # x direct shear from Vx
                           "vx_torsion": [],             # x torsional shear from Mz
                           "vy_direct": [],              # y direct shear from Vy
                           "vy_torsion": [],             # y torsional shear from Mz
                           "vz_direct": [],              # z shear (axial) from Vz
                           "vz_Mx": [],                  # z shear (axial) from Mx
                           "vz_My": [],                  # z shear (axial) from My
                           "vx_total": [],               # x shear total = direct + torsional
                           "vy_total": [],               # y shear total = direct + torsional
                           "vz_total": [],               # z shear total = direct + overturningX + overturningY
                           "v_resultant": [],            # resultant shear from SRSS of x, y, z shear
                           
                           "Fx":[],                      # used to verify equilibrium sum_Fx = 0
                           "Fy":[],                      # used to verify equilibrium sum_Fy = 0
                           "Fz":[],                      # used to verify equilibrium sum_Fz = 0
                           "Mxi":[],                     # used to verify equilibrium sum_Mx = 0
                           "Myi":[],                     # used to verify equilibrium sum_My = 0
                           "Mzi":[],                     # used to verify equilibrium sum_Mz = 0
                           
                           "tauX_direct":[],             # same as above but expressed in stress (ksi) rather than (k/in)
                           "tauX_torsion":[],
                           "tauY_direct":[],
                           "tauY_torsion":[],
                           "tauZ_direct":[],
                           "tauZ_Mx":[],
                           "tauZ_My":[],
                           "tauX_total": [],
                           "tauY_total": [],
                           "tauZ_total": [],
                           "sigma_vm": []
                           }
        self.v_max = None                               # maximum shear force within the weld group
        self.v_max_ID = None                            # the patch ID (or index) where maximum shear force occurs
        
        # the dict above is converted into a dataframe for return
        self.df_welds = None
        
    
    def add_rectangle(self, xo, yo, width, height, thickness):
        """
        Add a rectangular weld group.
        
        Arguments:
            xo                      float:: lower left corner x coordinate
            yo                      float:: lower left corner y coordinate
            width                   float:: width of rectangle
            height                  float:: height of rectangle
            thickness               float:: weld throat thickness
        """
        pt1 = [xo, yo]
        pt2 = [xo + width, yo]
        pt3 = [xo + width, yo + height]
        pt4 = [xo, yo + height]
        
        self.add_line(start=pt1, end=pt2, thickness=thickness)
        self.add_line(start=pt4, end=pt3, thickness=thickness)
        self.add_line(start=pt1, end=pt4, thickness=thickness)
        self.add_line(start=pt2, end=pt3, thickness=thickness)
            
        
    def add_circle(self, xo, yo, diameter, thickness):
        """
        Add a circular weld group.
        
        Arguments:
            xo                      float:: circle center x coordinate
            yo                      float:: circle center y coordinate
            diameter                float:: circle center diameter
            thickness               float:: weld throat thickness
        """
        # calculate circumference to determine number of segments
        circumference = diameter * math.pi
        segments = int(circumference // MIN_PATCH_SIZE)
        
        # divide into angle increments from 0 to 360
        theta_list = np.linspace(0,360,segments+1)
        theta_list = [x*math.pi/180 for x in theta_list]
        
        # get x and y coordinate with equation of circle
        x_list = [xo+diameter/2*math.cos(theta) for theta in theta_list]
        y_list = [yo+diameter/2*math.sin(theta) for theta in theta_list]
        
        # draw segments
        for i in range(len(x_list)-1):
            pt1 = [x_list[i], y_list[i]]
            pt2 = [x_list[i+1], y_list[i+1]]
            self.add_line(start=pt1, end=pt2, thickness=thickness)
    
    
    def add_line(self, start, end, thickness):
        """
        Add a weld strip to the weld group by specifying two points. 
        
        Arguments:
            start           list:: [x, y] coordinate of first point
            end             list:: [x, y] coordiante of the second point
            thickness       float:: weld throat thickness. 

        Return:
            None
        """
        # convert into numpy arrays
        start = np.array(start)
        end = np.array(end)
        position_vector = end-start
        
        # calculate number of segments
        length_line = np.linalg.norm(position_vector)
        segments = int(length_line // MIN_PATCH_SIZE) if length_line > MIN_PATCH_SIZE else 1
        length_segments = length_line / (segments)
        
        # discretize into N segments (N+1 end points)
        alpha = np.linspace(0, 1, segments+1)
        x_ends = start[0] + alpha * position_vector[0]
        y_ends = start[1] + alpha * position_vector[1]
        x_center = [(x_ends[i] + x_ends[i+1]) / 2 for i in range(len(x_ends)-1)]
        y_center = [(y_ends[i] + y_ends[i+1]) / 2 for i in range(len(y_ends)-1)]
        
        # add to dictionary storing discretization
        self.dict_welds["x_centroid"] = self.dict_welds["x_centroid"] + list(x_center)
        self.dict_welds["y_centroid"] = self.dict_welds["y_centroid"] + list(y_center)
        self.dict_welds["x_start"] = self.dict_welds["x_start"] + list(x_ends[:-1])
        self.dict_welds["y_start"] = self.dict_welds["y_start"] + list(y_ends[:-1])
        self.dict_welds["x_end"] = self.dict_welds["x_end"] + list(x_ends[1:])
        self.dict_welds["y_end"] = self.dict_welds["y_end"] + list(y_ends[1:])
        self.dict_welds["length"] = self.dict_welds["length"] + [length_segments] * segments
        self.dict_welds["thickness"] = self.dict_welds["thickness"] + [thickness] * segments
        self.dict_welds["area"] = self.dict_welds["area"] + [thickness * length_segments] * segments
        
        
    def rotate(self, angle):
        """rotate all meshes by a user-specified angle in DEGREES counter-clockwise"""
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
        Calculate geometric properties of weld group. Private method called by solve() or preview().
        """
        # calculate widths and depths
        all_x = self.dict_welds["x_centroid"] + self.dict_welds["x_start"] + self.dict_welds["x_end"]
        all_y = self.dict_welds["y_centroid"] + self.dict_welds["y_start"] + self.dict_welds["y_end"]
        
        ################ STRESS CONVENTION #################
        # centroid
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
        if self.Ix == self.Iy:
            self.theta_p = 0
        else:
            self.theta_p = (  math.atan((self.Ixy)/((self.Ix-self.Iy)/2)) / 2) * 180 / math.pi
        
        
        ################ UNIT FORCE CONVENTION #################
        # modify length to account for variable thickness. Proportioned based on min weld thickness
        t_min = min(self.dict_welds["thickness"])
        modified_length = [t/t_min * L for t,L in zip(self.dict_welds["thickness"], self.dict_welds["length"])]
        self.dict_welds["length_effective"] = modified_length
        
        # total lengths and effective length
        self.L_force = sum(self.dict_welds["length"])
        self.Le_force = sum(self.dict_welds["length_effective"])
        
        # centroid
        xL = sum([x*L for x,L in zip(self.dict_welds["x_centroid"],modified_length)])
        yL = sum([y*L for y,L in zip(self.dict_welds["y_centroid"],modified_length)])
        self.x_centroid_force = xL / self.Le_force
        self.y_centroid_force = yL / self.Le_force
        
        # moment of inertia
        self.Ix_force = sum([ L * (y - self.y_centroid)**2 for y,L in zip(self.dict_welds["y_centroid"],modified_length) ])
        self.Iy_force = sum([ L * (x - self.x_centroid)**2 for x,L in zip(self.dict_welds["x_centroid"],modified_length) ])
        self.Ixy_force = sum([ L * (y - self.y_centroid) * (x - self.x_centroid) for x,y,L in zip(self.dict_welds["x_centroid"],self.dict_welds["y_centroid"],modified_length) ])
        self.Iz_force = self.Ix_force + self.Iy_force
        
        # section modulus
        self.Sx1_force = self.Ix_force / abs(max(all_y) - self.y_centroid)
        self.Sx2_force = self.Ix_force / abs(min(all_y) - self.y_centroid)
        self.Sy1_force = self.Iy_force / abs(max(all_x) - self.x_centroid)
        self.Sy2_force = self.Iy_force / abs(min(all_x) - self.x_centroid)
        
        # principal axis
        if self.Ix_force == self.Iy_force:
            self.theta_p_force = 0
        else:
            self.theta_p_force = (  math.atan((self.Ixy_force)/((self.Ix_force-self.Iy_force)/2)) / 2) * 180 / math.pi    
            
    
    def preview(self):
        """
        preview weld group defined by user.
        """
        DEFAULT_THICKNESS = 0.25  # for display
        
        # update geometric property
        self.update_geometric_properties()
        
        # normalize thickness for display
        t_min = min(self.dict_welds["thickness"])
        line_thicknesses = [t/t_min * DEFAULT_THICKNESS for t in self.dict_welds["thickness"]]
        
        # initialize figure
        fig, axs = plt.subplots(1,2, figsize=(11,8.5), gridspec_kw={"width_ratios":[2,3]})
        
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
            axs[1].add_patch(patches.Polygon(np.array(vertices), closed=True, facecolor="steelblue",
                                          alpha=0.8, edgecolor="black", zorder=1, lw=0.5))
            
        # plot Cog
        axs[1].plot(self.x_centroid, self.y_centroid, marker="x",c="red",markersize=8,zorder=2,linestyle="none")

        # annotation for weld properties
        xo = 0.22
        yo = 0.85
        dy = 0.045
        unit = "in"
        axs[0].annotate("Weld Group Properties", 
                        (xo-0.03,yo), fontweight="bold",xycoords='axes fraction', fontsize=12, va="top", ha="left")
        axs[0].annotate(r"$x_{{cg}} = {:.2f} \quad {}$".format(self.x_centroid_force, unit), 
                        (xo,yo-dy*1), xycoords='axes fraction', fontsize=12, va="top", ha="left")
        axs[0].annotate(r"$y_{{cg}} = {:.2f} \quad {}$".format(self.y_centroid_force, unit), 
                        (xo,yo-dy*2), xycoords='axes fraction', fontsize=12, va="top", ha="left")
        axs[0].annotate(r"$L = {:.2f} \quad {}$".format(self.L_force, unit), 
                        (xo,yo-dy*3), xycoords='axes fraction', fontsize=12, va="top", ha="left")
        axs[0].annotate(r"$L_{{effective}} = {:.2f} \quad {}$".format(self.Le_force, unit), 
                        (xo,yo-dy*4), xycoords='axes fraction', fontsize=12, va="top", ha="left")
        axs[0].annotate(r"$I_x = {:.2f} \quad {}^3$".format(self.Ix_force, unit), 
                        (xo,yo-dy*5), xycoords='axes fraction', fontsize=12, va="top", ha="left")
        axs[0].annotate(r"$I_y = {:.2f} \quad {}^3$".format(self.Iy_force, unit), 
                        (xo,yo-dy*6), xycoords='axes fraction', fontsize=12, va="top", ha="left")
        axs[0].annotate(r"$I_z = {:.2f} \quad {}^3$".format(self.Iz_force, unit), 
                        (xo,yo-dy*7), xycoords='axes fraction', fontsize=12, va="top", ha="left")
        axs[0].annotate(r"$S_{{x,top}} = {:.2f} \quad {}^2$".format(self.Sx1_force, unit), 
                        (xo,yo-dy*8), xycoords='axes fraction', fontsize=12, va="top", ha="left")
        axs[0].annotate(r"$S_{{x,bottom}} = {:.2f} \quad {}^2$".format(self.Sx2_force, unit), 
                        (xo,yo-dy*9), xycoords='axes fraction', fontsize=12, va="top", ha="left")
        axs[0].annotate(r"$S_{{y,right}} = {:.2f} \quad {}^2$".format(self.Sy1_force, unit), 
                        (xo,yo-dy*10), xycoords='axes fraction', fontsize=12, va="top", ha="left")
        axs[0].annotate(r"$S_{{y,left}} = {:.2f} \quad {}^2$".format(self.Sy2_force, unit), 
                        (xo,yo-dy*11), xycoords='axes fraction', fontsize=12, va="top", ha="left")
        axs[0].annotate(r"$I_{{xy}} = {:.2f} \quad {}^3$".format(self.Ixy_force, unit), 
                        (xo,yo-dy*12), xycoords='axes fraction', fontsize=12, va="top", ha="left")
        axs[0].annotate(r"$\theta_{{p}} = {:.2f} \quad deg$".format(self.theta_p_force), 
                        (xo,yo-dy*13), xycoords='axes fraction', fontsize=12, va="top", ha="left")

        
        # styling
        axs[1].set_aspect('equal', 'datalim')
        fig.suptitle("Weld Group Preview", fontweight="bold", fontsize=16)
        axs[1].set_axisbelow(True)
        axs[0].set_xticks([])
        axs[0].set_yticks([])
        plt.tight_layout()
            
            
    def solve(self, Vx=0, Vy=0, Mx=0, My=0, torsion=0, tension=0):
        """
        Start analysis.
        
        Arguments:
            Vx                  (OPTIONAL) float:: in-plane shear in X direction. Default = 0
            Vy                  (OPTIONAL) float:: in-plane shear in Y direction. Default = 0
            Mx                  (OPTIONAL) float:: out-of-plane moment around X-axis. Default = 0
            My                  (OPTIONAL) float:: out-of-plane moment around Y-axis. Default = 0
            torsion             (OPTIONAL) float:: in-plane torsion. Default = 0
            tension             (OPTIONAL) float:: out-of-plane axial force (negative is compression). Default = 0
            
        Returns:
            df_weld             dataframe:: calculation summary table
        """
        # store applied loading
        self.Vx = Vx
        self.Vy = Vy
        self.Mx = Mx
        self.My = My
        self.torsion = torsion
        self.tension = tension
        
        # calculate geometric properties
        self.update_geometric_properties()
        
        # EXCEPTION: no applied loading
        if Vx==0 and Vy==0 and Mx==0 and My==0 and torsion==0 and tension==0:
            return "No loading applied to weld group"
        
        # WARNING: weld group not defined with respect to principal axis
        if abs(self.theta_p) > 0.1:  #deg
            print("WARNING: Weld group is not in its principal orientation. Results may not be correct!")
            print(f"Please rotate by {self.theta_p:.2f} degrees using the .rotate() method before solving.")
        
        # loop through every weld patch
        for i in range(len(self.dict_welds["length_effective"])):
            ################# FORCE PER UNIT LENGTH ########################
            Li = self.dict_welds["length"][i]
            dx = self.dict_welds["x_centroid"][i] - self.x_centroid
            dy = self.dict_welds["y_centroid"][i] - self.y_centroid
            length_factor = self.dict_welds["length_effective"][i] / self.dict_welds["length"][i]
            
            # kip/in (per foot basis)
            vx_direct = - Vx / self.Le_force * length_factor
            vx_torsion = torsion * dy / self.Iz_force * length_factor
            vy_direct = - Vy / self.Le_force * length_factor
            vy_torsion = - torsion * dx / self.Iz_force * length_factor
            vz_direct = - tension / self.Le_force * length_factor
            vz_Mx = -Mx * dy / self.Ix_force * length_factor
            vz_My = My * dx / self.Iy_force * length_factor
            vx_total = vx_direct + vx_torsion
            vy_total = vy_direct + vy_torsion
            vz_total = vz_direct + vz_Mx + vz_My
            v_resultant = math.sqrt(vx_total**2 + vy_total**2 + vz_total**2)
            
            # kips (based on actual weld length)
            Fx = vx_total * Li
            Fy = vy_total * Li
            Fz = vz_total * Li
            Mxi = Fz * dy
            Myi = -Fz * dx
            Mzi = - Fx * dy + Fy * dx
            
            # append results to dictionary
            self.dict_welds["vx_direct"].append(vx_direct)
            self.dict_welds["vx_torsion"].append(vx_torsion)
            self.dict_welds["vy_direct"].append(vy_direct)
            self.dict_welds["vy_torsion"].append(vy_torsion)
            self.dict_welds["vz_direct"].append(vz_direct)
            self.dict_welds["vz_Mx"].append(vz_Mx)
            self.dict_welds["vz_My"].append(vz_My)
            self.dict_welds["vx_total"].append(vx_total)
            self.dict_welds["vy_total"].append(vy_total)
            self.dict_welds["vz_total"].append(vz_total)
            self.dict_welds["v_resultant"].append(v_resultant)
            self.dict_welds["Fx"].append(Fx)
            self.dict_welds["Fy"].append(Fy)
            self.dict_welds["Fz"].append(Fz)
            self.dict_welds["Mxi"].append(Mxi)
            self.dict_welds["Myi"].append(Myi)
            self.dict_welds["Mzi"].append(Mzi)
        
            ################# STRESS ########################
            tauX_direct = - Vx / self.A
            tauX_torsion = torsion * dy / self.Iz
            tauY_direct = - Vy / self.A
            tauY_torsion = - torsion * dx / self.Iz
            tauZ_direct = - tension / self.A
            tauZ_Mx = -Mx * dy / self.Ix
            tauZ_My = My * dx / self.Iy
            tauX_total = tauX_direct + tauX_torsion
            tauY_total = tauY_direct + tauY_torsion
            tauZ_total = tauZ_direct + tauZ_Mx + tauZ_My
            simplified_vm = math.sqrt(3*(tauX_total**2 + tauY_total**2 + tauZ_total**2))
            
            self.dict_welds["tauX_direct"].append(tauX_direct)
            self.dict_welds["tauX_torsion"].append(tauX_torsion)
            self.dict_welds["tauY_direct"].append(tauY_direct)
            self.dict_welds["tauY_torsion"].append(tauY_torsion)
            self.dict_welds["tauZ_direct"].append(tauZ_direct)
            self.dict_welds["tauZ_Mx"].append(tauZ_Mx)
            self.dict_welds["tauZ_My"].append(tauZ_My)
            self.dict_welds["tauX_total"].append(tauX_total)
            self.dict_welds["tauY_total"].append(tauY_total)
            self.dict_welds["tauZ_total"].append(tauZ_total)
            self.dict_welds["sigma_vm"].append(simplified_vm)
        
        # convert dict to a dataframe for return
        self.df_welds = pd.DataFrame(self.dict_welds)
        
        # check equilibrium
        self.check_equilibrium()
        
        return self.df_welds
        
        
    def check_equilibrium(self):
        """
        Check if results are correct by checking equilibrium. Probably not needed.
        More for me to debug.
        """
        TOL = 0.1
        
        sumFx = sum(self.dict_welds["Fx"])
        sumFy = sum(self.dict_welds["Fy"])
        sumFz = sum(self.dict_welds["Fz"])
        sumMx = sum(self.dict_welds["Mxi"])
        sumMy = sum(self.dict_welds["Myi"])
        sumMz = sum(self.dict_welds["Mzi"])
        
        residual_Fx = sumFx + self.Vx
        residual_Fy = sumFy + self.Vy
        residual_Fz = sumFz + self.tension
        residual_Mx = sumMx + self.Mx
        residual_My = sumMy + self.My
        residual_Mz = sumMz + self.torsion
        
        flag_Fx = "OK" if abs(residual_Fx) < TOL else "WARNING: NOT OKAY. EQUILIBRIUM NOT SATISFIED"
        flag_Fy = "OK" if abs(residual_Fy) < TOL else "WARNING: NOT OKAY. EQUILIBRIUM NOT SATISFIED"
        flag_Fz = "OK" if abs(residual_Fz) < TOL else "WARNING: NOT OKAY. EQUILIBRIUM NOT SATISFIED"
        flag_Mx = "OK" if abs(residual_Mx) < TOL else "WARNING: NOT OKAY. EQUILIBRIUM NOT SATISFIED"
        flag_My = "OK" if abs(residual_My) < TOL else "WARNING: NOT OKAY. EQUILIBRIUM NOT SATISFIED"
        flag_Mz = "OK" if abs(residual_Mz) < TOL else "WARNING: NOT OKAY. EQUILIBRIUM NOT SATISFIED"
        
        if flag_Fx !="OK" or flag_Fy !="OK" or flag_Fz !="OK" or flag_Mx !="OK" or flag_My !="OK" or flag_Mz !="OK":
            print(f"\t\t Fx_applied={self.Vx:.2f},\t  sumFx={sumFx:.2f},\t residual = {residual_Fx:.2f},\t {flag_Fx}")
            print(f"\t\t Fy_applied={self.Vy:.2f},\t  sumFy={sumFy:.2f},\t residual = {residual_Fy:.2f},\t {flag_Fy}")
            print(f"\t\t Fz_applied={self.tension:.2f},\t  sumFz={sumFz:.2f},\t residual = {residual_Fz:.2f},\t {flag_Fz}")
            print(f"\t\t Mx_applied={self.Mx:.2f},\t  sumMx={sumMx:.2f},\t residual = {residual_Mx:.2f},\t {flag_Mx}")
            print(f"\t\t My_applied={self.My:.2f},\t  sumMy={sumMy:.2f},\t residual = {residual_My:.2f},\t {flag_My}")
            print(f"\t\t Mz_applied={self.torsion:.2f},\t  sumMz={sumMz:.2f},\t residual = {residual_Mz:.2f},\t {flag_Mz}")
            raise RuntimeError("Error: Equilibrium check failed.")
        
        
    def plot_results(self, plot="force", colormap="jet", cmin="auto", cmax="auto"):
        """
        plot results using matplotlib
        """
        # plot unit force or stress
        if plot == "force":
            magnitude = self.dict_welds["v_resultant"]
            title = "Weld Group Contours (k/in)"
        else:
            magnitude = self.dict_welds["sigma_vm"]
            title = "Weld Group Contours (ksi)"
        
        # normalize thickness for display
        DEFAULT_THICKNESS = 0.25
        t_min = min(self.dict_welds["thickness"])
        line_thicknesses = [t/t_min * DEFAULT_THICKNESS for t in self.dict_welds["thickness"]]
        
        # initialize figure
        fig, axs = plt.subplots(1,2, figsize=(11,8.5), gridspec_kw={"width_ratios":[2,3]})
        
        # colormap
        cm = plt.get_cmap(colormap)
        cmin = min(magnitude) if cmin == "auto" else cmin
        cmax = max(magnitude) if cmax == "auto" else cmax
        if math.isclose(cmax-cmin, 0):
            cmin = 0
        v_normalized = [(v-cmin)/(cmax-cmin) for v in magnitude]
        colors = [cm(x) for x in v_normalized]
            
        # add colorbar to plot
        tick_values = np.linspace(cmin,cmax,6)
        norm = mcolors.Normalize(vmin=cmin, vmax=cmax)
        fig.colorbar(mcm.ScalarMappable(norm=norm, cmap=cm), 
                     orientation='vertical',
                     ax=axs[1],
                     ticks=tick_values)
        
        # plot weld mesh with polygon patches
        for i in range(len(self.dict_welds["x_start"])):
            x0 = self.dict_welds["x_start"][i]
            x1 = self.dict_welds["x_end"][i]
            y0 = self.dict_welds["y_start"][i]
            y1 = self.dict_welds["y_end"][i]
            
            # calculate perpendicular direction vector to offset by thickness
            u = np.array([x1,y1]) - np.array([x0,y0])
            u_unit = u / np.linalg.norm(u)
            v_unit = np.array([u_unit[1], - u_unit[0]])
            
            # plot using polygon patches
            pt1 = np.array([x0, y0]) + v_unit * line_thicknesses[i]
            pt2 = np.array([x0, y0]) - v_unit * line_thicknesses[i]
            pt3 = np.array([x1, y1]) - v_unit * line_thicknesses[i]
            pt4 = np.array([x1, y1]) + v_unit * line_thicknesses[i]
            vertices = [pt1, pt2, pt3, pt4, pt1]
            axs[1].add_patch(patches.Polygon(np.array(vertices), closed=True, facecolor=colors[i],
                                          alpha=0.8, edgecolor=colors[i], zorder=1, lw=0.5))
        
        # plot Cog
        axs[1].plot(self.x_centroid, self.y_centroid, marker="x",c="red",markersize=8,zorder=2,linestyle="none")
        axs[1].annotate("",
                        xy=(self.x_centroid+1, self.y_centroid), 
                        xytext=(self.x_centroid, self.y_centroid),
                        color="black",
                        arrowprops=dict(arrowstyle="simple,head_length=0.4,head_width=0.3,tail_width=0.10",
                                            fc="black", ec="black"))
        axs[1].annotate("",
                        xy=(self.x_centroid, self.y_centroid+1), 
                        xytext=(self.x_centroid, self.y_centroid),
                        color="black",
                        arrowprops=dict(arrowstyle="simple,head_length=0.4,head_width=0.3,tail_width=0.10",
                                            fc="black", ec="black"))
        axs[1].annotate("X",
                        xy=(self.x_centroid, self.y_centroid), 
                        xytext=(self.x_centroid+1.1, self.y_centroid),
                        va="center",
                        color="black")
        axs[1].annotate("Y",
                        xy=(self.x_centroid, self.y_centroid), 
                        xytext=(self.x_centroid, self.y_centroid+1.1),
                        ha="center",
                        color="black")
        
        
        # annotation for weld properties
        xo = 0.22
        yo = 0.98
        dy = 0.045
        axs[0].annotate("Weld Group Properties", 
                        (xo-0.03,yo), fontweight="bold",xycoords='axes fraction', fontsize=12, va="top", ha="left")
        if plot == "force":
            axs[0].annotate(r"$x_{{cg}} = {:.2f} \quad in$".format(self.x_centroid_force), 
                            (xo,yo-dy*1), xycoords='axes fraction', fontsize=12, va="top", ha="left")
            axs[0].annotate(r"$y_{{cg}} = {:.2f} \quad in$".format(self.y_centroid_force), 
                            (xo,yo-dy*2), xycoords='axes fraction', fontsize=12, va="top", ha="left")
            axs[0].annotate(r"$L = {:.2f} \quad in$".format(self.L_force), 
                            (xo,yo-dy*3), xycoords='axes fraction', fontsize=12, va="top", ha="left")
            axs[0].annotate(r"$L_{{effective}} = {:.2f} \quad in$".format(self.Le_force), 
                            (xo,yo-dy*4), xycoords='axes fraction', fontsize=12, va="top", ha="left")
            axs[0].annotate(r"$I_x = {:.2f} \quad in^3$".format(self.Ix_force), 
                            (xo,yo-dy*5), xycoords='axes fraction', fontsize=12, va="top", ha="left")
            axs[0].annotate(r"$I_y = {:.2f} \quad in^3$".format(self.Iy_force), 
                            (xo,yo-dy*6), xycoords='axes fraction', fontsize=12, va="top", ha="left")
            axs[0].annotate(r"$I_z = {:.2f} \quad in^3$".format(self.Iz_force), 
                            (xo,yo-dy*7), xycoords='axes fraction', fontsize=12, va="top", ha="left")
            axs[0].annotate(r"$S_{{x,top}} = {:.2f} \quad in^2$".format(self.Sx1_force), 
                            (xo,yo-dy*8), xycoords='axes fraction', fontsize=12, va="top", ha="left")
            axs[0].annotate(r"$S_{{x,bottom}} = {:.2f} \quad in^2$".format(self.Sx2_force), 
                            (xo,yo-dy*9), xycoords='axes fraction', fontsize=12, va="top", ha="left")
            axs[0].annotate(r"$S_{{y,right}} = {:.2f} \quad in^2$".format(self.Sy1_force), 
                            (xo,yo-dy*10), xycoords='axes fraction', fontsize=12, va="top", ha="left")
            axs[0].annotate(r"$S_{{y,left}} = {:.2f} \quad in^2$".format(self.Sy2_force), 
                            (xo,yo-dy*11), xycoords='axes fraction', fontsize=12, va="top", ha="left")
            axs[0].annotate(r"$I_{{xy}} = {:.2f} \quad in^3$".format(self.Ixy_force), 
                            (xo,yo-dy*12), xycoords='axes fraction', fontsize=12, va="top", ha="left")
            axs[0].annotate(r"$\theta_{{p}} = {:.2f} \quad deg$".format(self.theta_p_force), 
                            (xo,yo-dy*13), xycoords='axes fraction', fontsize=12, va="top", ha="left")
        else:
            axs[0].annotate(r"$x_{{cg}} = {:.2f} \quad in$".format(self.x_centroid), 
                            (xo,yo-dy*1), xycoords='axes fraction', fontsize=12, va="top", ha="left")
            axs[0].annotate(r"$y_{{cg}} = {:.2f} \quad in$".format(self.y_centroid), 
                            (xo,yo-dy*2), xycoords='axes fraction', fontsize=12, va="top", ha="left")
            axs[0].annotate(r"$A = {:.2f} \quad in^2$".format(self.A), 
                            (xo,yo-dy*3), xycoords='axes fraction', fontsize=12, va="top", ha="left")
            axs[0].annotate(r"$I_x = {:.2f} \quad in^4$".format(self.Ix), 
                            (xo,yo-dy*4), xycoords='axes fraction', fontsize=12, va="top", ha="left")
            axs[0].annotate(r"$I_y = {:.2f} \quad in^4$".format(self.Iy), 
                            (xo,yo-dy*5), xycoords='axes fraction', fontsize=12, va="top", ha="left")
            axs[0].annotate(r"$I_z = {:.2f} \quad in^4$".format(self.Iz), 
                            (xo,yo-dy*6), xycoords='axes fraction', fontsize=12, va="top", ha="left")
            axs[0].annotate(r"$S_{{x,top}} = {:.2f} \quad in^3$".format(self.Sx1), 
                            (xo,yo-dy*7), xycoords='axes fraction', fontsize=12, va="top", ha="left")
            axs[0].annotate(r"$S_{{x,bottom}} = {:.2f} \quad in^3$".format(self.Sx2), 
                            (xo,yo-dy*8), xycoords='axes fraction', fontsize=12, va="top", ha="left")
            axs[0].annotate(r"$S_{{y,right}} = {:.2f} \quad in^3$".format(self.Sy1), 
                            (xo,yo-dy*9), xycoords='axes fraction', fontsize=12, va="top", ha="left")
            axs[0].annotate(r"$S_{{y,left}} = {:.2f} \quad in^3$".format(self.Sy2), 
                            (xo,yo-dy*10), xycoords='axes fraction', fontsize=12, va="top", ha="left")
            axs[0].annotate(r"$I_{{xy}} = {:.2f} \quad in^4$".format(self.Ixy), 
                            (xo,yo-dy*11), xycoords='axes fraction', fontsize=12, va="top", ha="left")
            axs[0].annotate(r"$\theta_{{p}} = {:.2f} \quad deg$".format(self.theta_p), 
                            (xo,yo-dy*12), xycoords='axes fraction', fontsize=12, va="top", ha="left")
            
        xo = 0.22
        yo = 0.35
        dy = 0.045
        axs[0].annotate("Applied Loading", 
                        (xo-0.03,yo), fontweight="bold",xycoords='axes fraction', fontsize=12, va="top", ha="left")
        axs[0].annotate(r"$V_x = {:.2f} \quad kips$".format(self.Vx), 
                        (xo,yo-dy*1), xycoords='axes fraction', fontsize=12, va="top", ha="left")
        axs[0].annotate(r"$V_y = {:.2f} \quad kips$".format(self.Vy), 
                        (xo,yo-dy*2), xycoords='axes fraction', fontsize=12, va="top", ha="left")
        axs[0].annotate(r"$V_z = {:.2f} \quad kips$".format(self.tension), 
                        (xo,yo-dy*3), xycoords='axes fraction', fontsize=12, va="top", ha="left")
        axs[0].annotate(r"$M_x = {:.2f} \quad k.in$".format(self.Mx), 
                        (xo,yo-dy*4), xycoords='axes fraction', fontsize=12, va="top", ha="left")
        axs[0].annotate(r"$M_y = {:.2f} \quad k.in$".format(self.My), 
                        (xo,yo-dy*5), xycoords='axes fraction', fontsize=12, va="top", ha="left")
        axs[0].annotate(r"$M_z = {:.2f} \quad k.in$".format(self.torsion), 
                        (xo,yo-dy*6), xycoords='axes fraction', fontsize=12, va="top", ha="left")
        
        # styling
        axs[1].set_aspect('equal', 'datalim')
        fig.suptitle(title, fontweight="bold", fontsize=16)
        axs[1].set_axisbelow(True)
        axs[0].set_xticks([])
        axs[0].set_yticks([])
        plt.tight_layout()
    
    
    def plot_results_3D(self, plot="force", colormap="jet", cmin="auto", cmax="auto"):
        """
        use plotly to generate an interactive plot
        """
        # plot unit force or stress
        if plot == "force":
            magnitude = self.dict_welds["v_resultant"]
            title = "Weld Group Contours (k/in)"
        else:
            magnitude = self.dict_welds["sigma_vm"]
            title = "Weld Group Contours (ksi)"
            
        # initialize a plotly figure with 4 subplots
        fig = make_subplots(rows=2, cols=2,
                            subplot_titles=("Weld Group Properties", "Contour Plot", "Applied Loading", "Quiver Plot"),
                            row_heights=[0.5, 0.5],
                            column_widths=[0.3, 0.7],
                            horizontal_spacing=0.02,
                            vertical_spacing=0.05,
                            specs = [[{"type":"xy"}, {"type":"scatter3d"}],
                                     [{"type":"xy"}, {"type":"scatter3d"}]]
                            )
        
        fig.add_trace(go.Scatter(y=[2, 3, 1]),row=1, col=1)
        fig.add_trace(go.Scatter(y=[2, 3, 1]),row=2, col=1)
        
        fig.add_trace(go.Scatter3d(x=[2, 3, 1], y=[0, 0, 0],
                                   z=[0.5, 1, 2], mode="lines"),row=1, col=2)
        fig.add_trace(go.Scatter3d(x=[2, 3, 1], y=[0, 0, 0],
                                   z=[0.5, 1, 2], mode="lines"),row=2, col=2)
        
        
        # properties table
        property_table = go.Table(header=dict(values=['A Scores', 'B Scores'],
                                                line_color='darkslategray',
                                                fill_color='lightskyblue',
                                                align='left'),
                                  cells=dict(values=[[100, 90, 80, 90], # 1st column
                                                   [95, 85, 75, 95]], # 2nd column
                                                   line_color='darkslategray',
                                                   fill_color='lightcyan',
                                                   align='left'))
        #fig.add_trace(property_table, row=2, col=1)
            
            
            
            
        # plot_data1 = go.Scatter3d(x,y,z,name="data")
        # fig.add_trace(plot_data1)
        
        # change such that axes are in proportion.
        # fig.update_scenes(aspectmode="data")
        
        # add title
        fig.update_layout(title="<b>Weld Group Result Summary</b>",
                          title_xanchor="center",
                          title_font_size=24,
                          title_x=0.5, 
                          title_y=0.95,
                          title_font_color="white")
        # background color
        fig.update_layout(paper_bgcolor="#3b3b41",
                          font_color="white")
        
        return fig





















