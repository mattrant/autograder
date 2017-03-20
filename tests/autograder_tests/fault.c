#include <stdio.h>

int main(){

        int x = 10000;
        int i;
        for(i =10;i>=0;--i)
                x/=i;
        printf("%d\n",x);

}
