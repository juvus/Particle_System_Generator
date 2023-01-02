/* Module with realization of the Quick Sort algorithm for the 2D arrays */
#include <stdio.h>
#include <stdlib.h>

static void quick_sort(double *arrayX, double *arrayY, int left, int right);
static void swap(double *element_1_Ptr, double *element_2_Ptr);

void sort_array(double *arrayX, double *arrayY, int size) {
	/* Main code for the sort algorithm (in ascending order of X) */
	/* arrayX - pointer to the 1d array of points X coordinates; */
	/* arrayY - pointer to the 1d array of points Y coordinates; */
	/* size   - size of the arrayX and arrayY */
	quick_sort(arrayX, arrayY, 0, (size - 1));
} /* fcn sort_array */

static void quick_sort(double *arrayX, double *arrayY, int left, int right) {
	/* Algorithm of the quick sort algorithm (in ascending order of X) */
	/* arrayX - pointer to the 1d array of points X coordinates; */
	/* arrayY - pointer to the 1d array of points Y coordinates; */
	/* left   - left index of the subarray */
	/* right  - right index of the subarray */
	double allowEntry = arrayX[left];
	int allowEntryPtr = left;
	int l_hold = left, r_hold = right;
	
	while (left < right) {
		/* Searching the element lower than pivot point starting from the right */
		while ((allowEntry <= arrayX[right]) && (left < right)) {
			right--;
		} /* while */
		/* Swap the found element with the pivot point */
		if (left != right) {
			swap(&arrayX[allowEntryPtr], &arrayX[right]);
			swap(&arrayY[allowEntryPtr], &arrayY[right]);
			allowEntryPtr = right;
			left++;
		} /* if */
		/* Searching the element larger than pivot point from the left */
		while ((allowEntry >= arrayX[left]) && (left < right)) {
			left++;	
		} /* while */
		/* Swap the found element with the pivot point */
		if (left != right) {
			swap(&arrayX[allowEntryPtr], &arrayX[left]);
			swap(&arrayY[allowEntryPtr], &arrayY[left]);
			allowEntryPtr = left;
			right--;
		} /* if */
	} /* while */
	
	allowEntryPtr = left;
	left = l_hold;
	right = r_hold;
	
	if (left < allowEntryPtr) {
		quick_sort(arrayX, arrayY, left, (allowEntryPtr - 1));
	} /* if */
	
	if (right > allowEntryPtr) {
		quick_sort(arrayX, arrayY, (allowEntryPtr + 1), right);
	} /* if */
} /* fcn quick_sort */

static void swap(double *element_1_Ptr, double *element_2_Ptr) {
	/* Function for swap the values of 2 elements using their pointers */
	/* element_1_Ptr - pointer to the element 1 */
	/* element_2_Ptr - pointer to the element 2 */
	double temp;
	temp = *element_1_Ptr;
	*element_1_Ptr = *element_2_Ptr;
	*element_2_Ptr = temp;
} /*swap*/
