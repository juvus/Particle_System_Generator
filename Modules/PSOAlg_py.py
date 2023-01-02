#==========================================================================================
# Realization of the particle swarm optimization (PSO) algorithm
#==========================================================================================

import numpy as np
np.random.seed()  # Seed the generator
import math as m
from Modules.Particle import Particle

class PSOParticle():
    """Class for single particle of the algorithm"""
    def __init__(self, nVar, varMin, varMax, init_circularity, init_convexity,
                 init_elongation, particle):
        self.nVar = nVar  # Number of unknown (decision) variables (equal to nDim + realWidth)
        self.varMin = varMin  # Lower bound of decision variables
        self.varMax = varMax  # Upper bound of decision variables
        self.init_circularity = init_circularity
        self.init_convexity = init_convexity
        self.init_elongation = init_elongation
        self.imgScale = 1.0  # Image scale (during the search it is constant)
        self.position = None  # Curent position in hyperspace
        self.bestPosition = None # Best found position by the particle
        self.velocity = None  # Current particle velocity
        self.cost = np.inf  # Current value of the cost function
        self.bestCost = np.inf  # Best value (lowest) of the cost function found by particle
        self.geomParticle = particle

    def initialize(self):
        """Method for initialization of the searching particle"""
        self.position = np.random.uniform(self.varMin, self.varMax, self.nVar).astype('double')
        self.velocity = np.zeros(self.nVar, dtype='double')
        self.update_cost()

    def update_cost(self):
        """Method for update the current cost value"""
        particleData = self.geomParticle.get_particle_parameters(self.imgScale, self.position, self.nVar)
        
        # Take only important parameters
        circularity = particleData['circularity']
        convexity = particleData['convexity']
        elongation = particleData['elongation']
        
        self.cost = m.sqrt(m.pow((self.init_circularity - circularity), 2) + \
                           m.pow((self.init_convexity - convexity), 2) + \
                           m.pow((self.init_elongation - elongation), 2))
        # Update self best cost
        if self.cost < self.bestCost:
            self.bestCost = self.cost
            self.bestPosition = self.position


class PSOAlg_py():
    """Class for particle swarm optimization algorithm"""
    def __init__(self, progress_callback, init_circularity, init_convexity,
                 init_elongation, nVar, varMin, varMax, useIterLimit, iterLimit, 
                 usePrecisionLimit, precisionLimit, showErrorPlot, nPop, w,
                 wDamp, c1, c2, a, b):
        self.progress_callback = progress_callback  # Link to the main window class
        self.init_circularity = init_circularity  # Initial (target) circularity 
        self.init_convexity = init_convexity  # Initial (target) convexity
        self.init_elongation = init_elongation  # Initial (target) elongation
        self.nVar = nVar  # Number of unknown (decision) variables (equal to nDim + realWidth)
        self.varMin = varMin  # Lower bound of decision variables
        self.varMax = varMax  # Upper bound of decision variables
        self.useIterLimit = useIterLimit  # Flag to use iteration limit
        self.iterLimit = iterLimit  # Maximum number of iterations
        self.usePrecisionLimit = usePrecisionLimit  # Flag to use precise limit
        self.precisionLimit = precisionLimit  # Minimum precise limit
        self.showErrorPlot = showErrorPlot  # Save or not progress data for plot
        self.nPop = nPop  # Population size (swarm size)
        self.w = w  # Inertia coefficient
        self.wDamp = wDamp  # Damping ratio of inertia coefficient
        self.c1 = c1  # Personal acceleration coefficient
        self.c2 = c2  # Social acceleration coefficient
        self.a = a  # Additional randomization of a-th particle in swarm
        self.b = b  # Additional randomization of all particles every b-th iteration   
        self.swarm = []  # List of individual searching particles
        self.doSearch = None  # Flag to run or stop the search
        self.iteration = None  # Current search iteration
        
        self.globalBestPosition = None  # Best position (solution)
        self.globalBestCost = np.inf  # The least value of the cost function 
        self.arrayBestCosts = []  # Array to see the progress of searching process
        self.r1 = None  # Parameter used in equation
        self.r2 = None  # Parameter used in equation
        
        self.particle = Particle()  # Construct particle for determination of its parameters
        
    def initialization(self):
        """Method for the initial generation of all the particles in the swarm"""
        self.swarm = []
        for i in range(self.nPop):
            particle = PSOParticle(self.nVar, self.varMin, self.varMax, self.init_circularity, 
                                   self.init_convexity, self.init_elongation, self.particle)
            particle.initialize()
            self.swarm.append(particle)
            self.update_global_best(self.swarm[i].bestCost, self.swarm[i].bestPosition)
        self.arrayBestCosts.append(self.globalBestCost)
        
    def update_global_best(self, bestCost, bestPosition):
        """Method for update the global best"""
        if bestCost < self.globalBestCost:
            self.globalBestCost = bestCost
            self.globalBestPosition = bestPosition
    
    def randomize_vector(self):
        """Method for randomization of the vector"""
        return np.random.uniform(0.0, 1.0, self.nVar).astype('double')
    
    def run_search(self):
        """Method for main searching loop"""
        # Initialization
        self.initialization()
        
        # Search
        self.doSearch = True
        self.iteration = 1
        self.arrayBestCosts = []
        while self.doSearch:
            # One search iteration
            for i in range(self.nPop):
                # Randomize r1 and r2 parameters
                self.r1 = self.randomize_vector()
                self.r2 = self.randomize_vector()
                # Update the velocity         
                self.swarm[i].velocity = self.w * self.swarm[i].velocity + \
                    self.r1*self.c1*(self.swarm[i].bestPosition - self.swarm[i].position) + \
                    self.r2*self.c2*(self.globalBestPosition - self.swarm[i].position)
                # Update the particle position
                self.swarm[i].position = self.swarm[i].position + self.swarm[i].velocity
                # Restrictions to the position (in should be in range 0.0 - 1.0). Reset to random
                for j in range(self.swarm[i].position.shape[0]):
                    if self.swarm[i].position[j] > 1.0:
                        self.swarm[i].position[j] = np.random.uniform(self.varMin, self.varMax, 1)[0]
                    if self.swarm[i].position[j] < 0.0:
                        self.swarm[i].position[j] = np.random.uniform(self.varMin, self.varMax, 1)[0]
                
                # Every a-th particle will be randomized
                if i % self.a == 0:
                    self.swarm[i].position = np.random.uniform(self.varMin, self.varMax, self.nVar).astype('double')

                # Aditional randomization - reset of particles every k-th iteration
                if self.iteration % self.b == 0:
                    self.swarm[i].position = np.random.uniform(self.varMin, self.varMax, self.nVar).astype('double')
                    self.w = np.random.uniform(0.0, 1.0, 1)[0]
                
                # Update particle cost and global best cost
                self.swarm[i].update_cost()
                self.update_global_best(self.swarm[i].bestCost, self.swarm[i].bestPosition)
                 
            # Reduce the inertia coefficient
            self.w = self.w * self.wDamp
            
            # Save the best global cost to the array
            if self.showErrorPlot:
                self.arrayBestCosts.append(self.globalBestCost)
            
            if self.useIterLimit and (self.iteration >= self.iterLimit):
                self.doSearch = False
            if self.usePrecisionLimit and (self.precisionLimit >= self.globalBestCost):
                self.doSearch = False
            
            # Make the data and return it as a progress callback
            progressData = {}
            progressData = {'iteration'         : self.iteration,
                            'globalBestPosition': self.globalBestPosition,
                            'globalBestCost'    : self.globalBestCost,
                            'arrayBestCosts'    : self.arrayBestCosts,
                            'doSearch'          : self.doSearch}            
            
            # Send the callback
            self.progress_callback.emit(progressData)       
            self.iteration += 1
                