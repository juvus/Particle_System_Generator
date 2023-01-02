#ifndef FUNCTION_DISTRIBUTION_TREATMENT_H_
#define FUNCTION_DISTRIBUTION_TREATMENT_H_

	/* Function for calculation the differential disrtibution from cumulative distribution */
	void calc_diff_from_cum(double *cum, double *diff);
	
	/* Function for normalize the differential distribution */
	void normalize_diff(double *diff, double *normDiff);
	
	/* Function for determining the differential distribution boundaries */
	void calc_boundaries(double *normDiff, int *leftBndChannel, int *rightBndChannel);
	
	/* Function for making diff and cum disributions from the count array */
	void make_distr_from_count_array(unsigned long *countArray, double *diff, double *cum);
	
	/* Function for generation a value from the specific distribution */
	double get_value_from_distribution(double *normDiff, double *chLower, double *chUpper, 
		int logScale, int leftBndChannel, int rightBndChannel);
	
#endif /* FUNCTION_DISTRIBUTION_TREATMENT_H_ */
