#ifndef DATA_TYPES_H_
#define DATA_TYPES_H_

	/* Declare the full output structure */
	struct paramsStruct {
		int nDim;
		double imgScale;
		int imgWidth;
		double realWidth;
	    double centreXPos;
	    double centreYPos;
	    double areaPixels;
	    double areaUm2;
	    double CEDiameter;
	    double perimeter;
	    double circularity;
	    double HSCircularity;
	    double convexity;
	    double solidity;
	    double SEVolume;
	    double major_x1;
	    double major_y1;
	    double major_x2;
	    double major_y2;
	    double minor_x1;
	    double minor_y1;
	    double minor_x2;
	    double minor_y2;
	    double majorAxisDeg;
	    double length;
	    double width;
	    double aspectRatio;
	    double elongation;
	    double maxDistance;
	};
	
	/* Type of the paramsStruct */
	typedef struct paramsStruct paramsStruct_t;
	
#endif /* DATA_TYPES_H_ */
