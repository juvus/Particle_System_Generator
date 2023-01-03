# Particle System Generator
## Table of contents

1. [Introduction](#1-Introduction)
2. [Working principle of particle system generator](#2-Working-principle-of-particle-system-generator)
3. [Description of the software](#3-description-of-the-software)

## 1. Introduction
One of the problems faced by developers of systems for recognition of particles (their sizes and shapes) is the difficulty in assessing the quality of such recognition. The system, which is always able to give the final result, cannot determine how close it is to reality, since information about the system of tested particles is not known in advance. One obvious solution to the problem is to calibrate the system (and adjust recognition algorithms) on some reference material, and then use the calibrated system to recognize particles of the real material.<br>

The creation of reference materials with, for example, spherical particles of medium size can be solved and quite often is already used to test the behavior of systems that make particle recognition. But such task becomes significantly complicated when it is necessary to create spherical particles of micron-level size, or when it is necessary to obtain a mixture from many particles, where the shape parameters would be distributed according to a known law. If it is necessary to create particles of irregular shape, and even so that the shape parameters would be distributed according to a law known in advance, then the task becomes practically impossible. Therefore, to test algorithms for the recognition of particles of irregular shapes, it is necessary to use other approaches, one of which is, for instance, the creation of artificial images with the particle size and shape distributions as we need.

<img src="/Images for GitHub/Fig 01. Idea of particle system generation.png" alt="Idea of particle system generation" width=100%>

**Fig.1.** Graphical representation of the idea of creation of images with generated particle system.

Developed application with graphical user interface (GUI) is trying to solve the problem. It is designed to create images with artificially generated 2D particles. An important feature of such particle generation is that particles are generated in accordance with desired and predefined distribution of sizes and shape parameters (PSD, Circularity, Convexity and Elongation).

## 2. Working principle of particle system generator
### 2.1. Representation of the irregular shape particles 

Thw work of the particle system generator is based on the method that has been chosen to represent 2D irregular shape particles. Circular (ans spherical) particle can be easily represented only with a single parameter – circular equivalent (CE) diameter. However, a particle of irregular shape can no longer be described by one parameter. There are many ways of describing an irregular shape, one of which is to use radius vectors that deviate from each other at the same angle, as shown in Figure 2. With this approach, any irregular particle shape can be represented by a set of radiuses Ri. It is important to note that increasing the number of radius vectors increases the accuracy of describing the particle shape.

<img src="/Images for GitHub/Fig 02. Representation of the irregular shape particle.png" alt="Representation of the irregular shape particle" width=100%>

**Fig.2.** Example of the description of spherical particle with only one parameter and the irregular shape particle with set of radius vectors.

For convenience, the values of the radius vectors lengths can be normalized. Therefore, any irregular particle shape can be described by the following set of n values.

<img src="/Images for GitHub/Eq 01. Equation for description of the particle.png" alt="Equation for description of the particle" width=100%>

### 2.2. Particle shape parameters

Having values of radius vectors that describe the irregular shape (and therefore the coordinates of each vertex of the polygon), it is possible to determine different particle shape parameters: (1) 





Имея значение радиус-векторов, описывающих irregular shape (и, поэтому координаты каждой вершины многоугольника), можно определить множество различных параметров формы: . Важно отметить, что для системы, состоящей из множества различных частиц, перечисленные параметры имеют некторое распределение. 

<br>

Many of the parameters listed above are calculated on the basis of the other parameters, so it is possible to see a certain hierarchy of calculation, which is presented in Figure 2. In the figure, the main characteristics of the particle shape are marked in blue.


Главными параметрами являются






Основная идея, лежащая в основе работы генератора - представление нерегулярной формы двумерной частицы в виде набора (массива) радиус-векторов.


## 3. Description of the software

## 4. Used technologies

## 5. Documentstion

## 6. Install from source

## 7. Project Organization


## 8. Plans for the application development

## 9. Licence
Traffic light simulator code in this project is available under the `GPLv3` license. You can find the license file here: [LICENSE](/LICENSE)