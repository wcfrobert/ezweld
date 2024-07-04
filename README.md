<h1 align="center">
  <br>
  <img src="https://github.com/wcfrobert/ezweld/blob/master/doc/logo.png?raw=true" alt="logo" style="width: 60%;" />
  <br>
  Weld Stress Calculation in Python (WORK IN PROGRESS)
  <br>
</h1>



<div align="center">
  <img src="https://github.com/wcfrobert/ezweld/blob/master/doc/demo.gif?raw=true" alt="demo" style="width: 75%;" />
</div>



- [Quick Start](#quick-start)
- [Installation](#installation)
- [Usage](#usage)
- [Theoretical Background](#theoretical-background)
- [Assumptions and Limitations](#assumptions-and-limitations)
- [License](#license)




## Quick Start

Run main.py:

```python
import ezweld

# initialize a weld group
weld_group = ezweld.weldgroup.WeldGroup()

# draw welds
weld_group.add_line(start=[0,0], end=[0,10], segments=20, size=5/16)
weld_group.add_line(start=[0,0], end=[10,10], segments=20, size=5/16)

# preview geometry
weld_group.preview()

# calculate stresses using the elastic method
results = weld_group.solve(Vx=0, Vy=100, tension=0, Mx=1000, My=0, torsion=0)

# plot weld stress
weld_group.plot_results()
```

Sign convention shown below:

<div align="center">
  <img src="https://github.com/wcfrobert/ezweld/blob/master/doc/weld_dof.png?raw=true" alt="demo" style="width: 60%;" />
</div>
`weld_group.preview()` returns a matplotlib figure showing what the weld group looks like and its geometric properties.



`weld_group.plot_results()` returns a plotly figure.



`weld_group.solve()` returns the following dictionary:







## Installation

**Option 1: Anaconda Python**

Run main.py using your base Anaconda environment. 

1. Download Anaconda python
2. Download this package (click the green "Code" button and download zip file)
3. Open and run "main.py" in Anaconda's Spyder IDE.

The following packages are used:

* Numpy
* Pandas
* Matplotlib
* Plotly


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

Pip install is also available.

```
pip install ezweld
```



## Usage

Here are all the public methods available to the user:

**Defining Weld Group**

* `ezweld.weldgroup.WeldGroup.add_line(start, end, segments, thickness)`
* `ezweld.weldgroup.WeldGroup.add_rectangle(xo, yo, width, height, xsegments, ysegments, thickness)`
* `ezweld.weldgroup.WeldGroup.add_circle(xo, yo, diameter, segments, thickness)`
* `ezweld.weldgroup.WeldGroup.rotate(angle)`

**Solving**

* `ezweld.weldgroup.WeldGroup.solve(Vx=0, Vy=0, tension=0, Mx=0, My=0, torsion=0)`

**Visualizations**

* `ezweld.weldgroup.WeldGroup.preview()`
* `ezweld.weldgroup.WeldGroup.plot_results()`

For more guidance and documentation, you can access the docstring of any method using the help() command. 

For example, here's the output from `help(ezweld.weldgroup.WeldGroup.add_line)`

<div align="center">
  <img src="https://github.com/wcfrobert/ezweld/blob/master/doc/docstring.png?raw=true" alt="demo" style="width: 80%;" />
</div>



## Theoretical Background

**Section Analogy**

Welds transfer forces between two connected members. At the plane of connection, we can think of the weld as the member itself; having its own geometric properties. With this assumption in mind, finding the stress state of a weld group is entirely analogous to determining stress on a cross-section using the elastic stress formulas. Here is a figure from the “Design of Welded Structures” textbook by Omer W. Blodgett that illustrates this analogy.

<div align="center">
  <img src="https://github.com/wcfrobert/ezweld/blob/master/doc/weld_comparison.png?raw=true" alt="demo" style="width: 50%;" />
</div>
First, we need to calculate the weld group's geometric properties. EZweld does so by discretizing the weld group into little patches then applying the parallel axis theorem.

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



**Force/Length Convention - Treating Welds as Lines**

In the structural engineering context, welds are often thought of as 1-dimensional "lines". As such, results are often expressed as **force per unit length** (e.g. kip/in) rather than force per unit area (e.g. ksi). But why introduce another layer of abstraction when the above section property formulas are perfectly fine? 

Quoting Omer W. Blodgett's in his textbook first published in 1966. Chapter 2.2-8:

> "[*On the line approximation for determining section properties*] With a thin section, the inside dimension is almost as large as the outside dimension; and, in most cases, the property of the section varies as the cubes of these two dimensions. This means dealing with the difference between two very large numbers. In order to get any accuracy, **it would be necessary to calculate this out by longhand or by using logarithms rather than use the usual slide rule** [*emphasis mine*]. To simplify the problem, the section may be treated as a line, having no thickness."

In Chapter 7.4-7, Blodgett presents two other reasons for treating welds as lines.

* With the line method, geometric properties, as well as demands can be calculated without specifying a thickness upfront. This is convenient from a workflow perspective because engineers can now calculate a demand, then specify a thickness afterwards. In the pre-calculator era when engineering calculations are not automated, change in the input parameter could mean revising pages of calculation by hand.
* Stress transformation and combination is complicated and burdensome to do by hand. The "force per unit length" convention is a design simplification that circumvents the thorny problem of stress transformations and change of basis.

Here a table from the Omer W. Blodgett textbook that provides equations for common weld group geometric properties (1 dimensions less):

<div align="center">
  <img src="https://github.com/wcfrobert/ezweld/blob/master/doc/weld_properties.png?raw=true" alt="demo" style="width: 60%;" />
</div>
Here are the exact same formulas as the previous section with one dimension less (t = unity):

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

An important limitation of the line method is that it assumes uniform thickness within a weld group. The above table should NOT be used for **weld groups with variable thicknesses.** In the rare case that a weld group has variable thickness, first calculate an "effective" length in proportional with the minimum thickness within the weld group, then use this modified length instead in the equations above.

$$L_{effective} = \frac{t}{t_{min}} \times L_i$$

It is quite easy to convert between the two conventions if you have uniform thickness:

$$(ksi) = \frac{(k/in)}{t_{weld}}$$

$$(in^4) = (in^3)\times t_{weld}$$



**Weld Stress Via Elastic Method**

A weld group may be subjected to loading in all 6 degrees of freedom. These applied loads are then translated into stresses using the geometric properties above and the elastic stress formulas below. 



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




Sum the above terms together. Depending on the conventions used, these terms are either expressed as (force/length) or (force/area). 

$$v_{x,total} = v_{x,direct} + v_{x,torsional}$$

$$v_{y,total} = v_{y,direct} + v_{y,torsional}$$

$$v_{z,total} = v_{z,direct} + v_{z,Mx} + v_{z,My}$$

The three terms above are then combined into a single value then compared to a design capacity. In the next two sections, $\tau$ will be used for stress, $v$ will be used for unit force.



**Resultant Unit Force - Simplified Approach**

Using the "weld-as-line" convention (force/length), the three components above are simply added vectorially into a resultant shear force, then compared with an allowable shear capacity. 

$$v_{resultant} = \sqrt{v_{x,total}^2 + v_{y,total}^2 + v_{z,total}^2} \leq \phi\frac{F_{EXX}}{\sqrt{3}}t_{weld} \approx \phi0.6F_{EXX}t_{weld}$$



**Resultant Stress - Von-Mises Yield Criterion**

The assumption of pure shear, and vector addition without stress transformation is convenient but not accurate (but then again neither is the elastic method). For example, complete-joint-penetration (CJP) welds and partial-joint-penetration (PJP) welds do have a normal stress component. Writing out the full Von-Mises yield criterion below, notice how the $\sigma$ term is not multiplied by 3, and thus $\sqrt{3}$ does not factor out cleanly. 

$$\sigma_v = \sqrt{\frac{1}{2}[(\sigma_{xx}-\sigma_{yy})^2+(\sigma_{yy}-\sigma_{zz})^2+(\sigma_{zz}-\sigma_{xx})^2] + 3[\tau_{xy}^2+\tau_{yz}^2+\tau_{xz}^2]} \leq F_{EXX}$$

$$\sigma_v = \sqrt{\sigma_{zz}^2 + 3[\tau_{xy}^2+\tau_{yz}^2]}$$



In the case PJPs, the Von-Mises stress can be expressed as a function of global stress terms without any coordinate transformation. The global vertical axis (Z) always corresponds with the normal stress vector, and magnitude of the in-plane resultant ($\tau_{xy}^2 + \tau_{yz}^2$) is always the same regardless coordinate system. Therefore, the Von-Mises criterion for PJPs is expressed as:

$$\sigma_v = \sqrt{\tau_{z, total}^2 + 3[\tau_{x, total}^2+\tau_{y, total}^2]} \leq \phi F_{EXX}$$



In the case of fillet welds, we must first established a local coordinate system to map global stress to a local stress. 

```math
\{ \tau_{x},  \tau_{y} , \tau_{z} \} \rightarrow \{ \sigma_{\perp},  \tau_{\parallel} , \tau_{\perp} \}
```


<div align="center">
  <img src="https://github.com/wcfrobert/ezweld/blob/master/doc/weld_coord.png?raw=true" alt="demo" style="width: 60%;" />
</div>
<div align="center">
  <img src="https://github.com/wcfrobert/ezweld/blob/master/doc/fillet_coord.png?raw=true" alt="demo" style="width: 40%;" />
</div>


A fillet weld actually has three failure planes, and we typically assume failure to occur along the inclined throat of the weld. Therefore, the local coordinate system must also be rotated 45 degrees. Refer to this [Engineering Stack Exchange post](https://engineering.stackexchange.com/questions/37181/why-is-fillet-weld-assumed-to-be-in-a-state-of-pure-shear-stress) for more info. Let's first establish the necessary transformation matrix for each patch of weld.

First, the longitudinal basis vector **(x')** is established by the start and end point of the weld line defined by the user.

```math
u_{start}=\{x_i,y_i,0\}, \:  u_{end}=\{x_i,y_i,0\}
```

$$e_x =\frac{u_{end} - u_{start}}{||u_{end} - u_{start}||} $$


Then we let one of the transverse basis vector **(z')** be exactly aligned with Z, which points upward.

```math
e_z=\{0,0,1 \}
```

The last basis **(y')** is determined via a cross product. Notice how we crossed z' with x' to align with the right-hand axis convention.

$$e_y = \frac{e_z \times e_x}{||e_z \times e_x||} $$

Now we can define a 3x3 geometric transformation matrix.

$$ [T] = [e_x, e_y, e_z]$$

In addition, we want to apply a negative 45 degree rotation about the x-axis:

$$
[T_{-45}] = \begin{bmatrix}
1 & 0 & 0\\ 
0 & cos(-45) & -sin(-45)\\ 
0 & sin(-45) & cos(-45)\end{bmatrix}
$$

Rotating a stress vector is inconvenient because the associated dA must also be rotated, but notice that we are not looking at an infinitesimally small cube yet, evaluation of the fillet geometry is still a macro level exercise. For a unit strip of fillet weld, apply two successive transformations to get the unit force expressed in the local coordinate system.

```math
\{ v_{\perp},  v_{\parallel} , v_{\perp}\} = [T_{45}][T] \{ v_{x},  v_{y} , v_{z} \}
```

Then divide by the thickness to get stress:

$$\tau = v/t_{throat}$$

Now that we are on this inclined plane, we can apply the stress transformation equations, but that's unnecessary because the Von-Mises criterion for fillet can already to calculated.

$$\sigma_v = \sqrt{\sigma_{\perp}^2 + 3[\tau_{\parallel}^2+\tau_{\perp}^2]} \leq \phi F_{EXX}$$





## Assumptions and Limitations

- Sign convention follows the right-hand convention. right is +X, top is +Y, out-of-page is +Z

- EZweld is unit-agnostic. You can either use [kip, in] or [N, mm] as long as you are consistent.

- Be careful when specifying negative out-of-plane axial force. Compression is often transferred through other mechanisms like bearing rather than through the weld itself.

- The combined stress formula is only valid when applied about a weld group's principal orientation. EZweld will warn the user if a weld group needs to be rotated. In addition, the applied moment must be resolved to its principal components.

  <div align="center">
    <img src="https://github.com/wcfrobert/ezweld/blob/master/doc/weld_principal_axes.png?raw=true" alt="demo" style="width: 40%;" />
  </div>

  A weld group is in its principal orientation if the product of inertia is equal to zero:

  $$I_{xy} = 0$$

  Otherwise, the weld group must be rotated by the following angle.

  $$\theta_p = 0.5\times tan^{-1}(\frac{I_{xy}}{I_x - I_y})$$

* A key limitation of the elastic method is the assumption that no bearing surface exists. Consequently, out-of-plane moment must be resolved through the welds alone. This is done by assuming a very conservative neutral axis location that coincides with the weld group centroid, which means half of the weld fibers are put into compression to maintain equilibrium.
* The elastic method does not take into account deformation compatibility and the effect of load angle. Welds are assumed to share loads equally under direct shear. In actuality, welds oriented transversely to applied loading have up to 50% higher capacity and stiffness (but lower ductility). Refer to the steel construction manual for more guidance on this matter.



## License

MIT License

Copyright (c) 2024 Robert Wang



**Disclaimer:** this package is meant for personal and educational use only