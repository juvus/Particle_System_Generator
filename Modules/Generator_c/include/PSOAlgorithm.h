#ifndef FUNCTION_PSOALG_RUN_SEARCH_H_
#define FUNCTION_PSOALG_RUN_SEARCH_H_

	/* Function for performing the particle shape search with PSO algorithm */
	void PSOAlg_run_search(double init_circularity, double init_convexity, double init_elongation,
		int nVar, double varMin, double varMax, int useIterLimit, int iterLimit, 
		int usePrecisionLimit, double precisionLimit, int showErrorPlot, int nPop, double w,
		double wDamp, double c1, double c2, int a, int b, unsigned int *iteration, double *globalBestCost, 
		double *globalBestPosition, double *arrayBestCosts);
	
#endif /* FUNCTION_PSOALG_RUN_SEARCH_H_ */
