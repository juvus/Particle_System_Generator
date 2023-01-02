#================================================================================
# Wrapping of the dll library pso_algorithm.dll for searching the particle
# shape with PSO algorithm
#================================================================================

import ctypes
import struct

class PSOAlg_dll():
    """Wrapper class for dll with PSO searching algorithm"""
    
    def __init__(self):
        """Constructor of the class"""
        self.dll = ctypes.WinDLL('./Modules/Generator_c/build/pso_algorithm.dll')  # Loading the dll library

        # Function in dll is the following:
        # void PSOAlg_run_search(double init_circularity, double init_convexity, double init_elongation,
        # int nVar, double varMin, double varMax, int useIterLimit, int iterLimit, 
        # int usePrecisionLimit, double precisionLimit, int showErrorPlot, int nPop, double w,
        # double wDamp, double c1, double c2, int a, int b, unsigned int *iteration, double *globalBestCost, 
        # double *globalBestPosition, double *arrayBestCosts)

        # Define the function return type:
        self.dll.PSOAlg_run_search.restype = None
        
        # Define the function parameters:
        self.dll.PSOAlg_run_search.argtypes = [
            ctypes.c_double,  # init_circularity
            ctypes.c_double,  # init_convexity
            ctypes.c_double,  # init_elongation
            ctypes.c_int,  # nVar
            ctypes.c_double,  # varMin
            ctypes.c_double,  # varMax
            ctypes.c_int,  # useIterLimit
            ctypes.c_int,  # iterLimit
            ctypes.c_int,  # usePrecisionLimit
            ctypes.c_double,  # precisionLimit
            ctypes.c_int,  # showErrorPlot
            ctypes.c_int,  # nPop
            ctypes.c_double,  # w
            ctypes.c_double,  # wDamp
            ctypes.c_double,  # c1
            ctypes.c_double,  # c2
            ctypes.c_int,  # a
            ctypes.c_int,  # b
            ctypes.POINTER(ctypes.c_uint),  # pointer to iteration
            ctypes.POINTER(ctypes.c_double),  # pointer to globalBestCost
            ctypes.POINTER(ctypes.c_double),  # pointer to globalBestPosition
            ctypes.POINTER(ctypes.c_double)]  # pointer to arrayBestCosts
            
    def run_search(self, init_circularity, init_convexity, init_elongation, nVar, varMin,
                   varMax, useIterLimit, iterLimit, usePrecisionLimit, precisionLimit,
                   showErrorPlot, nPop, w, wDamp, c1, c2, a, b):
        """Method for main searching loop"""
        
        # Create additional parameters for the function
        if(useIterLimit):
            useIterLimit = 1  # Prepare for c function (true -> 1)
        else:
            useIterLimit = 0  # Prepare for c function (false -> 0)
            
        if(usePrecisionLimit):
            usePrecisionLimit = 1  # Prepare for c function (true -> 1)
        else:
            usePrecisionLimit = 0  # Prepare for c function (false -> 0)
        
        iteration_t = ctypes.c_uint  # Type
        iteration = iteration_t()  # L-value
        iteration_p = ctypes.byref(iteration)  # Pointer
        
        globalBestCost_t = ctypes.c_double
        globalBestCost = globalBestCost_t()
        globalBestCost_p = ctypes.byref(globalBestCost)
        
        globalBestPosition_t = ctypes.c_double * nVar
        globalBestPosition = globalBestPosition_t()
        globalBestPosition_p = ctypes.cast(globalBestPosition, ctypes.POINTER(ctypes.c_double))    
        
        if(showErrorPlot):
            showErrorPlot = 1  # Prepare for c function (true -> 1)
            arrayBestCosts_t = ctypes.c_double * iterLimit   
            arrayBestCosts = arrayBestCosts_t()
            arrayBestCosts_p = ctypes.cast(arrayBestCosts, ctypes.POINTER(ctypes.c_double)) 
        else:
            showErrorPlot = 0  # Prepare for c function (false -> 0)
            arrayBestCosts_t = ctypes.c_double
            arrayBestCosts_p = arrayBestCosts_t()
        
        # Call the function from pso_algorithm.dll (Wrapped function)
        ret = self.dll.PSOAlg_run_search(init_circularity, init_convexity, init_elongation, 
            nVar, varMin, varMax, useIterLimit, iterLimit, usePrecisionLimit, precisionLimit,
            showErrorPlot, nPop, w, wDamp, c1, c2, a, b, iteration_p, globalBestCost_p, 
            globalBestPosition_p, arrayBestCosts_p)
            
        # Prepare the calculated parameters suitable for python use
        iteration = iteration.value
        globalBestCost = globalBestCost.value
        
        globalBestPositionList = [0.0] * nVar
        for i in range(nVar):
            globalBestPositionList[i] = globalBestPosition[i]
            
        if(showErrorPlot):
            arrayBestCostsList = [0.0] * iterLimit
            for i in range(iterLimit):
                arrayBestCostsList[i] = arrayBestCosts[i]
        else:
            arrayBestCostsList = []
        
        # Prepare the output dictionary CalculatedParams
        CalculatedParams = \
            {'iteration': iteration,
             'globalBestCost': globalBestCost,
             'globalBestPosition': globalBestPositionList,
             'arrayBestCosts': arrayBestCostsList}
        
        # Return the calculated particle parameters
        return CalculatedParams