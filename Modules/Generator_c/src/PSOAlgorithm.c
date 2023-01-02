/*======================================================================== 
  Module with realization of the PSO search algorithm for determination of
  the particle best shape (solving the reverse problem)
  ========================================================================*/

#include <stdio.h>
/*#include <stdint.h>*/
#include <stdlib.h>
/*#include <openssl/rand.h>*/
#include <math.h>
#include "data_types.h"
#include "get_particle_parameters.h"

/* Function for printing the error end exiting the program */
static void print_error_and_exit(void);
/* Function for generation random double numbers in range [0.0, 1.0) */
static double random_double(void); 
/* Function for dynamic allocation of 1d array */
static double* dynamic_1d_array_alloc(int N);
/* Function for dynamic allocation of 2d arrays */
static double** dynamic_2d_array_alloc(int N, int M);
/* Function for memory free of the 2d array */
static void dynamic_2d_array_free(double **array, int N);
/* Function for update the current particle cost */
static double calculate_cost(double imgScale, double init_circularity, double init_convexity, 
	double init_elongation, int nVar, double *position);


void PSOAlg_run_search(double init_circularity, double init_convexity, double init_elongation,
	int nVar, double varMin, double varMax, int useIterLimit, int iterLimit, 
	int usePrecisionLimit, double precisionLimit, int showErrorPlot, int nPop, double w,
	double wDamp, double c1, double c2, int a, int b, unsigned int *iteration, double *globalBestCost, 
	double *globalBestPosition, double *arrayBestCosts) {
	/* Function for performing the particle shape search with PSO algorithm 
	   init_circularity   - Target particle circularity, [-]
	   init_convexity     - Target particle convexity, [-]
	   init_elongation    - Target particle elongation, [-]
	   nVar               - Number of unknown (decision) variables (equal to nDim)
	   varMin             - Lower bound of decision variables
	   varMax             - Upper bound of decision variables
	   useIterLimit       - (bool) using of the iteration limit
	   iterLimit          - PSO iteration limit
	   usePrecisionLimit  - (bool) using the precision limit
	   showErrorPlot      - (bool) save data every iteration for building error plot or not
	   nPop               - Population size (swarm size)
	   w                  - Inertia coefficient
	   wDamp              - Damping ratio of inertia coefficient
	   c1                 - Personal acceleration coefficient
	   c2                 - Social acceleration coefficient
	   a                  - Additional randomization of a-th particle in swarm
	   b                  - Additional randomization of all particles every b-th iteration
	   Return:
	   iteration          - Final number of iterations
	   globalBestCost     - Found best cost
	   globalBestPosition - Found best position
	   arrayBestCosts     - Array with the cost values for every iteration (for the plot) */	
	
	/* Create necessary arrays in dynamic memory and variables */
	double **PSOPart_position = dynamic_2d_array_alloc(nPop, nVar);
	double *position = dynamic_1d_array_alloc(nVar);  /* Time position */
	double **PSOPart_bestPosition = dynamic_2d_array_alloc(nPop, nVar);
	double **PSOPart_velocity = dynamic_2d_array_alloc(nPop, nVar);
	double *PSOPart_cost = dynamic_1d_array_alloc(nPop);
	double *PSOPart_bestCost = dynamic_1d_array_alloc(nPop);
	double *r1 = dynamic_1d_array_alloc(nVar);
	double *r2 = dynamic_1d_array_alloc(nVar);
	int i, j;
	double imgScale = 1.0;
	
	/* ===== 1. INITIALIZATION OF THE PSO ALGORITHM ===== */
	*iteration = 1;
	int doSearch = 1;
	
	/* Initialize the best costs with very high values */
	*globalBestCost = INFINITY;
	for (i = 0; i < nPop; i++) {
		PSOPart_bestCost[i] = INFINITY;
	}
	
	/* Randomize the position */
	for (i = 0; i < nPop; i++) {
		for (j = 0; j < nVar; j++) {
			PSOPart_position[i][j] = varMin + (varMax - varMin) * random_double();
		}
	}
	
	/* Update the costs */
	for (i = 0; i < nPop; i++) {
		
		/* Copy the current particle position to time position */
		for (j = 0; j < nVar; j++) {
			position[j] = PSOPart_position[i][j];
		}
		
		/* Update the current particle cost */
		PSOPart_cost[i] = calculate_cost(imgScale, init_circularity, init_convexity, 
			init_elongation, nVar, position);
		
		/* Update the particle best cost so far */
		if (PSOPart_cost[i] < PSOPart_bestCost[i]) {
			PSOPart_bestCost[i] = PSOPart_cost[i];
			for (j = 0; j < nVar; j++) {
				PSOPart_bestPosition[i][j] = position[j];
			}
		}
		
		/* Update the global cost and global best position */
		if (PSOPart_cost[i] < *globalBestCost) {
			*globalBestCost = PSOPart_cost[i];
			for (j = 0; j < nVar; j++) {
				globalBestPosition[j] = position[j];
			}
		}
	}
	
	/* Add the first iteration cost to the arrayBestCosts */
	if (showErrorPlot) {
		arrayBestCosts[0] = *globalBestCost;
	}
	
	/* ===== 2. SEARCHING LOOP OF THE PSO ALGORITHM ===== */
	while(doSearch) {
		for (i = 0; i < nPop; i++) {
			for (j = 0; j < nVar; j++) {
				
				/* Randomize r1 and r2 parameters (0 - 1)*/
				r1[j] = random_double();
                r2[j] = random_double();
                
                /* Update the velocity */
                PSOPart_velocity[i][j] = w * PSOPart_velocity[i][j] + 
                	r1[j] * c1 * (PSOPart_bestPosition[i][j] - PSOPart_position[i][j]) + 
                	r2[j] * c2 * (globalBestPosition[j] - PSOPart_position[i][j]);
                
                /* Update the particle position */
                PSOPart_position[i][j] += PSOPart_velocity[i][j];
                
                /* Restrictions to the position (in should be in range 0.0 - 1.0). Reset to random */
                if (PSOPart_position[i][j] > 1.0) {
                	PSOPart_position[i][j] = varMin + (varMax - varMin) * random_double();
				}
				if (PSOPart_position[i][j] < 0.0) {
                	PSOPart_position[i][j] = varMin + (varMax - varMin) * random_double();
				} 
				
				/* IN FUTURE: Add the additioanl randomization of the vector if the geometrical distance from it
				   to the best found position is too close. This addition randomization should prevent the effect 
				   of particle stack in the one position in the multidimentional space. */
			}
			
			/* Additional randomization: every a-th particle will be randomized */
			if ((i % a) == 0) {
				for (j = 0; j < nVar; j++) {
					PSOPart_position[i][j] = varMin + (varMax - varMin) * random_double();
				}
			}
			
			/* Additional randomization: reset of particles every b-th iteration */
			if ((*iteration % b) == 0) {
				for (j = 0; j < nVar; j++) {
					PSOPart_position[i][j] = varMin + (varMax - varMin) * random_double();
					w = (rand() % 32767) / (double)32767;
				}
			}
			
			/* Copy the current particle position to time position */
			for (j = 0; j < nVar; j++) {
				position[j] = PSOPart_position[i][j];
			}
			
			/* Update the current particle cost */
			PSOPart_cost[i] = calculate_cost(imgScale, init_circularity, init_convexity, 
				init_elongation, nVar, position);
			
			/* Update the particle best cost so far */
			if (PSOPart_cost[i] < PSOPart_bestCost[i]) {
				PSOPart_bestCost[i] = PSOPart_cost[i];
				for (j = 0; j < nVar; j++) {
					PSOPart_bestPosition[i][j] = position[j];
				}
			}
			
			/* Update the global cost */
			if (PSOPart_cost[i] < *globalBestCost) {
				*globalBestCost = PSOPart_cost[i];
				for (j = 0; j < nVar; j++) {
					globalBestPosition[j] = position[j];
				}
			}	
		}
		
		/* Reduce the inertia coefficient */
		w = w * wDamp;
			
		/* Add the iteration best cost to the arrayBestCosts */
		if ((showErrorPlot) && (*iteration < iterLimit)) {
			arrayBestCosts[*iteration] = *globalBestCost;
		}
		
		/* Check the search termination by iterLimit and by precisionLimit*/
		if ((useIterLimit) && (*iteration >= iterLimit)) {
			doSearch = 0;
		}
		else if ((usePrecisionLimit) && (precisionLimit >= *globalBestCost)) {
			doSearch = 0;
		}
		else {
			*iteration += 1;
		}	
	}
		
	/* Free different arrays in raw memory*/
	dynamic_2d_array_free(PSOPart_position, nPop);
	free(position);
	dynamic_2d_array_free(PSOPart_bestPosition, nPop);
	dynamic_2d_array_free(PSOPart_velocity, nPop);
	free(PSOPart_cost);
	free(PSOPart_bestCost);
	free(r1);
	free(r2);
		
} /* fcn PSOAlg_run_search */


static void print_error_and_exit(void) {
	/* Function for printing the error end exiting the program */
	printf("Error in memory allocation!");
	exit(1);
} /* fcn print_error_and_exit */


static double random_double(void) {
	/* Function for generation random double numbers in range [0.0, 1.0) */ 
    return ((rand() % 32767) / (double)32767);
}


static double* dynamic_1d_array_alloc(int N) {
	/* Function for dynamic allocation of 2d arrays 
	   N - number of elements */
	   
	double *array = (double *) malloc (N * sizeof(double));
	if (NULL == array) print_error_and_exit();
	return array;
}


static double** dynamic_2d_array_alloc(int N, int M) {
	/* Function for dynamic allocation of 2d arrays 
	   N     - number of rows
	   M     - number of columns 
	   Return:
	   array - name of the array (pointer to pointer to double) */
	   
	int i;
	double **array = (double **) malloc (N * sizeof(double *));
	if (NULL == array) print_error_and_exit();
	for (i = 0; i < N; i++) {
		array[i] = (double *) malloc (M * sizeof(double));
		if (NULL == array[i]) print_error_and_exit();
	}
	return array;
} /* fcn dynamic_2d_array_alloc */


static void dynamic_2d_array_free(double **array, int N) {
	/* Function for memory free of the 2d array
	   array - name of the array (pointer to pointer to double)
	   N     - number of rows */
	
	int i;
	for (i = 0; i < N; i++) {
		free(array[i]);
	}
	free(array);	
} /* fcn dynamic_2d_array_free */


static double calculate_cost(double imgScale, double init_circularity, double init_convexity, 
	double init_elongation, int nVar, double *position) {
	/* Function for update the current particle cost 
	   imgScale       - Value of the image scale
	   init_circularity   - Target particle circularity, [-]
	   init_convexity     - Target particle convexity, [-]
	   init_elongation    - Target particle elongation, [-]
	   nVar               - Number of unknown (decision) variables (equal to nDim)
	   position         - array of the particle position
	   Return:
	   cost             - value of the cost for the current particle position */
	
	double circularity;
	double convexity;
	double elongation;
	double cost;
	
	/* Allocate data structures in memory: */	
	paramsStruct_t *allParams = (paramsStruct_t *) malloc (sizeof(paramsStruct_t));
	if (NULL == allParams) print_error_and_exit();

	/* Calculate the particle parameters */
	get_particle_parameters(imgScale, position, nVar, allParams);
	
	/* Assign the results to the local vars */
	circularity = allParams->circularity;
	convexity = allParams->convexity;
	elongation = allParams->elongation;
	
	/* Calculation the cost */
	cost = sqrt(pow((init_circularity - circularity), 2) + 
		        pow((init_convexity - convexity), 2) + 
				pow((init_elongation - elongation), 2));
	
	/* Free allocated data structures in memory: */
	free(allParams);
	
	return cost;	
}

  
