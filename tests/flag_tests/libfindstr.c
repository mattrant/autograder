#include<stdio.h>
#include<string.h>
//author:Shuanshuan Wu
void findstrloc(char str[], char subStr[], int *linePtr, int *colPtr)
{
	int i, j, flag, strLen, subStrLen;
	int lineCnt = 0, colCnt = 0;
	char c;

	strLen = strlen(str);
	subStrLen = strlen(subStr);


	for (i = 0; i < strLen - subStrLen + 1; i++) {
		if (str[i] == '\n'){
			lineCnt++;
			colCnt = 0;
		}
		else{
			flag = 1;
			for (j = 0; j < subStrLen; j++){
				if (str[i + j] != subStr[j]){
					flag = 0;
					break;
				}
			}
			if (flag == 1){
				*linePtr = lineCnt;
				*colPtr = colCnt;
                break;
			}
			colCnt++;
		}
	}
}

void readstrtxt(char str[], FILE *fp)
{
    int i = 0;
    char c;
    while ((c = fgetc(fp)) != EOF){
        str[i] = c;
        i++;
    }
}

void readstrinput(char subStr[])
{
		int i = 0;
		char c;
		while ((c = getchar()) != '\n'){
			subStr[i] = c;
			i++;
		}
}
