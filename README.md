# Particle System Generator
## Table of contents

1. [Introduction](#1-Introduction)
2. [Working principle of particle system generator](#2-Working-principle-of-particle-system-generator)<br>
    2.1. [Representation of the irregular shape particles](#21-representation-of-the-irregular-shape-particles)<br>
    2.2. [Particle shape parameters](#22-particle-shape-parameters)<br>
    2.3. [Direct and inverse calculation problems](#23-direct-and-inverse-calculation-problems)<br>
    2.4. [General algorithm for particles generation](#24-general-algorithm-for-particles-generation)
3. [Description of the software](#3-description-of-the-software)
4. [Used technologies](#4-used-technologies)
5. [Documentation](#5-documentation)
6. [Installation guide](#6-installation-guide)
7. [Examples of render capabilities of generated particle systems](#7-examples-of-render-capabilities-of-generated-particle-systems)<br>
    7.1. [Different number of particles per single picture](#71-different-number-of-particles-per-single-picture)<br>
    7.2. [Different picture scales](#72-different-picture-scales)<br>
    7.3. [Different picture colors](#73-different-picture-colors)<br>
    7.4. [Different particle blurs](#74-different-particle-blurs)<br>
    7.5. [Particles overlap simulation](#75-particles-overlap-simulation)<br>
    7.6. [Scale drawing option](#76-scale-drawing-option)
8. [Licence](#8-licence)

## 1. Introduction
One of the problems faced by developers of systems for recognition of particles (their sizes and shapes) is the difficulty in assessing the quality of such recognition. The system, which is always able to give the final result, cannot determine how close it is to reality, since information about the system of tested particles is not known in advance. One obvious solution to the problem is to calibrate the system (and adjust recognition algorithms) on some reference material, and then use the calibrated system to recognize particles of the real material.<br>

The creation of reference materials with, for example, spherical particles of medium size can be solved and quite often is already used to test the behavior of systems that make particle recognition. But such task becomes significantly complicated when it is necessary to create spherical particles of micron-level size, or when it is necessary to obtain a mixture from many particles, where the shape parameters would be distributed according to a known law. If it is necessary to create particles of irregular shape, and even so that the shape parameters would be distributed according to a law known in advance, then the task becomes practically impossible. Therefore, to test algorithms for the recognition of particles of irregular shapes, it is necessary to use other approaches, one of which is, for instance, the creation of artificial pictures with the particle size and shape distributions as we need.

<p align="center">
<img src="/Images for GitHub/Fig 01. Idea of particle system generation.png" alt="Idea of particle system generation" width=788px>
</p>

**Fig.1.** Graphical representation of the idea of creation of pictures with generated particle system.

Developed application with graphical user interface (GUI) is trying to solve the problem. It is designed to create pictures with artificially generated 2D particles. An important feature of such particle generation is that particles are generated in accordance with desired and predefined distribution of sizes and shape parameters (PSD, Circularity, Convexity and Elongation).

## 2. Working principle of particle system generator
### 2.1. Representation of the irregular shape particles 

Thw work of the particle system generator is based on the method that has been chosen to represent 2D irregular shape particles. Circular (ans spherical) particle can be easily represented only with a single parameter – circular equivalent (CE) diameter. However, a particle of irregular shape can no longer be described by one parameter. There are many ways of describing an irregular shape, one of which is to use radius vectors that deviate from each other at the same angle, as shown in Figure 2. With this approach, any irregular particle shape can be represented by a set of radiuses Ri. It is important to note that increasing the number of radius vectors increases the accuracy of describing the particle shape.

<p align="center">
<img src="/Images for GitHub/Fig 02. Representation of the irregular shape particle.png" alt="Representation of the irregular shape particle" width=534px>
</p>

**Fig.2.** Example of the description of spherical particle with only one parameter and the irregular shape particle with set of radius vectors.

For convenience, the values of the radius vectors lengths can be normalized. Therefore, any irregular particle shape can be described by the following set of n values.

<p align="center">
<img src="/Images for GitHub/Eq 01. Equation for description of the particle.png" alt="Equation for description of the particle" width=346px>
</p>

### 2.2. Particle shape parameters

Having values of radius vectors that describe the irregular shape (and therefore the coordinates of each vertex of the polygon), it is possible to determine different particle shape parameters: (1) coordinates of centre of mass; (2) major and minor axis; (3) length; (4) width; (5) aspect ratio; (6) elongation; (7) area; (8) CE diameter; (9) SE volume; (10) perimeter; (11) circularity; (12) HS circularity; (13) convex hull coordinates; (14) convex hull perimeter; (15) convexity; (16) area enclosed by convex hull; (17) solidity. Many of the listed parameters are calculated on the basis of the other parameters, so it is possible to see a certain hierarchy of calculation, which is presented in Figure 3. In the figure, the main characteristics of the particle shape are marked in blue. It is also important to note that for a system consisting of many different particles, the listed parameters have a certain distribution.<br>

<p align="center">
<img src="/Images for GitHub/Fig 03. Flowchart of the particle parameters calculation.png" alt="Flowchart of the particle parameters calculation" width=791px>
</p>

### 2.3. Direct and inverse calculation problems

The direct problem is calculation of the parameters of irregular particle which shape is set by the coordinates of radius vectors:

<p align="center">
<img src="/Images for GitHub/Eq 02. Equation for the direct problem.png" alt="Equation for the direct problem" width=340px>
</p>

where S is shape parameters; x_A is CE diameter, [μm]; C is circularity, [-]; C_c is convexity, [-]; E is elongation, [-]; R_i is length of radius vectors as it was shown in previous chapters, [-]; f represents the calculation algorithm.

The meaning of the inverse problem is to find an irregular particle shape (in other words, values R_i of radius vectors), which calculated parameters will exactly coincide with the desired ones. 

<p align="center">
<img src="/Images for GitHub/Eq 03. Equation for the reverse problem.png" alt="Equation for the reverse problem" width=397px>
</p>

The solution of the inverse problem has some features that distinguish it from the solution of the direct problem: (1) nontriviality of the solution; (2) existance of many possible solutions; (3) approximation of the solution. For solving the inverse problem the class of the evolutionary algorithms is well suited, when each next iteration relies on the information obtained prior to this step or at the current step and on the search target. Examples of such algorithms are: (1) Particle swarm optimization (PSO); (2) Genetic algorithm; (3) Ant algorithm; (4) Artificial immune system algorithm; (5) Gradient decay algorithm and others. The current version of the application take into consideration PSO algorithm only.

### 2.4. General algorithm for particles generation

The general algorithm for solving the inverse problem and finding the particle shape according to the specified input shape parameters can be illustrated on Figure 4.

<p align="center">
<img src="/Images for GitHub/Fig 04. General algorithm for solving the reverse problem.png" alt="General algorithm for solving the reverse problem" width=566px>
</p>

After input shape parameters setting (step 1) and initial particle shape guess, as random shape (step 2) the shape parameters are calculated (step 3). After that the error e as an Euclidian distance between the vector of input parameters S_in and calculated parameters S can be determined (step 4). This error, as well as the iteration count is used then do determine whether the search algorithm is finished or not (step 5). In case when current iteration count i is greater than maximum iteration number i_max, or when the error e is lower than error limit ε the searching is terminated. If the search is continuing the next step (step 6) is adjusting the particle shape by any rule. In our case the rule is obeys the PSO algorithm. When the search is finished (step 7) the output of the algorithm is the set of radius vectors R_out represented the shape of the particle whose parameters are the same as the initial ones.

## 3. Description of the software

The main task of the particle system generator is the generation of artificial pictures with particles which distributions of shape parameters are known in advance. For convenience, the application is functionally divided into 4 parts (tools), each of which provides a part of the functionality, either to work out any specific algorithms or directly to generate the final pictures. Table 1 provides information on the developed tools with the necessary explanations. Figures 5 - 10 demonstrates the GUIs of the application tools.

**Table 1.** Tools of the developed particle system generator.

| № | Name of the tool | Additional information |
|---|---|---|
| 1 | Particle tester tool | Using for test of the different algorithms of determination of irregular shape parameters such as circularity, convexity, elongation and others. |
| 2 | Particle finder tool | Provides functionality of the search algorithm (Particle swart optimization) for searching the particle shape with the desired shape parameters. The algorithm is solving so called the reverse problem. |
| 3 | Particles generator tool | Using the functionality of the first two tools this tool is able to generate the desired amount of irregular shape particles which distributions of shape parameters if known in advance. |
| 4 | Pictures render tool | Using the data about particles generated with particle generated tool, this tool is able to render the set of final pictures with desired size, scale, colors and blur. |

<p align="center">
<img src="/Images for GitHub/Fig 05. MainWindow.png" alt="MainWindow interface" width=414px>
</p>

**Fig.5.** Main window of the particles system generator with set of tools.

<p align="center">
<img src="/Images for GitHub/Fig 06. ParticleTester interface.png" alt="ParticleTester interface" width=743px>
</p>

**Fig.6.** Window of the particle tester tool.

<p align="center">
<img src="/Images for GitHub/Fig 07. Real particle image loader.png" alt="Real particle image loader" width=869px>
</p>

**Fig.7.** Window of the real particle image loader of the particle tester tool.

<p align="center">
<img src="/Images for GitHub/Fig 08. ParticleFinder interface.png" alt="ParticleFinder interface" width=1034px>
</p>

**Fig.8.** Window of the particle finder tool.

<p align="center">
<img src="/Images for GitHub/Fig 09. ParticlesGenerator interface.png" alt="ParticlesGenerator interface" width=588px>
</p>

**Fig.9.** Window of the particle system generator tool.

<p align="center">
<img src="/Images for GitHub/Fig 10. PicturesRender interface.png" alt="PicturesRender interface" width=588px>
</p>

**Fig.10.** Window of the pictures render tool.

## 4. Used technologies

The application was developed mainly using Python 3.7.The most important libraries used for creating the functionality of the application are the fillowing: PyQt5, Matplotlib, Numpy, Openpyxl, Pillow. The modules that requires to produce heavy calculations were written in C. 

## 5. Documentation

Documentation for every tool can be found in _Help_ folder as a set of pdf files. Documentation for each specific tool can be opened using the menu: _Info_ -> _Help_.

## 6. Installation guide

To install and succesfully run the program the following should be done (assuming that application is installed in D:\Projects\Particle_System_Generator):

- Install MSYS2, gcc:
https://www.msys2.org/
- Compile some modules for particles generator:
```
$ git clone https://github.com/juvus/Particle_System_Generator.git
$ cd D:\Projects\Particle_System_Generator\Modules\Generator_c
$ mingw32-make
```
- Install anaconda environment
https://www.anaconda.com/products/individual
- Create prts_sys_gen virtual environment:
```
$ conda create --name prts_sys_gen
```
- Activate the environment:
```
$ conda activate prts_sys_gen
```
- Change directory to that with program code
```
$ cd D:\Projects\Particle_System_Generator 
```
- Install the python (3.7 version)
```
$ conda install python=3.7
```
- Install the required libraries (listed in file requirements.txt)
```
$ pip install -r requirements.txt
```
- Run the software
```
$ python Run.py
```

## 7. Examples of render capabilities of generated particle systems

During the development of the particles system generator software, a separation in functionality was made between the particles generation and it’s rendering so that already generated particle data (generation of particles may take considerable time especially when a huge number of particles are generated) can be used in multiple renders of such pictures that are needed at the current moment. Rendering of pictures takes significantly less time than generation a particles system.<br>

Using render settings the pictures render tool has many opportunities to render exactly those pictures that we need. Various possible options with examples are presented below.

### 7.1. Different number of particles per single picture

<p align="center">
<img src="/Images for GitHub/Fig 11. Render. Different particles number per single picture.png" alt="Render. Different particles number per single picture" width=755px>
</p>

**Fig.11.** Example of different particles number per single rendered picture. A –100 part.; B - 500 part., C – 1000 part.

### 7.2. Different picture scales

<p align="center">
<img src="/Images for GitHub/Fig 12. Render. Different picture scales.png" alt="Render. Different picture scales" width=757px>
</p>

**Fig.12.** Example of pictures that contain 500 particles in different scales. A – 0.1 μm/pix; B – 0.2 μm/pix, C – 0.4 μm/pix

### 7.3. Different picture colors

<p align="center">
<img src="/Images for GitHub/Fig 13. Render. Different picture colors.png" alt="Render. Different picture colors" width=765px>
</p>

**Fig.13.** Example of pictures with different colors of background and particles.

### 7.4. Different particle blurs

<p align="center">
<img src="/Images for GitHub/Fig 14. Render. Different particle blurs.png" alt="Render. Different particle blurs" width=757px>
</p>

**Fig.14.** Example of pictures with different particles blur. A – blur particles 0%, blur value 0%; B – blur particles 50%, blur value 50%; C – blur particles 100%, blur value 100%.

### 7.5. Particles overlap simulation

<p align="center">
<img src="/Images for GitHub/Fig 15. Render. Particles overlap simulation.png" alt="Render. Particles overlap simulation" width=510px>
</p>

**Fig.15.** Example of pictures with disabled (A) and enabled (B) option of particles overlap.

### 7.6. Scale drawing option

<p align="center">
<img src="/Images for GitHub/Fig 16. Render. Scale drawing option.png" alt="Render. Scale drawing option" width=693px>
</p>

**Fig.16.** Example of pictures without the scale in the bottom (A) and with the scale (B). Enlarged part with the scale is shown in (C). The solidity here is a ratio between area occupied by particles and area of the picture (on pix or μm).

## 8. Licence
Particle system generator application code in this project is available under the `GPLv3` license. You can find the license file here: [LICENSE](/LICENSE)
