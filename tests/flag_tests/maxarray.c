#include<stdio.h>
#include<stdlib.h>
#include "libmaxarray.h"

void getArr(int arr[], int arrSize);

int main(void)
{
        int len, i, maxVal, maxIdx;
        int *arrayIn;

	/* get input */
        printf("Input the array size:\n");
        scanf("%d", &len);
        if (len < 1) {
		printf("Array size must be 1 or larger.\n");
		return 0;
	}

	/* dynamic memory allocation */
        arrayIn = (int*) malloc(len * sizeof(int));

	/* read array from stdin */
	getArr(arrayIn, len);

	/* determine maxVal and maxIdx */
        maxElem(arrayIn, len, &maxVal, &maxIdx);

	/* print result */
	printf("The maximum element of the array is %d.\n", maxVal);
	printf("The index of the first occurence of the maximum element is %d.\n", maxIdx);

	/* free dynamically allocated memory */
	free(arrayIn);

	return 0;
}

void getArr(int arr[], int arrSize)
{
	int i;

	if (arrSize == 1)
		printf("Input INT1:\n");
	else if (arrSize == 2)
		printf("Input INT1 INT2:\n");
	else
		printf("Input INT1 INT2 ... INT%d:\n", arrSize);

	for (i = 0; i < arrSize; i++) {
		scanf("%d", &arr[i]);
	}
}
