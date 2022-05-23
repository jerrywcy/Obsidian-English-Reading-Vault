#include <bits/stdc++.h>
#include <conio.h>

using namespace std;

int n;
char str[60010][20];

int main(){
    FILE * input=fopen("vocabulary.txt","r");
    FILE * output=fopen("vocabulary.json","w");
    fprintf(output,"{\n");
    while (fscanf(input,"%s",str)!=EOF){
        system("cls");
        printf("你认识 %s 吗?(y/n)",str);
        char ch=getch();
        if (ch=='y'){
            fprintf(output,"    \"%s\":1,\n",str);
        }
    }
    fprintf(output,"}");
    fclose(input);
    fclose(output);
}