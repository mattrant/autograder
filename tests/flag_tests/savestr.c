#include<stdio.h>
#include<string.h>
#include<stdlib.h>

#define FILENAME "outfile.txt"
//Author:Shuanshuan Wu
int main()
{
    char c;
    FILE *fp;
   
   
    //printf("Input a string: \n");

    fp = fopen(FILENAME, "w");

    if (fp == NULL){
        printf("Opening file failed.\n");
        return 0;
        }
    else{
        while ( (c = getchar()) != '\n' )
            putc(c, fp);

        fclose(fp);
    }
    printf("outfile.txt-answer1.txt");

    return 0;
}


