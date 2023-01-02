/*======================================================================== 
  Module with functions for the calculation of particle parameters 
  ========================================================================*/

#include <stdlib.h>
#include <stdio.h>
#include <math.h>
#include "data_types.h"
#include "sort_array.h"

/* Function for printing the error end exiting the program */
static void print_error_and_exit(void);

/* Function for calculation of the particle area in pixels */
static double calc_area_pix(int nDim, double *dimsCoordMidX, double *dimsCoordMidY);

/* Function for calculation of the particle perimeter in pixels */
static double calc_perimeter_pix(int nDim, double *dimsCoordMidX, double *dimsCoordMidY);

/* Function for determination of the convex hull coordinates */
static int calc_convex_hull_coords(int nDim, double *dimsCoordMidX, double *dimsCoordMidY,
	double *hullCoordMidX, double *hullCoordMidY);
	
/* 2D cross product of OA and OB vectors, i.e. z-component of their 3D cross product. 
   Returns a positive value, if OAB makes a counter-clockwise turn,
   negative for clockwise turn, and zero if the points are collinear. */
static double cross(double Ox, double Oy, double Ax, double Ay, double Bx, double By);

/* Function for clear the array (make all elements equal to 0)  */
static void clear_array(double *array, int nDim);

/* Function to make the reverse order arrays of the coordinates */
static void reverse_array(double *coordMidX, double *coordMidY, int nDim);

/* Function to calculate the theta angle of major axis */
static double calc_theta(int nDim, double *dimsCoordMidX, double *dimsCoordMidY, 
	double areaPixels, double centreXPos, double centreYPos);
	
/* Function for determining moments and product of inertia about centroid */
static void calc_inertia(double *result, double nDim, double *dimsCoordMidX, double *dimsCoordMidY,
	double areaPixels, double centreXPos, double centreYPos);
	
/* Function for calculation principal moments of inertia and orientation */
static void calc_principal(double *result, double Ixx, double Iyy, double Ixy);

/* Function for calculation the certain projection length in um  */
static double calc_projection_length(double x1, double y1, double x2, double y2, int nDim,
	double *dimsCoordMidX, double *dimsCoordMidY, double imgScale);


void get_particle_parameters(double imgScale, double *dimsValues, int nDim, paramsStruct_t *allParams) {
	/* Main function for the calculation of particle parameters
	   imgScale          - Image scale (um/pix)
	   dimsValues        - Dimensions of the particle (set of values (0.0 - 1.0))
	   nDim              - Number of the particle dimensions (equal to the amount of sliders)
	   full              - full version of output (1) or short (0)
	   paramsStruct      - pointer for the structure with all particle parameters (paramsStruct_t type)
	   paramsStructShort - pointer for the structure with limited part parameters (paramsSctuctShort_t type) */
	
	/* Define important variables: */
	int i, j;
	double imgWidth = 360.0; /* Width of the image (pix) */
	double realWidth; /* Real width of the image with particle */
	double centreRadius = 5.0; /* Radius of the central polygon */
	double dN;  /* How many degrees in one section */
	double radius;  /* Radius to the point of polygon */
	double angle;  /* Angle between radius and horisontal line */
	double a, b, c;  /* Temporary double variables */
	double x1;  /* Temporary x coordinate */
	double x2;  /* Temporary x coordinate */
	double y1;  /* Temporary y coordinate */
	double y2;  /* Temporary y coordinate */
	int hullPointsNum;  /* Number of points of the convex hull */
	double theta; /* Angle of the particle orientation in rad */
	
	/* Define different arrays in dynamic memory*/
	/* Coordinates of all dims points (0 in left top corner) */
	double *dimsCoordX = (double*) malloc (nDim * sizeof(double));
	double *dimsCoordY = (double*) malloc (nDim * sizeof(double));
	if (NULL == dimsCoordX || NULL == dimsCoordY) print_error_and_exit();
	/* Coordinates of all dims points (0 in the middle of the particle) */
	double *dimsCoordMidX = (double*) malloc (nDim * sizeof(double));
	double *dimsCoordMidY = (double*) malloc (nDim * sizeof(double));
	if (NULL == dimsCoordMidX || NULL == dimsCoordMidY) print_error_and_exit();
	/* Coordinates of all convex hull points (0 in the middle of the particle) */
	double *hullCoordMidX = (double*) malloc (nDim * sizeof(double));
	double *hullCoordMidY = (double*) malloc (nDim * sizeof(double));
	if (NULL == hullCoordMidX || NULL == hullCoordMidY) print_error_and_exit();
	/* majorAxisPoints, minorAxisPoints */
	double *majorAxisPointsX = (double*) malloc (2 * sizeof(double));
	double *majorAxisPointsY = (double*) malloc (2 * sizeof(double));
	double *minorAxisPointsX = (double*) malloc (2 * sizeof(double));
	double *minorAxisPointsY = (double*) malloc (2 * sizeof(double));
	if (NULL == majorAxisPointsX || NULL == majorAxisPointsY) print_error_and_exit();
	if (NULL == minorAxisPointsX || NULL == minorAxisPointsY) print_error_and_exit();
	
	/* Parameters */
	double areaPixels;  /* Area of the particle in [pix] */
	double areaUm2;  /* Area of the particle in [um^2] */
	double CEDiameter; /* CE Diameter of the particle [um] */
	double centreXPos;  /* X coordinate of the centre [pix] */
	double centreYPos;  /* Y coordinate of the centre [pix] */
	double perimeter;  /* Perimeter of the particle [um] */
	double circularity;  /* Particle circularity parameter [-] */
	double convexHullPerimeter;  /* Convex Hull perimeter of the particle [um] */
	double convexity;  /* Convexity of the particle [-] */
	double areaConvexHullPix;  /* Area, encloseby in convex hull [pix] */
	double solidity;  /* Particle solidity [-] */
	double HSCircularity;  /* Hi sensitivity (HS) circularity [-] */
	double SEVolume;  /* Spherical equivalent (SE) volume of the particle */
	double orientation;  /* Angle of major axis in rad from the gorizontal line (from pi/2 to -pi/2 CCW) */
	double major_x1;  /* Major x1 coord */
	double major_y1;  /* Major y1 coord */
	double major_x2;  /* Major x2 coord */
	double major_y2;  /* Major y2 coord */
	double minor_x1;  /* Minor x1 coord */
	double minor_y1;  /* Minor y1 coord */
	double minor_x2;  /* Minor x2 coord */
	double minor_y2;  /* Minor y2 coord */
	double majorAxisDeg;  /* Angle of the major axis in degres */
	double length;  /* Length of the particle [um] */
	double width;  /* Width of the particle [um] */
	double aspectRatio;  /* Aspect ratio of the particle [-] */
	double elongation;  /* Elongation of the particle [-] */
	double maxDistance;  /* Max distance between points of particle */
	
	/* ========== Start the calculations ========== */
	
	/* realWidth: calculation of the real width */
	realWidth = imgScale * imgWidth;
	
	/* dimsCoord, dimsCoordMid: calculation the coordinates of the particle dims points */
	dN = 2 * M_PI / nDim;
	for (i = 0; i < nDim; i++) {
		radius = dimsValues[i] * (180.0 - centreRadius) + centreRadius;
		angle = i * dN;
		dimsCoordX[i] = cos(angle) * radius + 180.0;
		dimsCoordY[i] = sin(angle) * radius + 180.0;			
		dimsCoordMidX[i] = dimsCoordX[i] - 180.0;
		dimsCoordMidY[i] = dimsCoordY[i] - 180.0;
	}
	
	/* areaPixels: calculating particle area in pixels (Gerone method) */
	areaPixels = calc_area_pix(nDim, dimsCoordMidX, dimsCoordMidY);

	/* centreXPos, centreYPos: calculating coordinates (X, Y) of centre of mass */
	a = 0.0;
	b = 0.0;
	for (i = 0; i < nDim; i++) {
		if (i == (nDim - 1)) {
			x1 = dimsCoordMidX[0];
			y1 = dimsCoordMidY[0];
		} else {
			x1 = dimsCoordMidX[i + 1];
			y1 = dimsCoordMidY[i + 1];
		}
		a += (dimsCoordMidX[i] + x1) * (dimsCoordMidX[i] * y1 - x1 * dimsCoordMidY[i]);
		b += (dimsCoordMidY[i] + y1) * (dimsCoordMidX[i] * y1 - x1 * dimsCoordMidY[i]);		
	}
	centreXPos = a / (6.0 * areaPixels);
	centreYPos = b / (6.0 * areaPixels);
	
	/* areaUm2: calculating particle area in um^2 */
	areaUm2 = pow(imgScale, 2) * areaPixels;
	
	/* CEDiameter: calculating the CE Diameter */
	CEDiameter = sqrt(areaUm2 * 4/ M_PI);
	
	/* perimeter: calculating the perimeter */
	perimeter = calc_perimeter_pix(nDim, dimsCoordMidX, dimsCoordMidY);
	perimeter *= imgScale;

	/* circularity: calculating the particle circularity */
	circularity = 2 * sqrt(M_PI * areaUm2) / perimeter;

	/* HSCircularity: calculating the particle high sensitive (HS) circularity */
	HSCircularity = (4 * M_PI * areaUm2) / (pow(perimeter, 2));
	
	/* calculate coordinates of the convex hull points */
	hullPointsNum = calc_convex_hull_coords(nDim, dimsCoordMidX, dimsCoordMidY,
		hullCoordMidX, hullCoordMidY);
	
	/* areaConvexHullPix: calculation the area enclosed by convex hull */
	areaConvexHullPix = calc_area_pix(hullPointsNum, hullCoordMidX, hullCoordMidY);
	
	/* convexHullPerimeter: calculationg the convex hull perimeter */
	convexHullPerimeter = calc_perimeter_pix(hullPointsNum, hullCoordMidX, hullCoordMidY);
	convexHullPerimeter *= imgScale;
	
	/* convexity: calculating the particle convexity */
	convexity = convexHullPerimeter / perimeter;
	
	/* solidity: calculating the particle solidity */
	solidity = areaPixels / areaConvexHullPix;
	
	/* SEVolume: calculating the spherical equivalent (SE) volume */
	SEVolume = (M_PI * pow(CEDiameter, 3)) / 6;
	
	/* orientation: calculation of particle orientation as angle of
	   major axis in rad from the gorizontal line (from pi/2 to -pi/2 CCW) */
	theta = calc_theta(nDim, dimsCoordMidX, dimsCoordMidY, areaPixels, centreXPos, centreYPos);
	orientation = M_PI / 2 - theta;
	
	/* minorAxisPoints, majorAxisPoints: calculations of the points for major and minor axis
	   Points are scaled to be exaxtly on a circle with the CE diameter (imgScale is used) */
	major_x1 = centreXPos + cos(orientation) * CEDiameter / (2 * imgScale);
    major_y1 = centreYPos - sin(orientation) * CEDiameter / (2 * imgScale);
    major_x2 = centreXPos - cos(orientation) * CEDiameter / (2 * imgScale);
    major_y2 = centreYPos + sin(orientation) * CEDiameter / (2 * imgScale);
    
    minor_x1 = centreXPos - sin(orientation) * CEDiameter / (2 * imgScale);
    minor_y1 = centreYPos - cos(orientation) * CEDiameter / (2 * imgScale);
    minor_x2 = centreXPos + sin(orientation) * CEDiameter / (2 * imgScale);
    minor_y2 = centreYPos + cos(orientation) * CEDiameter / (2 * imgScale);
    
    /* majorAxisDeg: calculating the angle (in degres) of major axis as in Morphologi G3*/
    majorAxisDeg = 180.0 - orientation * 180.0 / M_PI;
    
    /* length, width: calculating the length and width of the particle */
    length = calc_projection_length(major_x1, major_y1, major_x2, major_y2, nDim,
		dimsCoordMidX, dimsCoordMidY, imgScale);
	width = calc_projection_length(minor_x1, minor_y1, minor_x2, minor_y2, nDim,
		dimsCoordMidX, dimsCoordMidY, imgScale);
	
	/* aspectRatio: calculation of the aspect ratio of the particle */
	aspectRatio = width / length;
	if (aspectRatio > 1) {  /* We have to swap the axes */
		/* swap coordinates */
		x1 = major_x1;
        y1 = major_y1;
        x2 = major_x2;
        y2 = major_y2;
        major_x1 = minor_x1;
        major_y1 = minor_y1;
        major_x2 = minor_x2;
        major_y2 = minor_y2;
        minor_x1 = x1;
        minor_y1 = y1;
        minor_x2 = x2;
        minor_y2 = y2;
        /* swap width and length */
        a = width;
        width = length;
        length = a;
        /* recalculate the aspect ratio */
        aspectRatio = width / length;
        /* recalculate the majorAxisDeg */
        if (majorAxisDeg > 90.0) {
        	majorAxisDeg -= 90.0;
		} else {
			majorAxisDeg += 90.0;
		}
	}
	
	/* elongation: calculation of the particle elongation */
	elongation = 1.0 - aspectRatio;
	
	/* maxDistance: calculation of the maximum particle distance */
	maxDistance = 0.0;
    c = 0.0;
    for (i = 0; i < nDim; i++) {
    	for (j = 0; j < nDim; j++) {
    		if (i != j) {
    			c = sqrt(pow(dimsCoordMidX[i] - dimsCoordMidX[j], 2) + pow(dimsCoordMidY[i] - dimsCoordMidY[j], 2));
    			if (c > maxDistance) {
    				maxDistance = c;
				}
			}
		}
	}
	maxDistance *= imgScale;
	
	/* Fill the the output structure with calculated parameters (paramsStruct) */
	allParams->nDim = nDim;
	allParams->imgScale = imgScale;
	allParams->imgWidth = imgWidth;
	allParams->realWidth = realWidth;
	allParams->centreXPos = centreXPos;
	allParams->centreYPos = centreYPos;
	allParams->areaPixels = areaPixels;
	allParams->areaUm2 = areaUm2;
	allParams->CEDiameter = CEDiameter;
	allParams->perimeter = perimeter;
	allParams->circularity = circularity;
	allParams->HSCircularity = HSCircularity;
	allParams->convexity = convexity;
	allParams->solidity = solidity;
	allParams->SEVolume = SEVolume;
	allParams->major_x1 = major_x1;
	allParams->major_y1 = major_y1;
	allParams->major_x2 = major_x2;
	allParams->major_y2 = major_y2;
	allParams->minor_x1 = minor_x1;
	allParams->minor_y1 = minor_y1;
	allParams->minor_x2 = minor_x2;
	allParams->minor_y2 = minor_y2;
	allParams->majorAxisDeg = majorAxisDeg;
	allParams->length = length;
    allParams->width = width;
    allParams->aspectRatio = aspectRatio;
	allParams->elongation = elongation;
	allParams->maxDistance = maxDistance;
	
	/* Free different arrays in raw memory*/
	free(dimsCoordX);
	free(dimsCoordY);
	free(dimsCoordMidX);
	free(dimsCoordMidY);
	free(hullCoordMidX);
	free(hullCoordMidY);
	free(majorAxisPointsX);
	free(majorAxisPointsY);
	free(minorAxisPointsX);
	free(minorAxisPointsY);
} /* fcn get_particle_parameters */


static void print_error_and_exit(void) {
	/* Function for printing the error end exiting the program */
	printf("Error in memory allocation!");
	exit(1);
} /* fcn print_error_and_exit */


static double calc_area_pix(int nDim, double *dimsCoordMidX, double *dimsCoordMidY) {
	/* Function for calculation of the particle area in pixels
       nDim          - number of dimensions or length of the arrays
	   dimsCoordMidX - pointer to array of X coord of dims points
	   dimsCoordMidY - pointer to array of Y coord of dims points */
	int i;
	double a = 0.0;
	double x, y;
	
	for (i = 0; i < nDim; i++) {
		if (i == (nDim - 1)) {
			x = dimsCoordMidX[0];
			y = dimsCoordMidY[0];
		} else {
			x = dimsCoordMidX[i + 1];
			y = dimsCoordMidY[i + 1];
		}
		a += (dimsCoordMidX[i] * y - x * dimsCoordMidY[i]);
	}
	return (a / 2);
} /* fcn calc_area_pix */


static double calc_perimeter_pix(int nDim, double *dimsCoordMidX, double *dimsCoordMidY) {
	/* Function for calculation of the particle perimeter in pixels
       nDim          - number of dimensions or length of the arrays
	   dimsCoordMidX - pointer to array of X coord of dims points
	   dimsCoordMidY - pointer to array of Y coord of dims points */
	int i;
	double perimeter = 0.0;
	double x1, y1, x2, y2;
	
	for (i = 0; i < nDim; i++) {
		x1 = dimsCoordMidX[i];
		y1 = dimsCoordMidY[i];
		if (i == (nDim - 1)) {
			x2 = dimsCoordMidX[0];
			y2 = dimsCoordMidY[0];
		} else {
			x2 = dimsCoordMidX[i + 1];
			y2 = dimsCoordMidY[i + 1];
		}
		perimeter += sqrt(pow((x2 - x1), 2) + pow((y2 - y1), 2));
	}
	return perimeter;	
} /* calc_perimeter_pix */


static int calc_convex_hull_coords(int nDim, double *dimsCoordMidX, double *dimsCoordMidY,
	double *hullCoordMidX, double *hullCoordMidY) {
	/* Function for calculation of the coordinates of the convex hull. 
	   Implements Andrew's monotone chain algorithm. O(n log n) complexity.	
       nDim          - number of dimensions or length of the arrays
	   dimsCoordMidX - pointer to array of X coord of dims points
	   dimsCoordMidY - pointer to array of Y coord of dims points
	   hullCoordMidX - pointer to array of X coord of convex hull
	   hullCoordMidY - pointer to array of Y coord of convex hull
	   return:
	   ptr           - number of elements in the hullCoordMid arrays */
	
	int i;
	int ptr, ptrLower, ptrUpper;  /* pointer to the element in array */
	
	/* Make the copy of dimsCoordMidX and dimsCoordMidY in the memory */
	double *coordMidX = (double *) malloc (nDim * sizeof(double));
	double *coordMidY = (double *) malloc (nDim * sizeof(double));
	if (NULL == coordMidX || NULL == coordMidY) print_error_and_exit();
	
	for (i = 0; i < nDim; i++) {
		coordMidX[i] = dimsCoordMidX[i];
		coordMidY[i] = dimsCoordMidY[i];
	}
	
	/* Make sort by the x coordinate of all points in array */
	sort_array(coordMidX, coordMidY, nDim);

	/* Build lower hull */
	double *lowerX = (double *) malloc (nDim * sizeof(double));
	double *lowerY = (double *) malloc (nDim * sizeof(double));
	if (NULL == lowerX || NULL == lowerY) print_error_and_exit();
	
	clear_array(lowerX, nDim);
	clear_array(lowerY, nDim);
	
	ptr = -1;
	for (i = 0; i < nDim; i++) {
		while (ptr >= 1 && cross(lowerX[ptr - 1], lowerY[ptr - 1], 
			lowerX[ptr], lowerY[ptr], coordMidX[i], coordMidY[i]) <= 0) {
				ptr--;
			}
		ptr++;
		lowerX[ptr] = coordMidX[i];
		lowerY[ptr] = coordMidY[i];
	}
	ptrLower = ptr;  /* save the poiner to the max elem in lower arrays */
	
	/* Reverse the previously sorted array */
	reverse_array(coordMidX, coordMidY, nDim);
	
	/* Build upper hull */
	double *upperX = (double *) malloc (nDim * sizeof(double));
	double *upperY = (double *) malloc (nDim * sizeof(double));
	if (NULL == upperX || NULL == upperY) print_error_and_exit();
	
	clear_array(upperX, nDim);
	clear_array(upperY, nDim);
	
	ptr = -1;
	for (i = 0; i < nDim; i++) {
		while (ptr >= 1 && cross(upperX[ptr - 1], upperY[ptr - 1], 
			upperX[ptr], upperY[ptr], coordMidX[i], coordMidY[i]) <= 0) {
				ptr--;
			}
		ptr++;
		upperX[ptr] = coordMidX[i];
		upperY[ptr] = coordMidY[i];	
	}
	ptrUpper = ptr;  /* save the poiner to the max elem in upper arrays */
	
	/* Concatenation of the lower and upper hulls gives the convex hull. 
	   Last point of each list is omitted because it is repeated at the 
	   beginning of the other list. */
	ptr = 0;
	for (i = 0; i < ptrLower; i++) {
		hullCoordMidX[ptr] = lowerX[i];
		hullCoordMidY[ptr] = lowerY[i];
		ptr++;
	}
	for (i = 0; i < ptrUpper; i++) {
		hullCoordMidX[ptr] = upperX[i];
		hullCoordMidY[ptr] = upperY[i];
		ptr++;
	}
	
	/* Clear the used dynamic memory */
	free(coordMidX);
	free(coordMidY);
	free(lowerX);
	free(lowerY);
	free(upperX);
	free(upperY);
	
	/* ptr now containt the dimension of the hullCoordMid arrays */
	return ptr;
} /* fcn calc_convex_hull_coords */


static double cross(double Ox, double Oy, double Ax, double Ay, double Bx, double By) {
	/* 2D cross product calculation of OA and OB vectors, i.e. z-comp of their 3D cross product.
	   Ox, Oy - X and Y coordinates of the reference point
	   Ax, Ay - X and Y coordinates of the vector A
	   Bx, By - X and Y coordinates of the vector B  */
	double z = 0;
	z = (Ax - Ox) * (By - Oy) - (Ay - Oy) * (Bx - Ox);
	return z;
} /* fcn cross */
	
	
static void clear_array(double *array, int nDim) {
	/* Function for clear the array (make all elements equal to 0)  */
	int i;
	for (i = 0; i < nDim; i++) {
		array[i] = 0;
	}
} /* fcn clear_array */


static void reverse_array(double *coordMidX, double *coordMidY, int nDim) {
	/* Function to make the reverse order arrays of the coordinates */
	int i;
	double temp;
	for (i = 0; i < (nDim / 2); i++) {
		/* swap coordMidX values */
		temp = coordMidX[i];
		coordMidX[i] = coordMidX[nDim - 1 - i];
		coordMidX[nDim - 1 - i] = temp;
		
		/* swap coordMidY values */
		temp = coordMidY[i];
		coordMidY[i] = coordMidY[nDim - 1 - i];
		coordMidY[nDim - 1 - i] = temp;
	}
} /* fcn reverse_array */


static double calc_theta(int nDim, double *dimsCoordMidX, double *dimsCoordMidY, 
	double areaPixels, double centreXPos, double centreYPos) {
	/* Function to calculate the theta angle of major axis 
	   nDim          - number of dimensions or length of the arrays
	   dimsCoordMidX - pointer to array of X coord of dims points
	   dimsCoordMidY - pointer to array of Y coord of dims points 
	   areaPixels    - area of the polygon in pixels
	   centreXPos    - X coordinate of the centre of mass
	   centreYPos    - Y coordinate of the centre of mass  
	   return:
	   theta         - angle of the major axis in radians */

	double Ixx, Iyy, Ixy, theta;
	double result[3];
	
	/* Determine moments and product of inertia about centroid */
	calc_inertia(result, nDim, dimsCoordMidX, dimsCoordMidY, areaPixels, centreXPos, centreYPos);
	Ixx = result[0];
	Iyy = result[1];
	Ixy = result[2];
	
	/* Determine principal moments of inertia and orientation */
	calc_principal(result, Ixx, Iyy, Ixy);
	theta = result[2];
	
	/* Return only theta */
	return theta;
} /* fcn calc_theta */


static void calc_inertia(double *result, double nDim, double *dimsCoordMidX, double *dimsCoordMidY,
	double areaPixels, double centreXPos, double centreYPos) {
	/* Function for determining moments and product of inertia about centroid 
	   result        - pointer to the output array with the calculated data
	   nDim          - number of dimensions or length of the arrays
	   dimsCoordMidX - pointer to array of X coord of dims points
	   dimsCoordMidY - pointer to array of Y coord of dims points 
	   areaPixels    - area of the polygon in pixels
	   centreXPos    - X coordinate of the centre of mass
	   centreYPos    - Y coordinate of the centre of mass */
	
	int i;
	double sxx = 0.0;
	double syy = 0.0;
	double sxy = 0.0;
	double Ixx, Iyy, Ixy;
	double x, y, tmp;
	
	for (i = 0; i < nDim; i++) {
		if (i == (nDim - 1)) {
			x = dimsCoordMidX[0];
			y = dimsCoordMidY[0];
		} else {
			x = dimsCoordMidX[i + 1];
			y = dimsCoordMidY[i + 1];
		}
		
		tmp = (dimsCoordMidX[i]*y - x*dimsCoordMidY[i]);
		sxx += (pow(dimsCoordMidY[i], 2) + dimsCoordMidY[i]*y + pow(y, 2)) * tmp;
		syy += (pow(dimsCoordMidX[i], 2) + dimsCoordMidX[i]*x + pow(x, 2)) * tmp;
		sxy += (dimsCoordMidX[i]*y + 2*dimsCoordMidX[i]*dimsCoordMidY[i] + 2*x*y + x*dimsCoordMidY[i]) * tmp;
	}
	
	Ixx = sxx / 12 - areaPixels * pow(centreYPos, 2);
	Iyy = syy / 12 - areaPixels * pow(centreXPos, 2);
	Ixy = sxy / 24 - areaPixels * centreXPos * centreYPos;
	
	/* Prepare output */
	result[0] = Ixx;
	result[1] = Iyy;
	result[2] = Ixy;		
} /* fcn calc_inertia */


static void calc_principal(double *result, double Ixx, double Iyy, double Ixy) {
	/* Function for calculation principal moments of inertia and orientation
	   result - pointer to the output array with the calculated data
	   Ixx    - parameter Ixx
	   Iyy    - parameter Iyy
	   Ixy    - parameter Ixy */
	
	double avg, diff, I1, I2, theta;
	
	avg = (Ixx + Iyy) / 2;
	diff = (Ixx - Iyy) / 2;
	
	/* Some tricks to avoid symmetry and strange theta calculation */
	if (diff < 1 && diff > 0) {
		diff = 1;
	}
	if (diff > -1 && diff < 0) {
		diff = -1;
	}
	
	I1 = avg + sqrt(pow(diff, 2) + pow(Ixy, 2));
	I2 = avg - sqrt(pow(diff, 2) + pow(Ixy, 2));
	theta = atan2(-Ixy, diff) / 2;
	
	/* Prepare output data */
	result[0] = I1;
	result[1] = I2;
	result[2] = theta;
} /* fcn calc_principal */


static double calc_projection_length(double x1, double y1, double x2, double y2, int nDim,
	double *dimsCoordMidX, double *dimsCoordMidY, double imgScale) {
	/* Function for calculation the certain projection length in um
	   x1            - X coordinate of the first point
	   y1            - Y coordinate of the first point
	   x2            - X coordinate of the second point
	   y2            - Y coordinate of the second point
	   nDim          - number of dimensions or length of the arrays
	   dimsCoordMidX - pointer to array of X coord of dims points
	   dimsCoordMidY - pointer to array of Y coord of dims points
	   imgScale      - value of the image scale
	   return:
	   length        - projection length  */
	
	double *projectionsX = (double *) malloc (nDim * sizeof(double));
	double *projectionsY = (double *) malloc (nDim * sizeof(double));
	if (NULL == projectionsX || NULL == projectionsY) print_error_and_exit();
	int i;
	double a, b, c, d, x, y;
	double length;
	double maxX, maxY, minX, minY;
	
	/* Calculate projection of all points on the axis */
	for(i = 0; i < nDim; i++) {
		a = y2 - y1;
		b = x2 - x1;
		if (fabs(a) <= 0.5) {  /* Horizontal line */
			x = dimsCoordMidX[i];
			y = y1;
		} else if (fabs(b) <= 0.5) {  /* Vertical line */
			y = dimsCoordMidY[i];
			x = x1;
		} else {
			c = -1 * x1 * a / b + y1;
			d = dimsCoordMidX[i] * b / a + dimsCoordMidY[i];
			x = ((d - c) * b * a) / (pow(a, 2) + pow(b, 2));
			y = x * a / b + c;
		}
		projectionsX[i] = x;
		projectionsY[i] = y;
	}
	
	if (fabs(x2 - x1) > fabs(y2 - y1)) {
		/* use x coordinates to find the minimum and maximum points on a line */
		maxX = -INFINITY;
		minX = INFINITY;
		for (i = 0; i < nDim; i++) {
			if (projectionsX[i] > maxX) {
				maxX = projectionsX[i];
				maxY = projectionsY[i];
			}
			if (projectionsX[i] < minX) {
				minX = projectionsX[i];
				minY = projectionsY[i];
			}	
		}	
	} else {  /* use y coordinates to find the minimum and maximum points on a line */
		maxY = -INFINITY;
        minY = INFINITY;
        for (i = 0; i < nDim; i++) {
        	if (projectionsY[i] > maxY) {
        		maxY = projectionsY[i];
        		maxX = projectionsX[i];
			}
			if (projectionsY[i] < minY) {
				minY = projectionsY[i];
				minX = projectionsX[i];
			}
		}
	}
	
	/* Calculate the particle projection length */
	length = sqrt(pow(maxX - minX, 2) + pow(maxY - minY, 2)) * imgScale;
	
	/* Clear the used dynamic memory */
	free(projectionsX);
	free(projectionsY);
	
	return length;
} /* fcn calc_projection_length */
