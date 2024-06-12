<h1 align="center">
  <br>
  <img src="https://github.com/wcfrobert/ezweld/blob/master/doc/logo.png?raw=true" alt="logo" style="width: 60%;" />
  <br>
  Weld Stress Calculation in Python
  <br>
</h1>


<div align="center">
  <img src="https://github.com/wcfrobert/ezweld/blob/master/doc/demo.gif?raw=true" alt="demo" style="width: 75%;" />
</div>


WORK IN PROGRESS.....

- [Introduction](#introduction)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Usage](#usage)
- [Theoretical Background - Weld Stress Determination Via Elastic Method](#theoretical-background---weld-stress-determination-via-elastic-method)
- [Assumptions](#assumptions)
- [License](#license)


## Introduction

EZweld is a python package that calculates stress demand in weld groups subjected to both in-plane and out-of-plane loading. It does so using the elastic method as outlined in the AISC Steel Construction Manual. 1.) Define a weld group 2.) apply loading 3.) get the results back.

**Disclaimer:** this package is meant for <u>personal and educational use only</u>.


## Quick Start

Run main.py:

```python
import ezweld

# initialize a weld group
weld_group = ezweld.weldgroup.WeldGroup()

# draw welds
weld_group.add_line(start=[0,0], end=[0,10], segments=20)
weld_group.add_line(start=[0,0], end=[10,10], segments=20)

# preview geometry
weld_group.preview()

# calculate stresses using the elastic method
results = weld_group.solve(Vx=0, Vy=100, tension=0, Mx=1000, My=0, torsion=0)

# plot weld stress
weld_group.plot_results()
```

Sign convention for applied loading:

<div align="center">
  <img src="https://github.com/wcfrobert/ezweld/blob/master/doc/weld_dof.png?raw=true" alt="demo" style="width: 60%;" />
</div>


## Installation

**Option 1: Anaconda Python**

Run main.py using your base Anaconda environment. The following packages are used:

* Numpy
* Pandas
* Matplotlib
* Plotly

Installation procedure:

1. Download Anaconda python
2. Download this package (click the green "Code" button and download zip file)
3. Open and run "main.py" in Anaconda's Spyder IDE.


**Option 2: Regular Python**

1. Download this project to a folder of your choosing
    ```
    git clone https://github.com/wcfrobert/ezweld.git
    ```
2. Change directory into where you downloaded ezweld
    ```
    cd ezweld
    ```
3. Create virtual environment
    ```
    py -m venv venv
    ```
4. Activate virtual environment
    ```
    venv\Scripts\activate
    ```
5. Install requirements
    ```
    pip install -r requirements.txt
    ```
6. run ezweld
    ```
    py main.py
    ```



## Usage

Here are all the public methods available to the user:

**Defining Weld Group**

* `ezweld.WeldGroup.add_line(start, end, segments, thickness)`
* `ezweld.WeldGroup.add_rectangle(xo, yo, width, height, xsegments, ysegments, thickness)`
* `ezweld.WeldGroup.add_circle(xo, yo, diameter, segments, thickness)`
* `ezweld.WeldGroup.rotate(angle)`

**Solving**

* `ezweld.WeldGroup.solve(Vx, Vy, tension, Mx, My, torsion)`

**Visualizations**

* `ezweld.WeldGroup.preview()`
* `ezweld.WeldGroup.plot_results()`

For further guidance and documentation, you can access the docstring of any method using the help() command. (e.g. `help(ezweld.weldgroup.WeldGroup.add_line)`)




## Theoretical Background - Weld Stress Determination Via Elastic Method

**Analogy to Sections**

A weld group can be treated like any other geometric section. Therefore, calculating its stress state is entirely analogous to calculating elastic stress on a cross-section using the combined stress formula. You'll probably recognize these formulas as they appear in all mechanics of material textbooks. 

$$\sigma = \frac{P}{A} + \frac{M_x c_y}{I_x} + \frac{M_y c_x}{I_y}$$

$$\tau = \frac{Tc}{J}$$

Here is a figure from the “Design of Welded Structures” textbook by Omer W. Blodgett that illustrates the resemblance.

<div align="center">
  <img src="https://github.com/wcfrobert/ezweld/blob/master/doc/weld_comparison.png?raw=true" alt="demo" style="width: 50%;" />
</div>

An important precondition for using the above formula is that the section/weld-group MUST be oriented about its principal axes. If not, the section/weld-group must be rotated. EZweld makes this simple with the .rotate() method. In addition, the applied moment must be resolved about into its principal components.

<div align="center">
  <img src="https://github.com/wcfrobert/ezweld/blob/master/doc/weld_principal_axes.png?raw=true" alt="demo" style="width: 50%;" />
</div>

EZweld will warn the user if a weld group needs to be rotated. A weld group is in its principal orientation if the product of inertia is equal to zero:

$$I_{xy} = 0$$

Otherwise, the weld group must be rotated by a specific angle.

$$\theta_p = 0.5\times tan^{-1}(\frac{I_{xy}}{I_x - I_y})$$



**Geometric Properties**

A weld group, like any other sections, have geometric properties that we can calculate. EZweld does so by discretizing the weld group into little patches then applying the parallel axis theorem.

Area:

$$A_w =  \iint dA = \sum t_i L_i$$



Centroid:

$$x_{cg} = \frac{\sum x_iA_i}{\sum A}$$

$$y_{cg} = \frac{\sum y_iA_i}{\sum A}$$



Moment of Inertia:

$$I_x = \iint y^2 dA= \sum y_i^2A_i$$

$$I_y = \iint x^2 dA = \sum x_i^2A_i$$

$$I_{xy} = \iint xydA = \sum x_i y_i A_i$$

$$I_z = J = I_p = I_x + I_y$$



Section modulus:

$$S_{x,top} = \frac{I_x}{c_{y1}}$$

$$S_{x2,bot} = \frac{I_x}{c_{y2}}$$

$$S_{y,left} = \frac{I_y}{c_{x1}}$$

$$S_{y,right} = \frac{I_y}{c_{x2}}$$



Notations:

* $t_i$ = weld patch thickness
* $L_i$ = weld patch length
* $x_i$ = x distance from weld group centroid to weld patch
* $y_i$ = y distance from weld group centroid to weld patch
* $c_{y1}$ = y distance from weld group centroid to top-most fiber
* $c_{y2}$ = y distance from weld group centroid to bottom-most fiber
* $c_{x1}$ = x distance from weld group centroid to left-most fiber
* $c_{x2}$ = x distance from weld group centroid to right-most fiber



**Geometric Properties - (Treating Welds as Lines)**

In most structural engineering applications, welds are thought of as a 1-dimensional "line". As a result, weld stresses are expressed as **force per unit length** (kip/in) rather than force per unit area (ksi). This is simply a matter of convention. There are some benefits to working with one dimension less. For example, demands can now be calculated without knowing the weld's thickness, which means thickness becomes a design parameter that we can specify. But a drawback is that having one dimension less gets kind of confusing when weld groups have welds with variable thicknesses. 

Where variable weld thickness exists within a weld group, EZweld calculates an "effective" length in proportion to the minimum throat thickness within the group. This modified length is then used to calculate the geometric properties.


$$L'_{i} = \frac{t_i}{t_{min}} \times L_i$$

$$x_{cg} = \frac{\sum x_i L'_i}{\sum L'}$$


$$y_{cg} = \frac{\sum y_i L'_i}{\sum L'}$$


$$L_w =  \iint dL = \sum L'_i$$


$$I_x = \iint y^2 dL= \sum y_i^2 L'_i$$


$$I_y = \iint x^2 dL = \sum x_i^2 L'_i$$


$$I_{xy} = \iint xydL = \sum x_i y_i L'_i$$


$$I_z = J = I_p = I_x + I_y$$

$$S_{x,top} = \frac{I_x}{c_{x1}}$$

$$S_{x2,bot} = \frac{I_x}{c_{x2}}$$

$$S_{y,left} = \frac{I_y}{c_{y1}}$$

$$S_{y,right} = \frac{I_y}{c_{y2}}$$

We are essentially setting thickness to unity and subtracting on dimension from the units. We can also convert between the two conventions quite easily when the throat thicknesses are uniform.

* Converting between stress and force/length: $(ksi) = \frac{(k/in)}{t_{throat}}$

* Converting properties such as moment of inertias: $(in^4) = (in^3)\times t_{throat}$





**Calculating Stress**

A weld group may be subjected to loading in all 6 degrees of freedom. These forces are then translated into shear stresses using the geometric properties above and the elastic stress formula presented below.

<div align="center">
  <img src="https://github.com/wcfrobert/ezweld/blob/master/doc/weld_dof.png?raw=true" alt="demo" style="width: 100%;" />
</div>

Be careful when specifying negative out-of-plane axial force (i.e. compression). Compression is typically transferred through other mechanisms like bearing rather than through the weld itself. To encourage more deliberation on the part of the user, "Vz" was renamed to "tension".


Stress due to in-plane shear force ($V_x$, $V_y$):


$$\tau_{x,direct} = \frac{-V_x}{A}$$

$$\tau_{y,direct} = \frac{-V_y}{A}$$



Stress due to in-plane torsion ($torsion$):


$$\tau_{x,torsional} = \frac{torsion \times y_i}{J}$$

$$\tau_{y,torsional} = \frac{-torsion \times x_i}{J}$$



Stress from out-of-plane forces ($tension$, $M_x$, $M_y$):


$$\tau_{z,direct} = \frac{tension}{A}$$

$$\tau_{z,Mx} = \frac{M_x y_i}{I_x}$$

$$\tau_{z,My} =  \frac{M_y x_i}{I_y}$$



Sum the above terms together for the total shear stress about the three axes.

$$\tau_{x,total} = \tau_{x,direct} + \tau_{x,torsional}$$

$$\tau_{y,total} = \tau_{y,direct} + \tau_{y,torsional}$$

$$\tau_{z,total} = \tau_{z,direct} + \tau_{z,Mx} + \tau_{z,My}$$



We can get the resultant shear stress by adding the components vectorially.

$$\tau_{resultant} = \sqrt{\tau_{x,total}^2 + \tau_{y,total}^2 + \tau_{z,total}^2}$$



Unlike bolts, we do not differentiate between tension and shear (i.e. normal and shear stress) because we assume **all welds to fail in shear along the throat length**. In other words, assume zero normal stresses.

$$\sigma_{xx} = \sigma_{yy} = \sigma_{zz} = 0$$


According to the Von-Mises failure criterion:

$$\sigma_v^2 = \frac{1}{2}\times[(\sigma_{xx}-\sigma_{yy})^2 + (\sigma_{yy}-\sigma_{zz})^2 + (\sigma_{zz}-\sigma_{xx})^2 + 6(\tau_{yz}^2 + \tau_{zx}^2 + \tau_{xy}^2)]$$



Which in our case reduces to:

$$\sigma_v^2 = \frac{6}{2}\times[\tau_{yz}^2 + \tau_{zx}^2 + \tau_{xy}^2]$$

$$\sigma_v = \sqrt{3} \times \sqrt{\tau_{yz}^2 + \tau_{zx}^2 + \tau_{xy}^2} \leq F_y$$

$$\sigma_v = \sqrt{\tau_{yz}^2 + \tau_{zx}^2 + \tau_{xy}^2} \leq \frac{F_y}{\sqrt{3}} \approx 0.6F_y$$


CJPs and PJPs often do have normal stress components. But to keep things simple and conservative, assume the sigma term is multiplied by 3 as well.

$$\sigma_v = \sqrt{\sigma_{transverse}^2 + 3(\tau_{transverse}^2 + \tau_{longitudinal}^2}) \leq F_y$$


Here is an example illustrating how $V_y$ and $M_x$ is resolved into a resultant shear stress:

<div align="center">
  <img src="https://github.com/wcfrobert/ezweld/blob/master/doc/weld_stress_example.png?raw=true" alt="demo" style="width: 100%;" />
</div>


Limitations of the elastic method:

* The elastic method does not allow any plasticity which means it can be quite conservative whenever there are applied moments. Plastic method and the instant center of rotation method are less conservative if you are looking to justify extra capacity.
* The elastic method does not take into account deformation compatibility and the effect of load angle. Welds are assumed to share loads equally under direct shear. In actuality, welds oriented transversely to applied loading have up to 50% higher capacity and stiffness (but lower ductility). Transversely loaded welds tend to fracture first long before longitudinal welds can reach their full strength. Refer to the steel construction manual for more guidance on this matter.
* For out-of-plane moment, contribution of any bearing surface is ignored and the neutral axis is assumed to occur at the centroid.




## Assumptions

- Sign convention follows the right-hand rule. right is +X, top is +Y, out-of-page is +Z
- EZweld is unit-agnostic. You can either use [kip, in] or [N, mm] as long as you are consistent.
- Weld patches do not have its own local coordinate system. All stresses are expressed with respect to the global axis.
- Welds are assumed to fail in pure shear without any normal stress.
- The combined stress formula is only valid when applied about a weld group's principal orientation. EZweld will warn the user if a weld group needs to be rotated. The applied moment must be resolved to its principal components as well.




## License

MIT License

Copyright (c) 2024 Robert Wang