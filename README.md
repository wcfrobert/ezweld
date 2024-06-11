<h1 align="center">
  <br>
  <img src="https://github.com/wcfrobert/ezweld/blob/master/doc/logo.png?raw=true" alt="logo" style="width: 60%;" />
  <br>
  Weld Stress Calculations in Python
  <br>
</h1>

<div align="center">
  <img src="https://github.com/wcfrobert/ezweld/blob/master/doc/demo.gif?raw=true" alt="demo" style="width: 75%;" />
</div>




## Introduction

EZweld is a python package that calculates stresses within a weld group subjected to both in-plane and out-of-plane forces. It does so using the elastic method as outlined in the AISC Steel Construction Manual. Define a weld group, apply loading, and get the resulting stresses back. It's that easy!


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
results = weld_group.solve(Vx=0, Vy=0, tension=0, Mx=0, My=0, torsion=0)

# plot weld stress
weld_group.plot_results()


```


## Installation

**Option 1: Anaconda Python**

Simply run main.py using your base Anaconda environment. The following packages are used:

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

WORK IN PROGRESS




## Theoretical Background - Determining Weld Stress Via Elastic Method

<u>Geometric Properties</u>

A weld group can be treated like any other geometric section. As such, calculating its stress state is entirely analogous to calculating elastic stress on a cross-section using the combined stress formula. You'll see these equations in pretty much all mechanics of material textbooks. 

$$\sigma = \frac{P}{A} + \frac{M_x c_y}{I_x} + \frac{M_y c_x}{I_y}$$

$$\tau = \frac{Tc}{J}$$

Here is a figure from “Design of Welded Structures” textbook by Omer W. Blodgett that illustrates this similarity nicely.

<div align="center">
  <img src="https://github.com/wcfrobert/ezweld/blob/master/doc/weld_comparison.png?raw=true" alt="demo" style="width: 50%;" />
</div>

A weld group, like any other sections, have geometric properties that we can calculate. EZweld does so by discretizing the weld group into little patches then applying the parallel axis theorem.



Centroid:

$$x_{cg} = \frac{\sum x_iA_i}{\sum A}$$

$$y_{cg} = \frac{\sum y_iA_i}{\sum A}$$



Area:

$$A_w =  \iint dA = \sum t_i L_i$$



Moment of Inertia:

$$I_x = \iint y^2 dA= \sum y_i^2A_i$$

$$I_y = \iint x^2 dA = \sum x_i^2A_i$$

$$I_{xy} = \iint xydA = \sum x_i y_i A_i$$

$$I_z = J = I_p = I_x + I_y$$



Section modulus:

$$S_{x,top} = \frac{I_x}{c_{x1}}$$

$$S_{x2,bot} = \frac{I_x}{c_{x2}}$$

$$S_{y,left} = \frac{I_y}{c_{y1}}$$

$$S_{y,right} = \frac{I_y}{c_{y2}}$$



<u>Geometric Properties - (One Dimension Less)</u>

Structural engineers tend to work one abstraction layers up from mechanical engineers (e.g. strain vs. deformation, normal stress vs. axial+moment). In the structural engineering context, weld are typically thought of as a 1-dimensional "line". As a result, weld stresses are expressed as **force per unit length** (kip/in) rather than force per unit area (ksi). 

This is just a matter of convention. There are some benefits to working with one dimension less. For example, demands can now be calculated without knowing the weld's thickness, which means thickness becomes a design parameter that we can specify. One drawback is that having one dimension less gets kind of confusing, especially for weld groups with variable thicknesses. For weld group with variable thicknesses, the stress approach is recommended. Otherwise, we must calculate a modified length where:

$$L^* = \frac{t}{t_{min}}\times L$$

[INSERT FIGURE OF GEOMETRIC PROPERTIES]

The geometric property equations above are repeated below for one dimension less. Note we can convert between the two conventions by diving the values above by the throat thickness.

$$(ksi) = \frac{(k/in)}{t_{throat}}$$

$$(in^3) = \frac{(in^4)}{t_{throat}}$$

The geometric property equations above are repeated below for one dimension less. A easy way to think of this is to set t to unity.

$$x_{cg} = \frac{\sum x_i L^*_i}{\sum L^*}$$

$$y_{cg} = \frac{\sum y_i L^*_i}{\sum L^*}$$

$$L_w =  \iint dL = \sum L^*_i$$

$$I_x = \iint y^2 dL= \sum y_i^2 L^*_i$$

$$I_y = \iint x^2 dL = \sum x_i^2 L^*_i$$

$$I_{xy} = \iint xydL = \sum x_i y_i L^*_i$$

$$I_z = J = I_p = I_x + I_y$$

$$S_{x,top} = \frac{I_x}{c_{x1}}$$

$$S_{x2,bot} = \frac{I_x}{c_{x2}}$$

$$S_{y,left} = \frac{I_y}{c_{y1}}$$

$$S_{y,right} = \frac{I_y}{c_{y2}}$$



<u>Determining Stresses</u>

A weld group may be subjected to forces about all 6 degrees of freedom. One caveat is that axial out-of-plane force can only be positive (tension). Compressive stresses are assumed to transfer via other mechanisms (such as bearing) and is ignored by EZweld. These applied forces are translated into stresses on individual small patches of weld.

<div align="center">
  <img src="https://github.com/wcfrobert/ezweld/blob/master/doc/weld_dof.png?raw=true" alt="demo" style="width: 50%;" />
</div>

Whether a weld is subjected to tension or shear is irrelevant, all weld fail in shear along the throat length. Therefore, there is no such thing as normal stress (sigma) in weld stress calculations.

<div align="center">
  <img src="https://github.com/wcfrobert/ezweld/blob/master/doc/weld_throat.png?raw=true" alt="demo" style="width: 50%;" />
</div>





Stress from in-plane forces


$$\tau_{x,direct} = \frac{-V_x}{A}$$

$$\tau_{y,direct} = \frac{-V_y}{A}$$


$$\tau_{x,torsional} = \frac{torsion \times y_i}{J}$$

$$\tau_{y,torsional} = \frac{-torsion \times x_i}{J}$$



$$\tau_{x,total} = \tau_{x,direct} + \tau_{x,torsional}$$

$$\tau_{y,total} = \tau_{y,direct} + \tau_{y,torsional}$$



Stress from out-of-plane forces:


$$\tau_{z,direct} = \frac{tension}{A}$$

$$\tau_{z,Mx} = \frac{M_x y_i}{I_x}$$

$$\tau_{z,My} =  \frac{M_y x_i}{I_y}$$



$$\tau_{z,total} = \tau_{3,direct} + \tau_{3,Mx} + \tau_{3,My}$$



$$\tau_{resultant} = \sqrt{\tau_{x,total}^2 + \tau_{y,total}^2 + \tau_{z,total}^2}$$



The combined stress formula (i.e. P/A + M/S) is only valid when applied about a weld group's principal orientation. EZweld will warn the user if a weld group needs to be rotated. The applied moment must also be resolved to its principal components. A weld group orientation is in its principal state if:

$$I_{xy} = 0$$

Otherwise, the weld group must be rotated by:

$$\theta_p = 0.5\times tan^{-1}(\frac{I_{xy}}{I_x - I_y})$$




## Assumptions and Limitations

- Sign convention follows the right-hand rule. right is +X, top is +Y, out-of-page is +Z.
- Weld patch does not have its own local coordinate system. All stresses are expressed with respect to the global axis.
- The combined stress formula (i.e. P/A + M/S) is only valid when applied about a weld group's principal orientation. EZweld will warn the user if a weld group needs to be rotated. The applied moment must also be resolved to its principal components.
- Applying negative tension (i.e. compression) is not allowed and will be ignored by EZweld. Compressive stresses are assumed to transfer via other mechanisms (such as bearing).

- Units are in (kip, in) unless otherwise noted.




## License

MIT License

Copyright (c) 2024 Robert Wang