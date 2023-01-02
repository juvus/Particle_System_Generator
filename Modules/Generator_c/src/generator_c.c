/*================================================================================
  Realization of the particles system generator program on plain ANSI 
  standard C language. The purposes of the program are:
  	1) Read the files with the particle parameters distribution;
	2) Generate the particles (by solving the reverse problem with PSO algorithm;
	3) Save the generated particle data to the output file; 
  ================================================================================*/

#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <math.h>
#include <sys/stat.h>
#include "data_types.h"
#include "get_particle_parameters.h"
#include "PSOAlgorithm.h"
#include "distribution_treatment.h"

/* Function for printing the error end exiting the program */
static void print_error_and_exit(void);
/* Function for dynamic allocation of 1d array of desired type*/
static void* dynamic_1d_array_alloc(int N, size_t type);
/* Function for clear the array with distribution */
static void clear_distr_array(unsigned long *array);
/* Function for creation a good-loking string with time to finish */
static void make_label_for_time(char *string, unsigned long secNum);
/* Function for update the count array in iteration */
static void update_count_array(double value, double *chLower, double *chUpper, 
	unsigned long *countDistr);

int main(int argc, char *argv[]) {
	/* Main function of the generator */

	if (argc != 18) {
		printf("Wrong number of the parameters!\n");
		system("pause");
		exit(1);
	}
	
	/* Reading the parameters from the argv and convert them (17 items)*/
	int numThread = atoi(argv[1]);
	unsigned long particlesNum = atol(argv[2]);
	int PSO_nVar = atoi(argv[3]);
	double PSO_varMin = atof(argv[4]);
	double PSO_varMax = atof(argv[5]);
	int PSO_useIterLimit = atoi(argv[6]);
	int PSO_iterLimit = atoi(argv[7]);
	int PSO_usePrecisionLimit = atoi(argv[8]);
	double PSO_precisionLimit = atof(argv[9]);
	int PSO_showErrorPlot = atoi(argv[10]);
	int PSO_nPop = atoi(argv[11]);
	double PSO_w = atof(argv[12]);
	double PSO_wDamp = atof(argv[13]);
	double PSO_c1 = atof(argv[14]);
	double PSO_c2 = atof(argv[15]);
	int PSO_a = atoi(argv[16]);
	int PSO_b = atoi(argv[17]);
		
	/* Declare different usefull rarameters */
	unsigned long i;
	int j;
	FILE *inputFile;
	char inputFName[50];
	sprintf(inputFName, "./../data/init_params_distr_%d.txt", numThread);
	FILE *outputFile;
	char outputFName[50];
	sprintf(outputFName, "./../data/generated_data_%d.txt", numThread);
	char stopFName[] = "./../data/stop.txt";
	FILE *outputInfoFile;
	char outputInfoFName[50];
	sprintf(outputInfoFName, "./../data/generated_info_%d.txt", numThread);
	
	struct stat fileStat;
	srand(time(NULL)); /* Seed the random values */	
	time_t timeStart, timeEnd; 
	double timeDelta_d;
	double timeValue;
	unsigned long timeToFinish_ul; /* Total amount seconds to finish */
	char timeString[15];
	time_t timeElapsedStart, timeElapsedEnd;
	unsigned long timeElapsed_ul; /* Elapsed time in seconds */
	char timeElapsedString[15];	
	double percentComplete;
	paramsStruct_t *allParams = (paramsStruct_t *) malloc (sizeof(paramsStruct_t));
	if (NULL == allParams) print_error_and_exit();
	double imgScale;  /* Time image scale for the parameters calculation */
	double areaPixels; /* Time area in pixels for the parameters calculation */
	
	
	/* Determination and allocation in memory all the necessary variables and arrays */
	/* x values (All) */
	int chNum;
	double *CEDiam_chLower = dynamic_1d_array_alloc(100, sizeof(double));
	double *CEDiam_chCentre = dynamic_1d_array_alloc(100, sizeof(double));
	double *CEDiam_chUpper = dynamic_1d_array_alloc(100, sizeof(double));
	double *cirConEl_chLower = dynamic_1d_array_alloc(100, sizeof(double));
	double *cirConEl_chCentre = dynamic_1d_array_alloc(100, sizeof(double));
	double *cirConEl_chUpper = dynamic_1d_array_alloc(100, sizeof(double));
	/* y values (CEDiameter) */
	double *init_CEDiam_distr_cum = dynamic_1d_array_alloc(100, sizeof(double));
	double *init_CEDiam_distr_diff = dynamic_1d_array_alloc(100, sizeof(double));
	double *norm_CEDiam_distr_diff = dynamic_1d_array_alloc(100, sizeof(double));
	unsigned long *count_CEDiam_distr_diff = dynamic_1d_array_alloc(100, sizeof(unsigned long));
	double *gen_CEDiam_distr_cum = dynamic_1d_array_alloc(100, sizeof(double));
	double *gen_CEDiam_distr_diff = dynamic_1d_array_alloc(100, sizeof(double));
	/* y values (Circularity) */
	double *init_circ_distr_cum = dynamic_1d_array_alloc(100, sizeof(double));
	double *init_circ_distr_diff = dynamic_1d_array_alloc(100, sizeof(double));
	double *norm_circ_distr_diff = dynamic_1d_array_alloc(100, sizeof(double));
	unsigned long *count_circ_distr_diff = dynamic_1d_array_alloc(100, sizeof(unsigned long));
	double *gen_circ_distr_cum = dynamic_1d_array_alloc(100, sizeof(double));
	double *gen_circ_distr_diff = dynamic_1d_array_alloc(100, sizeof(double));
	/* y values (Convexity) */
	double *init_convex_distr_cum = dynamic_1d_array_alloc(100, sizeof(double));
	double *init_convex_distr_diff = dynamic_1d_array_alloc(100, sizeof(double));
	double *norm_convex_distr_diff = dynamic_1d_array_alloc(100, sizeof(double));
	unsigned long *count_convex_distr_diff = dynamic_1d_array_alloc(100, sizeof(unsigned long));
	double *gen_convex_distr_cum = dynamic_1d_array_alloc(100, sizeof(double));
	double *gen_convex_distr_diff = dynamic_1d_array_alloc(100, sizeof(double));
	/* y values (Elongation) */
	double *init_elong_distr_cum = dynamic_1d_array_alloc(100, sizeof(double));
	double *init_elong_distr_diff = dynamic_1d_array_alloc(100, sizeof(double));
	double *norm_elong_distr_diff = dynamic_1d_array_alloc(100, sizeof(double));
	unsigned long *count_elong_distr_diff = dynamic_1d_array_alloc(100, sizeof(unsigned long));
	double *gen_elong_distr_cum = dynamic_1d_array_alloc(100, sizeof(double));
	double *gen_elong_distr_diff = dynamic_1d_array_alloc(100, sizeof(double));
	/* y values (Solidity) */
	unsigned long *count_solid_distr_diff = dynamic_1d_array_alloc(100, sizeof(unsigned long));
	double *gen_solid_distr_cum = dynamic_1d_array_alloc(100, sizeof(double));
	double *gen_solid_distr_diff = dynamic_1d_array_alloc(100, sizeof(double));
	/* Differential distributions boundaries */
	int CEDiam_leftBndChannel;
	int CEDiam_rightBndChannel;
	int circ_leftBndChannel;
	int circ_rightBndChannel;
	int convex_leftBndChannel;
	int convex_rightBndChannel;
	int elong_leftBndChannel;
	int elong_rightBndChannel;
	/* Target particle parameters (for the search) */
	double target_CEDiameter;
	double target_circularity;
	double target_convexity;
	double target_elongation;
	/* Generated particle parameters and other data (after the search) */
	unsigned int iteration; 
	double globalBestCost;
	double *arrayBestCosts = dynamic_1d_array_alloc(PSO_iterLimit, sizeof(double));
	double *gen_dims = dynamic_1d_array_alloc(PSO_nVar, sizeof(double));
	double gen_CEDiameter;
	double gen_circularity;
	double gen_convexity;
	double gen_elongation;
	double gen_solidity;
	/* Sum of area in um2 */
	double sumAreaUm2;
	
	/* Read the input txt file and fill the distribution data arrays */
	if ((inputFile = fopen(inputFName, "r")) == NULL) {
		printf("Can't open the input file!\n");
		system("pause");
		exit(1);
	}
	
	for (i = 0; i < 100; i++) {
		fscanf(inputFile, "%d", &chNum);
		fscanf(inputFile, "%lf", &CEDiam_chLower[i]);
		fscanf(inputFile, "%lf", &CEDiam_chCentre[i]);
		fscanf(inputFile, "%lf", &CEDiam_chUpper[i]);
		fscanf(inputFile, "%lf", &init_CEDiam_distr_cum[i]);
		fscanf(inputFile, "%lf", &cirConEl_chLower[i]);
		fscanf(inputFile, "%lf", &cirConEl_chCentre[i]);
		fscanf(inputFile, "%lf", &cirConEl_chUpper[i]);		
		fscanf(inputFile, "%lf", &init_circ_distr_cum[i]);
		fscanf(inputFile, "%lf", &init_convex_distr_cum[i]);
		fscanf(inputFile, "%lf", &init_elong_distr_cum[i]);		
	}
	fclose(inputFile);
	
	/* Make the initial distribution treatment */
	/* 1. Calculating the differential distributions */
	calc_diff_from_cum(init_CEDiam_distr_cum, init_CEDiam_distr_diff);
	calc_diff_from_cum(init_circ_distr_cum, init_circ_distr_diff);
	calc_diff_from_cum(init_convex_distr_cum, init_convex_distr_diff);
	calc_diff_from_cum(init_elong_distr_cum, init_elong_distr_diff);
	
	/* 2. Normalization the distributions */
	normalize_diff(init_CEDiam_distr_diff, norm_CEDiam_distr_diff);
	normalize_diff(init_circ_distr_diff, norm_circ_distr_diff);
	normalize_diff(init_convex_distr_diff, norm_convex_distr_diff);
	normalize_diff(init_elong_distr_diff, norm_elong_distr_diff);
	
	/* 3. Slicing the distribution (determination boundaries of non 0 values) */
	calc_boundaries(norm_CEDiam_distr_diff, &CEDiam_leftBndChannel, &CEDiam_rightBndChannel);
	calc_boundaries(norm_circ_distr_diff, &circ_leftBndChannel, &circ_rightBndChannel);
	calc_boundaries(norm_convex_distr_diff, &convex_leftBndChannel, &convex_rightBndChannel);
	calc_boundaries(norm_elong_distr_diff, &elong_leftBndChannel, &elong_rightBndChannel);
	
	/* Empty the count arrays for further calc diff and cum distributions */
	clear_distr_array(count_CEDiam_distr_diff);
	clear_distr_array(count_circ_distr_diff);
	clear_distr_array(count_convex_distr_diff);
	clear_distr_array(count_elong_distr_diff);
	clear_distr_array(count_solid_distr_diff);
	
	/* ========== Main generation loop ========== */
	
	printf("Starting the generation thread: %d\n", numThread);
	
	/* Create the output file for aapend the generated data */
	if ((outputFile = fopen(outputFName, "a")) == NULL) {
		printf("Can't create the output file!");
		system("pause");
		exit(1);
	}
	
	timeElapsedStart = time(&timeElapsedStart);
	percentComplete = 0.0;
	sumAreaUm2 = 0.0;
	
	for (i = 0; i < particlesNum; i++) {
		/* Check to stop the generation */
		if (i % 10 == 0) {
			if (stat(stopFName, &fileStat) >= 0) {
				printf("The generation has been stopped!");
				break;
			}
		}
		
		/* Calculate the elapsed time so far */
		timeElapsedEnd = time(&timeElapsedEnd);
		timeElapsed_ul = (unsigned long)(difftime(timeElapsedEnd, timeElapsedStart));
		make_label_for_time(timeElapsedString, timeElapsed_ul);
		
		/* Calculate the time to finish */
		if (i == 0) {
			timeStart = time(&timeStart);
			sprintf(timeString, "00:00:00");
		}
		if (i % 20 == 0) {
			timeEnd = time(&timeEnd);
			timeDelta_d = difftime(timeEnd, timeStart);
			timeStart = time(&timeStart);
			timeValue = ((particlesNum - i - 1) / 20.0) * timeDelta_d;
			timeToFinish_ul = (unsigned long)(round((8.0 * timeToFinish_ul + 2.0 * timeValue) / 10.0));
			make_label_for_time(timeString, timeToFinish_ul);
		}
		
		/* Generation the desired parameters from the distribution */
		target_CEDiameter = get_value_from_distribution(norm_CEDiam_distr_diff, CEDiam_chLower, CEDiam_chUpper, 
			1, CEDiam_leftBndChannel, CEDiam_rightBndChannel);
		
		target_circularity = get_value_from_distribution(norm_circ_distr_diff, cirConEl_chLower, cirConEl_chUpper,
			0, circ_leftBndChannel, circ_rightBndChannel);
			
		target_convexity = get_value_from_distribution(norm_convex_distr_diff, cirConEl_chLower, cirConEl_chUpper, 
			0, convex_leftBndChannel, convex_rightBndChannel);
			
		target_elongation = get_value_from_distribution(norm_elong_distr_diff, cirConEl_chLower, cirConEl_chUpper,
			0, elong_leftBndChannel, elong_rightBndChannel);
		
		/* Search for the shape of particle with desired parameters with PSO alg. */	
		PSOAlg_run_search(target_circularity, target_convexity, target_elongation,
			PSO_nVar, PSO_varMin, PSO_varMax, PSO_useIterLimit, PSO_iterLimit, PSO_usePrecisionLimit, 
			PSO_precisionLimit, PSO_showErrorPlot, PSO_nPop, PSO_w,	PSO_wDamp, PSO_c1, PSO_c2, PSO_a, PSO_b,
			&iteration, &globalBestCost, gen_dims, arrayBestCosts);	
		
		/* Determine the found particle parameters */
		imgScale = 1.0;
		get_particle_parameters(imgScale, gen_dims, PSO_nVar, allParams);
		areaPixels = allParams->areaPixels;
		imgScale = target_CEDiameter * sqrt(M_PI /(areaPixels * 4));
		get_particle_parameters(imgScale, gen_dims, PSO_nVar, allParams);
		
		gen_CEDiameter = allParams->CEDiameter;
		gen_circularity = allParams->circularity;
		gen_convexity = allParams->convexity;
		gen_elongation = allParams->elongation;
		gen_solidity = allParams->solidity;
		sumAreaUm2 += allParams->areaUm2;
		
		/* Update the percent complete */
		percentComplete = i * 100.0 / (particlesNum - 1);
		
		/* Update the count arrays */
		update_count_array(gen_CEDiameter, CEDiam_chLower, CEDiam_chUpper, count_CEDiam_distr_diff);
		update_count_array(gen_circularity, cirConEl_chLower, cirConEl_chUpper, count_circ_distr_diff);
		update_count_array(gen_convexity, cirConEl_chLower, cirConEl_chUpper, count_convex_distr_diff);
		update_count_array(gen_elongation, cirConEl_chLower, cirConEl_chUpper, count_elong_distr_diff);
		update_count_array(gen_solidity, cirConEl_chLower, cirConEl_chUpper, count_solid_distr_diff);
		
		/* Save the current particle data to the output file */
		fprintf(outputFile, "%lu,%f", i, imgScale);
		for (j = 0; j < PSO_nVar; j++) {
			fprintf(outputFile, ",%f", gen_dims[j]);
		}
		fprintf(outputFile, "\n");
		
		/* Print some data to the terminal */
		printf("%d %lu %s %s | %5.1f%% | %5.2f | %5.2f | %5.2f | %5.2f\n", numThread, i, timeElapsedString,
			timeString, percentComplete, gen_CEDiameter, gen_circularity, gen_convexity, gen_elongation);
	}
	
	/* close the output file with the generated particles data*/
	fclose(outputFile);
	
	/* Calculate the generated differential and cumulative distributions */
	make_distr_from_count_array(count_CEDiam_distr_diff, gen_CEDiam_distr_diff, gen_CEDiam_distr_cum);
	make_distr_from_count_array(count_circ_distr_diff, gen_circ_distr_diff, gen_circ_distr_cum);
	make_distr_from_count_array(count_convex_distr_diff, gen_convex_distr_diff, gen_convex_distr_cum);
	make_distr_from_count_array(count_elong_distr_diff, gen_elong_distr_diff, gen_elong_distr_cum);
	make_distr_from_count_array(count_solid_distr_diff, gen_solid_distr_diff, gen_solid_distr_cum);
	
	/* Create and write data to generated info file */
	if ((outputInfoFile = fopen(outputInfoFName, "a")) == NULL) {
		printf("Can't create the output info file!");
		system("pause");
		exit(1);
	}
	fprintf(outputInfoFile, "%lu\n", i);
	fprintf(outputInfoFile, "%f\n", sumAreaUm2);
	
	for (j = 0; j < 100; j++) {
		fprintf(outputInfoFile, "%f,%f,%f,%f,%f\n", gen_CEDiam_distr_cum[j], gen_circ_distr_cum[j],
			gen_convex_distr_cum[j], gen_elong_distr_cum[j], gen_solid_distr_cum[j]);
	}
	fclose(outputInfoFile);
	
	/* Free all the allocated arrays in the dynamic memory */
	free(CEDiam_chLower);
	free(CEDiam_chCentre);
	free(CEDiam_chUpper);	
	free(cirConEl_chLower);
	free(cirConEl_chCentre);
	free(cirConEl_chUpper);
	free(init_CEDiam_distr_cum);
	free(init_CEDiam_distr_diff);
	free(norm_CEDiam_distr_diff);
	free(count_CEDiam_distr_diff);
	free(gen_CEDiam_distr_cum);
	free(gen_CEDiam_distr_diff);
	free(init_circ_distr_cum);
	free(init_circ_distr_diff);
	free(norm_circ_distr_diff);
	free(count_circ_distr_diff);
	free(gen_circ_distr_cum);
	free(gen_circ_distr_diff);
	free(init_convex_distr_cum);
	free(init_convex_distr_diff);
	free(norm_convex_distr_diff);
	free(count_convex_distr_diff);
	free(gen_convex_distr_cum);
	free(gen_convex_distr_diff);
	free(init_elong_distr_cum);
	free(init_elong_distr_diff);
	free(norm_elong_distr_diff);
	free(count_elong_distr_diff);
	free(gen_elong_distr_cum);
	free(gen_elong_distr_diff);
	free(count_solid_distr_diff);
	free(gen_solid_distr_cum);
	free(gen_solid_distr_diff);
	free(gen_dims);
	free(arrayBestCosts);
	free(allParams);
	
	/* system("pause"); */
	return 0;
} /* fcn main() */

static void print_error_and_exit(void) {
	/* Function for printing the error end exiting the program */
	printf("Error in memory allocation!");
	exit(1);
} /* fcn print_error_and_exit */

static void* dynamic_1d_array_alloc(int N, size_t type) {
	/* Function for dynamic allocation of 2d arrays 
	   N - number of elements */
	   
	size_t *array = (size_t *) malloc (N * sizeof(size_t));
	if (NULL == array) print_error_and_exit();
	return array;
} /* fcn dynamic_1d_array_alloc */

static void clear_distr_array(unsigned long *array) {
	/* Function for clear the array (make all elements equal to 0)  */
	int i;
	for (i = 0; i < 100; i++) {
		array[i] = 0;
	}
} /* fcn clear_distr_array */

static void make_label_for_time(char *string, unsigned long value) {
	/* Function for creation a good-loking string with time to finish */
	unsigned long secondsNum;
	unsigned long minutesNum;
	unsigned long hoursNum;
	
	hoursNum = value / 3600;
	value = value - hoursNum * 3600;
	minutesNum = value / 60;
	value = value - minutesNum * 60;
	secondsNum = value;
	sprintf(string, "%02lu:%02lu:%02lu", hoursNum, minutesNum, secondsNum);
} /* fcn make_label_for_time */

static void update_count_array(double value, double *chLower, double *chUpper, 
	unsigned long *countDistr) {
	/* Function for update the count array in iteration */
	
	int i;
	for (i = 0; i < 100; i++) {
		if ((value >= chLower[i]) && (value <= chUpper[i])) {
			countDistr[i] += 1;
			break;
		}
	}	
} /* fcn update_count_array */
