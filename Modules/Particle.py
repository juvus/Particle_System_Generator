#================================================================================
# Wrapping of the dll library particle.dll for determination of the particle 
# parameters. 
#================================================================================

import ctypes
import struct
from math import pi, sin, cos

# Define the c structure with output particle parameters
class paramsStruct_t(ctypes.Structure):
    _fields_ = \
        [('nDim', ctypes.c_int),  # Number of the particle dimensions (equal to the amount of sliders)
         ('imgScale', ctypes.c_double),  # Image scale (um/pix)
         ('imgWidth', ctypes.c_int),  # Width of the image (pix)
         ('realWidth', ctypes.c_double),  # Real width of the image with particle
         ('centreXPos', ctypes.c_double),  # X coordinate of the centre [pix]
         ('centreYPos', ctypes.c_double),  # Y coordinate of the centre [pix]
         ('areaPixels', ctypes.c_double),  # Area of the particle in [pix]
         ('areaUm2', ctypes.c_double),  # Area of the particle in [um^2]
         ('CEDiameter', ctypes.c_double),  # CE Diameter of the particle [um]
         ('perimeter', ctypes.c_double),  # Perimeter of the particle [um]
         ('circularity', ctypes.c_double),  # Particle circularity parameter [-]
         ('HSCircularity', ctypes.c_double),  # Hi sensitivity (HS) circularity [-]
         ('convexity', ctypes.c_double),  # Convexity of the particle [-]
         ('solidity', ctypes.c_double),  # Particle solidity [-]
         ('SEVolume', ctypes.c_double),  # Spherical equivalent (SE) volume of the particle
         ('major_x1', ctypes.c_double),  # Major x1 coord
         ('major_y1', ctypes.c_double),  # Major y1 coord
         ('major_x2', ctypes.c_double),  # Major x2 coord
         ('major_y2', ctypes.c_double),  # Major y2 coord
         ('minor_x1', ctypes.c_double),  # Minor x1 coord
         ('minor_y1', ctypes.c_double),  # Minor y1 coord
         ('minor_x2', ctypes.c_double),  # Minor x2 coord
         ('minor_y2', ctypes.c_double),  # Minor y2 coord
         ('majorAxisDeg', ctypes.c_double),  # Angle of the major axis in degres
         ('length', ctypes.c_double),  # Length of the particle [um]
         ('width', ctypes.c_double),  # Width of the particle [um]
         ('aspectRatio', ctypes.c_double),  # Aspect ratio of the particle [-]
         ('elongation', ctypes.c_double),  # Elongation of the particle [-]
         ('maxDistance', ctypes.c_double)]  # Max distance between points of particle

class Particle():
    """Wrapper class for dll with particle parameters calculation routins"""
    
    def __init__(self):
        """Constructor of the class"""
        self.dll = ctypes.WinDLL('./Modules/Generator_c/build/particle.dll')  # Loading the dll library
        
        # Function in dll is the following:
        # void get_particle_parameters(double imgScale, double *dimsValues, int nDim, paramsStruct_t *allParams)
                
        # Define the function return type:
        self.dll.get_particle_parameters.restype = None
        
        # Define the function parameters:
        self.dll.get_particle_parameters.argtypes = \
            [ctypes.c_double,  # imgScale
             ctypes.POINTER(ctypes.c_double),  # dimsValues
             ctypes.c_int,  # nDim
             ctypes.POINTER(paramsStruct_t)]  # allParams

        # Creating empty structure for dll function
        self.paramsStruct = paramsStruct_t();


    def get_particle_parameters(self, imgScale, dimsValues, nDim):  
        """Function for the calculation of particle parameters
           imgScale: Image scale (um/pix)
           dimsValues: Dimensions of the particle (set of values (0.0 - 1.0))
           nDim: Number of the particle dimensions (equal to the amount of sliders)
        """
        # Creation dimsValues array for the dll function
        dimsValues_t = ctypes.c_double * nDim
        dimsValuesArr = dimsValues_t();
        
        for i in range(nDim):
            dimsValuesArr[i] = dimsValues[i]
        
        # Call the function from particle.dll (Wrapped function)
        ret = self.dll.get_particle_parameters(imgScale, dimsValuesArr, nDim, 
            ctypes.byref(self.paramsStruct))
        
        # Additional calculation of the coordinates
        # dimsCoord, dimsCoordMid: calculation the coordinates of the particle dims points
        centreRadius = 5  # Radius of the central polygon
        imgWidth = 360  # Width of the image (pix)
        
        dN = 2 * pi / nDim
        array = [0] * nDim
        arrayMid = [0] * nDim
        for i in range(nDim):
            radius = dimsValues[i] * (180 - centreRadius) + centreRadius  # Slider starts not from the center!
            angle = i * dN
            x = int(round(cos(angle) * radius + imgWidth/2))
            y = int(round(sin(angle) * radius + imgWidth/2))
            array[i] = (x, y)
            arrayMid[i] = (x - imgWidth/2, y - imgWidth/2)
        dimsCoord = tuple(array)
        dimsCoordMid = tuple(arrayMid)       
        
        majorAxisPoints = ((self.paramsStruct.major_x1, 
                            self.paramsStruct.major_y1),
                           (self.paramsStruct.major_x2,
                            self.paramsStruct.major_y2))
        minorAxisPoints = ((self.paramsStruct.minor_x1, 
                            self.paramsStruct.minor_y1),
                           (self.paramsStruct.minor_x2,
                            self.paramsStruct.minor_y2))
        
        # Prepare the output dictionary CalculatedParams
        CalculatedParams = \
            {'nDim': self.paramsStruct.nDim,
             'dimsValues': dimsValues,
             'imgScale': imgScale,
             'imgWidth': self.paramsStruct.imgWidth,
             'realWidth': self.paramsStruct.realWidth,
             'dimsCoord' : dimsCoord,
             'dimsCoordMid': dimsCoordMid,
             'areaPixels': self.paramsStruct.areaPixels,
             'areaUm2': self.paramsStruct.areaUm2,
             'CEDiameter': self.paramsStruct.CEDiameter,
             'centreXPos': self.paramsStruct.centreXPos,
             'centreYPos': self.paramsStruct.centreYPos,
             'perimeter': self.paramsStruct.perimeter,
             'circularity': self.paramsStruct.circularity,
             'convexity': self.paramsStruct.convexity,
             'solidity': self.paramsStruct.solidity,
             'HSCircularity': self.paramsStruct.HSCircularity,
             'SEVolume': self.paramsStruct.SEVolume,
             'majorAxisPoints': majorAxisPoints,
             'minorAxisPoints': minorAxisPoints,
             'majorAxisDeg': self.paramsStruct.majorAxisDeg,
             'length': self.paramsStruct.length,
             'width': self.paramsStruct.width,
             'aspectRatio': self.paramsStruct.aspectRatio,
             'elongation': self.paramsStruct.elongation,
             'maxDistance': self.paramsStruct.maxDistance}
        
        # Return the calculated particle parameters
        return CalculatedParams