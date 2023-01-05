# Particle System Generator
## Table of contents

1. [Introduction](#1-Introduction)
2. [Working principle of particle system generator](#2-Working-principle-of-particle-system-generator)
3. [Description of the software](#3-description-of-the-software)

## 1. Introduction
One of the problems faced by developers of systems for recognition of particles (their sizes and shapes) is the difficulty in assessing the quality of such recognition. The system, which is always able to give the final result, cannot determine how close it is to reality, since information about the system of tested particles is not known in advance. One obvious solution to the problem is to calibrate the system (and adjust recognition algorithms) on some reference material, and then use the calibrated system to recognize particles of the real material.<br>

The creation of reference materials with, for example, spherical particles of medium size can be solved and quite often is already used to test the behavior of systems that make particle recognition. But such task becomes significantly complicated when it is necessary to create spherical particles of micron-level size, or when it is necessary to obtain a mixture from many particles, where the shape parameters would be distributed according to a known law. If it is necessary to create particles of irregular shape, and even so that the shape parameters would be distributed according to a law known in advance, then the task becomes practically impossible. Therefore, to test algorithms for the recognition of particles of irregular shapes, it is necessary to use other approaches, one of which is, for instance, the creation of artificial images with the particle size and shape distributions as we need.

<p align="center">
<img src="/Images for GitHub/Fig 01. Idea of particle system generation.png" alt="Idea of particle system generation" width=788px>
</p>

**Fig.1.** Graphical representation of the idea of creation of images with generated particle system.

Developed application with graphical user interface (GUI) is trying to solve the problem. It is designed to create images with artificially generated 2D particles. An important feature of such particle generation is that particles are generated in accordance with desired and predefined distribution of sizes and shape parameters (PSD, Circularity, Convexity and Elongation).

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

The main task of the particle system generator is the generation of artificial images with particles which distributions of shape parameters are known in advance. For convenience, the application is functionally divided into 4 parts (tools), each of which provides a part of the functionality, either to work out any specific algorithms or directly to generate the final images. Table 1 provides information on the developed tools with the necessary explanations. Figures 5 - 9 demonstrates the GUIs of the application tools.

**Table 1.** Tools of the developed particle system generator.

| № | Name of the tool | Name of the tool |
|---|---|---|
| 1 | Particle tester tool | Using for test of the different algorithms of determination of irregular shape parameters such as circularity, convexity, elongation and others. |
| 2 | Particle finder tool | Provides functionality of the search algorithm (Particle swart optimization) for searching the particle shape with the desired shape parameters. The algorithm is solving so called the reverse problem. |
| 3 | Particles generator tool | Using the functionality of the first two tools this tool is able to generate the desired amount of irregular shape particles which distributions of shape parameters if known in advance. |
| 4 | Pictures render tool | Using the data about particles generated with particle generated tool, this tool is able to render the set of final pictures with desired size, scale, colors and blur. |












## 4. Used technologies

The application was developed mainly using Python 3.7. Table 2 contains the most important libraries used for creating the functionality of the application. The modules that requires to produce heavy calculations was written in C. 

## 5. Documentstion

## 6. Install from source





## 7. Examples of render capabilities of generated particle systems







## 8. Plans for the application development

## 9. Licence
Traffic light simulator code in this project is available under the `GPLv3` license. You can find the license file here: [LICENSE](/LICENSE)