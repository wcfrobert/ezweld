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

EZweld is a python package that calculates stress demand in weld groups subjected to both in-plane and out-of-plane loading. It does so using the elastic method as outlined in the AISC Steel Construction Manual. 

**Disclaimer:** this package is meant for <u>personal and educational use only</u>.


- [Quick Start](#quick-start)
- [Installation](#installation)
- [Usage](#usage)
- [Theoretical Background](#theoretical-background)
- [Assumptions](#assumptions)
- [License](#license)



## Quick Start

Run main.py:

```python
import ezweld

# initialize a weld group
weld_group = ezweld.weldgroup.WeldGroup()

# draw welds
weld_group.add_line(start=[0,0], end=[0,10], segments=20, thickness=5/16)
weld_group.add_line(start=[0,0], end=[10,10], segments=20, thickness=5/16)

# preview geometry
weld_group.preview()

# calculate stresses using the elastic method
results = weld_group.solve(Vx=0, Vy=100, tension=0, Mx=1000, My=0, torsion=0)

# plot weld stress
weld_group.plot_results()
```

Sign convention for loading:

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

* `ezweld.weldgroup.WeldGroup.add_line(start, end, segments, thickness, fillet=True)`
* `ezweld.weldgroup.WeldGroup.add_rectangle(xo, yo, width, height, xsegments, ysegments, thickness, fillet=True)`
* `ezweld.weldgroup.WeldGroup.add_circle(xo, yo, diameter, segments, thickness, fillet=True)`
* `ezweld.weldgroup.WeldGroup.rotate(angle)`

**Solving**

* `ezweld.weldgroup.WeldGroup.solve(Vx=0, Vy=0, tension=0, Mx=0, My=0, torsion=0)`

**Visualizations**

* `ezweld.weldgroup.WeldGroup.preview()`
* `ezweld.weldgroup.WeldGroup.plot_results()`

For more guidance and documentation, you can access the docstring of any method using the help() command. For example, here's the output from `help(ezweld.weldgroup.WeldGroup.add_line)`

<div align="center">
  <img src="https://github.com/wcfrobert/ezweld/blob/master/doc/docstring.png?raw=true" alt="demo" style="width: 80%;" />
</div>



## Theoretical Background

**Section Analogy**

A weld group can be treated like a geometric section. Therefore, calculating its stress state is entirely analogous to calculating elastic stress on a cross-section using the elastic stress formulas. Here is a figure from the “Design of Welded Structures” textbook by Omer W. Blodgett that illustrates this similarity.

<div align="center">
  <img src="https://github.com/wcfrobert/ezweld/blob/master/doc/weld_comparison.png?raw=true" alt="demo" style="width: 50%;" />
</div>
An important precondition for using the combined stress formulas is that the section/weld-group must be oriented about its principal axes. EZweld will warn the user if a weld group needs to be rotated with the .rotate() method. In addition, the applied moment must be resolved about into its principal components.

<div align="center">
  <img src="https://github.com/wcfrobert/ezweld/blob/master/doc/weld_principal_axes.png?raw=true" alt="demo" style="width: 40%;" />
</div>


A weld group is in its principal orientation if the product of inertia is equal to zero:

$$I_{xy} = 0$$

Otherwise, the weld group must be rotated by the following angle.

$$\theta_p = 0.5\times tan^{-1}(\frac{I_{xy}}{I_x - I_y})$$



**Geometric Properties**

Like any other sections, a weld group has geometric properties that can be calculated. EZweld does so by discretizing the weld group into little patches then applying the parallel axis theorem.

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

In many engineering contexts, welds are thought of as 1-dimensional "lines". As a result, weld stresses are often expressed as **force per unit length** (e.g. kip/in) rather than force per unit area (e.g. ksi). There are some benefits to working with one dimension less. For example, demands can now be calculated without knowing the weld's thickness, which means thickness becomes a design parameter that we can specify. Here a table from the Omer W. Blodgett textbook that provides equations for common weld group geometric properties. Notice how the geometric properties are are 1 dimensions less:

<div align="center">
  <img src="https://github.com/wcfrobert/ezweld/blob/master/doc/weld_properties.png?raw=true" alt="demo" style="width: 60%;" />
</div>
One drawback, or point of confusion, is the assumption of uniform thickness within a weld group, which is not always true. The above table should NOT be used for **weld groups with variable thicknesses**. Instead, we must first calculate an "effective" length proportional to their thicknesses.

$$L_{effective} = \frac{t}{t_{min}} \times L_i$$


This modified length can then be used to calculate geometric properties.

$$x_{cg} = \frac{\sum x_i L_i}{\sum L}$$


$$y_{cg} = \frac{\sum y_i L_i}{\sum L}$$


$$L_w =  \iint dL = \sum L_i$$


$$I_x = \iint y^2 dL= \sum y_i^2 L_i$$


$$I_y = \iint x^2 dL = \sum x_i^2 L_i$$


$$I_{xy} = \iint xydL = \sum x_i y_i L_i$$


$$I_z = J = I_p = I_x + I_y$$

$$S_{x,top} = \frac{I_x}{c_{x1}}$$

$$S_{x2,bot} = \frac{I_x}{c_{x2}}$$

$$S_{y,left} = \frac{I_y}{c_{y1}}$$

$$S_{y,right} = \frac{I_y}{c_{y2}}$$

The formulas above are essentially the same as the previous section with thickness set to one. It is quite easy to convert between the two conventions:

$$(ksi) = \frac{(k/in)}{t_{throat}}$$

$$(in^4) = (in^3)\times t_{throat}$$



**Weld Stress Via Elastic Method**

A weld group may be subjected to loading in all 6 degrees of freedom. These applied loading are then translated into stresses using the geometric properties above and the elastic stress formulas below. 

<div align="center">
  <img src="https://github.com/wcfrobert/ezweld/blob/master/doc/weld_dof.png?raw=true" alt="demo" style="width: 60%;" />
</div>
Stress due to in-plane shear force ($V_x$, $V_y$):


$$v_{x,direct} = \frac{-V_x}{A_w}$$

$$v_{y,direct} = \frac{-V_y}{A_w}$$



Stress due to in-plane torsion ($torsion$):


$$v_{x,torsional} = \frac{torsion \times y_i}{J}$$

$$v_{y,torsional} = \frac{-torsion \times x_i}{J}$$



Stress from out-of-plane forces ($tension$, $M_x$, $M_y$):


$$v_{z,direct} = \frac{-tension}{A_w}$$

$$v_{z,Mx} = \frac{M_x y_i}{I_x}$$

$$v_{z,My} =  \frac{-M_y x_i}{I_y}$$




Sum the above terms together.

$$v_{x,total} = v_{x,direct} + v_{x,torsional}$$

$$v_{y,total} = v_{y,direct} + v_{y,torsional}$$

$$v_{z,total} = v_{z,direct} + v_{z,Mx} + v_{z,My}$$



Limitations of the elastic method:

* A key limitation of the elastic method is the assumption that no bearing surface exists. Consequently, out-of-plane moment must be resolved through the welds alone. This is done by assuming a very conservative neutral axis location that coincides with the weld group centroid, which means half of the weld fibers are put into compression to maintain equilibrium.
* The elastic method does not take into account deformation compatibility and the effect of load angle. Welds are assumed to share loads equally under direct shear. In actuality, welds oriented transversely to applied loading have up to 50% higher capacity and stiffness (but lower ductility). Transversely loaded welds tend to fracture first before longitudinal welds can reach their full strength. Refer to the steel construction manual for more guidance on this matter.
* The elastic method is conservative compared to alternative methods like the plastic method and the instant center of rotation method.



**Simplified Resultant Stress**

The AISC steel construction manual allows for a simplified approach of combining the three components above vectorially into a "resultant shear stress", then comparing this resultant with an allowable shear capacity.

$$v_{resultant} = \sqrt{v_{x,total}^2 + v_{y,total}^2 + v_{z,total}^2} \leq \phi\frac{F_{EXX}}{\sqrt{3}} \approx \phi0.6F_{EXX}$$



**Von-Mises Stress for PJP and CJP Welds**

The assumption of pure shear, and vector addition without stress transformation is convenient but not entirely accurate (but then again neither is the elastic method). For example, complete-joint-penetration (CJP) welds and partial-joint-penetration (PJP) welds does have a normal stress component. Writing out the full Von-Mises yield criterion below, notice how the $\sigma$ terms are not multiplied by 3, and thus $\sqrt{3}$ does not factor out cleanly.

$$\sigma_v = \sqrt{\frac{1}{2}[(\sigma_{xx}-\sigma_{yy})^2+(\sigma_{yy}-\sigma_{zz})^2+(\sigma_{zz}-\sigma_{xx})^2] + 3[\tau_{xy}^2+\tau_{yz}^2+\tau_{xz}^2]} \leq F_{EXX}$$

$$\sigma_v = \sqrt{\sigma_{zz}^2 + 3[\tau_{xy}^2+\tau_{yz}^2]}$$

In the case of CJPs and PJPs, the Von-Mises criterion can simply be expressed as a function of global stress terms without any coordinate transformation.

$$\sigma_v = \sqrt{v_{z, total}^2 + 3[v_{x, total}^2+v_{y, total}^2]} \leq \phi F_{EXX}$$



**Von-Mises Stress for Fillet Welds**

In the case of CJPs and PJPs, we did not need to define a local coordinate system because the global vertical axis (Z) always corresponds with the normal stress vector. For the in-plane shear stresses, regardless our basis, the resultant magnitude ($\tau_{xy}^2 + \tau_{yz}^2$) is always the same. 

In the case of fillet welds, this is no longer sufficient and we must established a local coordinate system to map global stress to a local stress. 

$$\{ v_{x},  v_{y} , v_{z} \} \rightarrow \{ \sigma_{\perp},  \tau_{\parallel} , \tau_{\perp} \}$$

<div align="center">
  <img src="https://github.com/wcfrobert/ezweld/blob/master/doc/weld_coord.png?raw=true" alt="demo" style="width: 60%;" />
</div>

<div align="center">
  <img src="https://github.com/wcfrobert/ezweld/blob/master/doc/fillet_coord.png?raw=true" alt="demo" style="width: 50%;" />
</div>

A fillet weld actually has three failure planes, and we typically assume failure to occur along the inclined "throat" of the weld. Therefore, we should establish a local coordinate system with a 45 degree rotated basis. Refer to this [Engineering Stack Exchange post](https://engineering.stackexchange.com/questions/37181/why-is-fillet-weld-assumed-to-be-in-a-state-of-pure-shear-stress) for more info.

The longitudinal axis **(x')** is established by the start and end point of the weld line defined by the user.

$$u_{start}=\{x_i,y_i,0\}, \:  u_{end}=\{x_i,y_i,0\}$$

$$e_x =\frac{u_{end} - u_{start}}{||u_{end} - u_{start}||} $$

Then we let the transverse axis **(z')** be exactly aligned with Z, which points upward.

$$e_z=\{0,0,1 \}$$

The last local axis **(y')** is determined via a cross product. Notice we crossed z' with x' to respect the right-hand rule.

$$e_y = \frac{e_z \times e_x}{||e_z \times e_x||} $$

Now we can define a geometric transformation matrix very similar to what we use for stiffness matrices in structural analysis.

$$[T] = \begin{bmatrix} e_x \\ e_y \\ e_z \\ \end{bmatrix}\\$$

$$\{ \sigma_{\perp},  \tau_{\parallel} , \tau_{\perp}\} = [T] \{ v_{x},  v_{y} , v_{z} \}$$

After we have performed the coordinate transformation, we can finally calculate the Von-Mises criterion for fillet welds:

$$\sigma_v = \sqrt{\sigma_{transverse}^2 + 3[\tau_{parallel}^2+\tau_{transverse}^2]} \leq \phi F_{EXX}$$



## Assumptions and Limitations

- Sign convention follows the right-hand rule. right is +X, top is +Y, out-of-page is +Z
- EZweld is unit-agnostic. You can either use [kip, in] or [N, mm] as long as you are consistent.
- The combined stress formula is only valid when applied about a weld group's principal orientation. EZweld will warn the user if a weld group needs to be rotated. The applied moment should also be resolved to its principal components.
- Be careful when specifying negative out-of-plane axial force (i.e. compression). For fillet welds, compression is typically transferred through other mechanisms like bearing rather than through the weld itself. To encourage more deliberation on the part of the user, "Vz" was renamed to "tension". 




## License

MIT License

Copyright (c) 2024 Robert Wang