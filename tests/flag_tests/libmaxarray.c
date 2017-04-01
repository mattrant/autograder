#include "libmaxarray.h"
//Author: Shuanshuan Wu
void maxElem(int array[], int len, int *maxValPtr, int *maxIdxPtr)
{
	int i;

	/* initialize to zeroth element and index */
	*maxValPtr = array[0];
	*maxIdxPtr = 0;

	for(i = 0; i < len; i++)
	if(*maxValPtr < array[i]) {
		*maxValPtr = array[i];
		*maxIdxPtr = i;
	}

}
