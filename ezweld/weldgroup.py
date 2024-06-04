import pandas as pd


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
        self.xc = None
        self.yc = None
        
        # geometric properties (stress)
        self.A = None
        self.Sx_stress = None
        self.Sy_stress = None
        self.Jw_stress = None
        
        # geometric properties (force per unit length)
        self.Lw = None
        self.Sx = None
        self.Sy = None
        self.Jw = None
        
        # dictionary storing discretization of weld group
        self.dict_welds = {"id":[],
                           "x":[],
                           "y":[],
                           "thickness":[],
                           "length":[],
                           "area":[],
                           "longitudinal_vec":[]}
        
        # the above dict is converted to dataframe for faster query and compute
        self.df_welds = None
    
    
    def add_rectangle(self, xo, yo, width, height, thickness=5/16, segmentx="auto", segmenty="auto"):
        pass
    
    
    def add_circle(self, xo, yo, diameter, thickness=5/16, segments="auto"):
        pass
    
    
    def add_line(self, start, end, thickness=5/16, segments="auto"):
        """
        Add a weld strip by specifying two points. 
        
        Within structural engineering, weld throat thickness is usually not specified
        until later, and forces are in force/length rather than stress. By default, 
        assume 5/16 inch throat thickness.
        
        By default, number of segment per strip will be max(L/20, 1 inch)
        
        """
        pass
    
    def update_geometric_properties(self):
        pass
    
    def solve(self, Vx=0, Vy=0, Mx=0, My=0, torsion=0, tension=0):
        pass
    
    def preview(self):
        pass
    
    def plot_results(self):
        pass