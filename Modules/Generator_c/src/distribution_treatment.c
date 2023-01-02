/*======================================================================== 
  Module with functions for the distributions treatment and generating
  values from the specific normalized differential distribution
  ========================================================================*/

#include <stdlib.h>
#include <stdio.h>
#include <math.h>

/* Function for generation random double numbers in range [0.0, 1.0) */
static double random_double(void);

void calc_diff_from_cum(double *cum, double *diff) {
	/* Function for calculation the differential disrtibution from cumulative distribution
	   cum  - pointer to cumulative distribution 1D array
	   return:
	   diff - pointer to differential distribution array */
	
	int i;
	
	diff[0] = cum[0];
	for (i = 1; i < 100; i++) {
		diff[i] = cum[i] - cum[i - 1];
		if (diff[i] < 0) {
			diff[i] = 0;
		}
	}
}

void normalize_diff(double *diff, double *normDiff) {
	/* Function for normalize the differential distribution
	   diff     - pointer to the differential distribution
	   return:
	   normDiff - pointer to the normalized differential distribution */
	   
	int i;
	double maxNum = 0.0;
	
	for (i = 0; i < 100; i++) {
		if (diff[i] > maxNum) {
			maxNum = diff[i];
		}
	}
	
	for (i = 0; i < 100; i++) {
		normDiff[i] = diff[i] / maxNum;
	}
}

void calc_boundaries(double *normDiff, int *leftBndChannel, int *rightBndChannel) {
	/* Function for determining the differential distribution boundaries 
	   normDiff        - pointer to the narmlized distribution array 
	   return:
	   leftBndChannel  - pointer to the left boundary channel
	   rightBndChannel - pointer to the right boundary channel */
	   
	int i;
	
	*leftBndChannel = 0;
	for (i = 0; i < 100; i++) {
		if (normDiff[i] > 0) {
			*leftBndChannel = i;
			break;
		}
	}
	
	*rightBndChannel = 99;
	for (i = 0; i < 100; i++) {
		if (normDiff[99 - i] > 0) {
			*rightBndChannel = 99 - i;
			break;
		}
	}
}

void make_distr_from_count_array(unsigned long *countArray, double *diff, double *cum) {
	/* Function for making diff and cum disributions from the count array 
	   countArray - pointer to the count differential distribution array
	   return:
	   diff       - pointer to the differential distribution array
	   cum        - pointer to the cumulative distribution array */
	   
	int i;
	unsigned long partSum = 0;
	
	for (i = 0; i < 100; i++) {
		partSum += countArray[i];
	}
	
	/* Make differential distribution */
	for (i = 0; i < 100; i++) {
		diff[i] = (double)countArray[i] * 100 / (double)partSum;
	}
	
	/* Make cumulative distribution */
	cum[0] = diff[0];
	for (i = 1; i < 100; i++) {
		cum[i] = cum[i - 1] + diff[i];
	}
}

double get_value_from_distribution(double *normDiff, double *chLower, double *chUpper, 
		int logScale, int leftBndChannel, int rightBndChannel) {
	/* Function for generation a value from the specific distribution
	   normDiff        - pointer to the normalized differential distribution
	   chLower         - pointer to the array of the distribution left boundaries
	   chUpper         - pointer to the array of the distribution right boundaries
	   logScale        - flag that determine wether the x scale is logarithmic or not
	   leftBndChannel  - index of the left boundary in chLower array
	   rightBndChannel - index of the right boundary in chUpper array
	   return:
	   xTry            - value from the distribution */
	
	double leftBndValue;
	double rightBndValue;
	int doSearch;
	int i;
	double xTry;
	double value;
	double prob;
	double rndNumber;
	
	if (logScale) { /* Only for the CEDiam */
		leftBndValue = log10(chLower[leftBndChannel]);
		rightBndValue = log10(chUpper[rightBndChannel]);
	} else {
		leftBndValue = chLower[leftBndChannel];
		rightBndValue = chUpper[rightBndChannel];
	}
	
	/* Make search for the value from the distribution */
	doSearch = 1;
	while (doSearch) {
		xTry = leftBndValue + (rightBndValue - leftBndValue) * random_double();
		if (logScale) {
			xTry = pow(10, xTry);
		}
		prob = 1.0;
		
		/* Determine the channel number */
		for (i = 0; i < 100; i++) {
			if ((xTry >= chLower[i]) && (xTry <= chUpper[i])) {
				prob = normDiff[i];
				break;
			}
		}
		
		/* Accept the particle or not according to probability */
		rndNumber = random_double();
		if (rndNumber < prob) {
			value = xTry;
			doSearch = 0;
		}
	}
	return value;	
}

static double random_double(void) {
	/* Function for generation random double numbers in range [0.0, 1.0) */ 
	return ((rand() % 32767) / (double)32767);
}
