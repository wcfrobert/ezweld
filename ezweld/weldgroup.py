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
        # result expressed as force/length or stress
        self.output_mode = "stress"  # default
        
        # applied force
        self.Vx = None
        self.Vy = None
        self.tension = None
        self.Mx = None
        self.My = None
        self.torsion = None
        
        # geometric properties (stress)
        self.x_centroid = None
        self.y_centroid = None
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
        
        # geometric properties (unit force)
        self.x_centroid_force = None
        self.y_centroid_force = None
        self.L_force = None
        self.Le_force = None
        self.Ix_force = None
        self.Iy_force = None
        self.Iz_force = None
        self.Ixy_force = None
        self.theta_p_force = None
        self.Sx1_force = None
        self.Sx2_force = None
        self.Sy1_force = None
        self.Sy2_force = None
        
        # dictionary storing analysis data
        self.dict_welds = {"x_centroid":[],
                           "y_centroid":[],
                           "x_start":[],
                           "y_start":[],
                           "x_end":[],
                           "y_end":[],
                           "thickness":[],
                           "length":[],
                           "area":[],
                           
                           "length_effective":[],
                           "vx_direct": [],
                           "vx_torsion": [],
                           "vy_direct": [],
                           "vy_torsion": [],
                           "vz_direct": [],
                           "vz_Mx": [],
                           "vz_My": [],
                           "vx_total": [],
                           "vy_total": [],
                           "vz_total": [],
                           "v_resultant": [],
                           
                           "Fx":[],
                           "Fy":[],
                           "Fz":[],
                           "Mxi":[],
                           "Myi":[],
                           "Mzi":[],
                           
                           "tauX_direct":[],
                           "tauX_torsion":[],
                           "tauY_direct":[],
                           "tauY_torsion":[],
                           "tauZ_direct":[],
                           "tauZ_Mx":[],
                           "tauZ_My":[],
                           "tauX_total": [],
                           "tauY_total": [],
                           "tauZ_total": [],
                           "tau_x": [],
                           "tau_y": [],
                           "tau_z": [],
                           "sigma_transverse": [],
                           "tau_parallel": [],
                           "tau_transverse": [],
                           "von_mises_PJP": [],
                           "von_mises_fillet": []
                           }
        
        # von-mises stress criterion
        self.sigma_v_PJP = None
        self.sigma_v_fillet = None
        
        # master result dataframe curated for return to user
        self.df_results = None
    
    
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
        Add a circular weld group by specifying the center and a diameter
        """
        # warn user if segment < 6
        if segments < 6:
            print("Warning: circular patch must have 8 segments or more!")
            segments = 6
        
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
            thickness       (OPTIONAL) float:: weld throat thickness. 
                                Default = None. If None, results are reported in force/length instead of stress
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
        
        # if None is ever passed into the thickness argument, activate flag to report result in force/length
        if thickness == None:
            self.output_mode = "force"
            thickness = 1.0  # set thickness to unity
        
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
        
    
    def solve(self, Vx=0, Vy=0, Mx=0, My=0, torsion=0, tension=0):
        """
        Start analysis.
        
        Arguments:
            Vx                  (OPTIONAL) float:: in-plane shear in X direction
            Vy                  (OPTIONAL) float:: in-plane shear in Y direction
            Mx                  (OPTIONAL) float:: out-of-plane moment around X-axis
            My                  (OPTIONAL) float:: out-of-plane moment around Y-axis
            torsion             (OPTIONAL) float:: in-plane torsion
            tension             (OPTIONAL) float:: out-of-plane axial force (negative is compression)
            
        Returns:
            df_results          dataframe:: result table where each row represents a single weld fiber
        """
        print("Starting analysis...")
        
        if self.output_mode == "force":
            print("Thickness information is not provided. Results will be displayed in force/area.")
            
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
            raise RuntimeError("ERROR: No loading applied to weld group")
        
        
        # WARNING: if thickness information is missing
        thickness_list = [x for x in self.dict_welds["thickness"] if x==None]
        if len(thickness_list) != 0:
            print("WARNING: some thicknesses are undefined. Results will be displayed as force/length.")
            
            
        # WARNING: weld group not defined with respect to principal axis
        if abs(self.theta_p) > 1:  #deg
            print("WARNING: Weld group should be rotated to its principal orientation.")
            print("WARNING: Please rotate by {self.theta_p:.2f} degrees by calling the .rotate() method before solving.")
        
        
        for i in range(len(self.dict_welds["length_effective"])):
            ################# FORCE PER UNIT LENGTH ########################
            if i==0:
                print("\t Calculating demand in terms of unit force")
            Li = self.dict_welds["length"][i]
            dx = self.dict_welds["x_centroid"][i] - self.x_centroid
            dy = self.dict_welds["y_centroid"][i] - self.y_centroid
            length_factor = self.dict_welds["length_effective"][i] / self.dict_welds["length"][i]
            
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
            
            Fx = vx_total * Li
            Fy = vy_total * Li
            Fz = vz_total * Li
            Mxi = Fz * dy
            Myi = -Fz * dx
            Mzi = - Fx * dy + Fy * dx
            
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
        
        
            ################# STRESS IF APPLICABLE ########################
            if self.output_mode=="stress":
                if i == 0:
                    print("\t Calculating demand in terms of stress")
                vx_direct = - Vx / self.A
                vx_torsion = torsion * dy / self.Iz
                vy_direct = - Vy / self.A
                vy_torsion = - torsion * dx / self.Iz
                vz_direct = - tension / self.A
                vz_Mx = -Mx * dy / self.Ix
                vz_My = My * dx / self.Iy
                vx_total = vx_direct + vx_torsion
                vy_total = vy_direct + vy_torsion
                vz_total = vz_direct + vz_Mx + vz_My
            else:
                vx_direct = "NA"
                vx_torsion = "NA"
                vy_direct = "NA"
                vy_torsion = "NA"
                vz_direct = "NA"
                vz_Mx = "NA"
                vz_My = "NA"
                vx_total = "NA"
                vy_total = "NA"
                vz_total = "NA"
            
            self.dict_welds["tauX_direct"].append(vx_direct)
            self.dict_welds["tauX_torsion"].append(vx_torsion)
            self.dict_welds["tauY_direct"].append(vy_direct)
            self.dict_welds["tauY_torsion"].append(vy_torsion)
            self.dict_welds["tauZ_direct"].append(vz_direct)
            self.dict_welds["tauZ_Mx"].append(vz_Mx)
            self.dict_welds["tauZ_My"].append(vz_My)
            self.dict_welds["tauX_total"].append(vx_total)
            self.dict_welds["tauY_total"].append(vy_total)
            self.dict_welds["tauZ_total"].append(vz_total)
        
        
        # check equilibrium
        self.check_equilibrium()
        
        # convert results to dataframe for output
        self.df_results = pd.DataFrame(self.dict_welds)
        
        print("Done. Thank you for using EZweld!")
        return self.df_results
        
    
    def update_geometric_properties(self):
        """
        calculate geometric properties of weld group.
        """
        # calculate widths and depths
        all_x = self.dict_welds["x_centroid"] + self.dict_welds["x_start"] + self.dict_welds["x_end"]
        all_y = self.dict_welds["y_centroid"] + self.dict_welds["y_start"] + self.dict_welds["y_end"]
        
        ################ STRESS CONVENTION IF APPLICABLE #################
        if self.output_mode == "stress":
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
            if self.Ix==self.Iy:
                self.theta_p = 0
            else:
                self.theta_p = (  math.atan((self.Ixy)/((self.Ix-self.Iy)/2)) / 2) * 180 / math.pi
        
        
        ################ UNIT FORCE CONVENTION #################
        # modify length to account for variable thickness
        t_min = min(self.dict_welds["thickness"])
        modified_length = [t/t_min * L for t,L in zip(self.dict_welds["thickness"], self.dict_welds["length"])]
        self.dict_welds["length_effective"] = modified_length
        
        # total lengths
        self.L_force = sum(self.dict_welds["length"])
        self.Le_force = sum(modified_length)
        
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
        if self.Ix_force==self.Iy_force:
            self.theta_p_force = 0
        else:
            self.theta_p_force = (  math.atan((self.Ixy_force)/((self.Ix_force-self.Iy_force)/2)) / 2) * 180 / math.pi
        
         
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
        
        
    def preview(self, unit="in"):
        """
        preview weld group defined by user.
        """
        DEFAULT_THICKNESS = 0.25  # for display
        
        # update geometric property
        self.update_geometric_properties()
        
        # normalize thickness for display
        if self.output_mode == "stress":
            t_min = min(self.dict_welds["thickness"])
            line_thicknesses = [t/t_min * DEFAULT_THICKNESS for t in self.dict_welds["thickness"]]
        else:
            line_thicknesses = [1 * DEFAULT_THICKNESS for t in self.dict_welds["thickness"]]
        
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
            # xlim and ylim do not adjust properly with only patches. plot the centroids as well but make them invisible
            axs[1].plot([xc],[yc],c="black",marker="o",markersize=2, alpha=0)
            
        # plot Cog
        axs[1].plot(self.x_centroid, self.y_centroid, marker="*",c="red",markersize=8,zorder=2,linestyle="none")
        axs[1].annotate("CoG",xy=(self.x_centroid, self.y_centroid), xycoords='data', color="red",
                     xytext=(5, -5), textcoords='offset points', fontsize=14, va="top", zorder=3)
        
        
        # annotation for weld properties
        xo = 0.12
        yo = 0.97
        dy = 0.045
        axs[0].annotate("Stress Calculations", 
                        (xo-0.03,yo), fontweight="bold",
                        xycoords='axes fraction', fontsize=12, va="top", ha="left")
        
        if self.output_mode == "force":
            axs[0].annotate("Not applicable. Thickness not provided.", 
                            (xo,yo-dy*1), xycoords='axes fraction', fontsize=12, va="top", ha="left")
        else:
            axs[0].annotate(r"$x_{{cg}} = {:.2f} \quad {}$".format(self.x_centroid, unit), 
                            (xo,yo-dy*1), xycoords='axes fraction', fontsize=12, va="top", ha="left")
            axs[0].annotate(r"$y_{{cg}} = {:.2f} \quad {}$".format(self.y_centroid, unit), 
                            (xo,yo-dy*2), xycoords='axes fraction', fontsize=12, va="top", ha="left")
            axs[0].annotate(r"$area = {:.2f} \quad {}^2$".format(self.A, unit), 
                            (xo,yo-dy*3), xycoords='axes fraction', fontsize=12, va="top", ha="left")
            axs[0].annotate(r"$I_x = {:.2f} \quad {}^4$".format(self.Ix, unit), 
                            (xo,yo-dy*4), xycoords='axes fraction', fontsize=12, va="top", ha="left")
            axs[0].annotate(r"$I_y = {:.2f} \quad {}^4$".format(self.Iy, unit), 
                            (xo,yo-dy*5), xycoords='axes fraction', fontsize=12, va="top", ha="left")
            axs[0].annotate(r"$I_z = {:.2f} \quad {}^4$".format(self.Iz, unit), 
                            (xo,yo-dy*6), xycoords='axes fraction', fontsize=12, va="top", ha="left")
            axs[0].annotate(r"$I_{{xy}} = {:.2f} \quad {}^4$".format(self.Ixy, unit), 
                            (xo,yo-dy*7), xycoords='axes fraction', fontsize=12, va="top", ha="left")
            axs[0].annotate(r"$\theta_{{p}} = {:.2f} \quad deg$".format(self.theta_p), 
                            (xo,yo-dy*8), xycoords='axes fraction', fontsize=12, va="top", ha="left")
    
        yo = 0.50
        dy = 0.045
        axs[0].annotate("Unit Force Calculations", 
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
        axs[0].annotate(r"$I_{{xy}} = {:.2f} \quad {}^3$".format(self.Ixy_force, unit), 
                        (xo,yo-dy*8), xycoords='axes fraction', fontsize=12, va="top", ha="left")
        axs[0].annotate(r"$\theta_{{p}} = {:.2f} \quad deg$".format(self.theta_p_force), 
                        (xo,yo-dy*9), xycoords='axes fraction', fontsize=12, va="top", ha="left")

        
        # styling
        axs[1].set_aspect('equal', 'datalim')
        fig.suptitle("Weld Group Preview", fontweight="bold", fontsize=16)
        axs[1].set_axisbelow(True)
        axs[0].set_xticks([])
        axs[0].set_yticks([])
        plt.tight_layout()
        
        
    def check_equilibrium(self):
        """
        Check if results are sensible by checking equilibrium.
        """
        TOL = 0.1
        print("\t Checking equilibrium:")
        
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
        
        print(f"\t\t Fx_applied={self.Vx:.2f},\t  sumFx={sumFx:.2f},\t residual = {residual_Fx:.2f},\t {flag_Fx}")
        print(f"\t\t Fy_applied={self.Vy:.2f},\t  sumFy={sumFy:.2f},\t residual = {residual_Fy:.2f},\t {flag_Fy}")
        print(f"\t\t Fz_applied={self.tension:.2f},\t  sumFz={sumFz:.2f},\t residual = {residual_Fz:.2f},\t {flag_Fz}")
        
        print(f"\t\t Mx_applied={self.Mx:.2f},\t  sumMx={sumMx:.2f},\t residual = {residual_Mx:.2f},\t {flag_Mx}")
        print(f"\t\t My_applied={self.My:.2f},\t  sumMy={sumMy:.2f},\t residual = {residual_My:.2f},\t {flag_My}")
        print(f"\t\t Mz_applied={self.torsion:.2f},\t  sumMz={sumMz:.2f},\t residual = {residual_Mz:.2f},\t {flag_Mz}")
        
        
        
    def plot_results(self):
        pass






















