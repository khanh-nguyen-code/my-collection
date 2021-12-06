#include"testmodule.h"
#include<string.h>
#include<stdlib.h>

int c_int(int in_int) {
    return in_int;
}

char* c_string(char* in_string) {
    int len = strlen(in_string);
    char* out_string = (char*) malloc((1 + len) * sizeof(char));
    memcpy(out_string, in_string, len);
    out_string[len] = '\0';
    return out_string;
}

void c_ptr(int h, int w, double* in_arr, double* out_arr) {
    for (int i_h=0; i_h<h; i_h++) {
        for (int i_w=0; i_w<w; i_w++) {
            int i = i_h * w + i_w;
            out_arr[i] = in_arr[i];
        }
    }
    return;
}