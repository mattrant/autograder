#include <stdio.h>
#include <string.h>
#include "libfindstr.h"

#define MAXCHAR 1000
#define FILENAME "infile.txt"

int main()
{
	/* 
	 * length of the string read from text file 
	 * and string taken from input
	 */
	int lenTxt, lenIn;

	/*
	 * sub-string location initialized with negative values. 
	 * So if the sub-string is found from the text file, 
	 * the locations become non-negative.
	 */
	int lineLoc = -1, colLoc = -1;
	char strIn[MAXCHAR], strTxt[MAXCHAR], c;
	FILE *fp;

	fp = fopen(FILENAME, "r");

	if (fp == NULL) {
		printf("Opening file %s failed.\n", FILENAME);
		return 0;
	}
	else{
		/*read string to strTxt[] from text file*/
		readstrtxt(strTxt, fp);

		/*take sub-string to be searched from input*/
		printf("Input a string to be searched for: ");
		readstrinput(strIn);

		lenTxt = strlen(strTxt);
		lenIn = strlen(strIn);
		
		if (lenTxt > 0 && lenIn > 0) {
						
			findstrloc(strTxt, strIn, &lineLoc, &colLoc);
			if (lineLoc >= 0)
				printf("The first occurrence of string \"%s\" is at line %d column %d.\n", strIn, lineLoc, colLoc);
			else
				printf("The string \"%s\" is not in the text file.\n", strIn);
		}
		fclose(fp);
	}
	return 0;
}

