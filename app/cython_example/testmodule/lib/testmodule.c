#include"testmodule.h"
#include<string.h>
#include<stdlib.h>

int c_int(int in_int) {
    return in_int;
}

char* c_string(char* in_string) {
    // copy to out_string
    int len = strlen(in_string);
    char* out_string = (char*) malloc((1 + len) * sizeof(char));
    memcpy(out_string, in_string, len);
    out_string[len] = '\0';
    return out_string;
}

void c_ptr(uint64_t h, uint64_t w, double* in_arr, double* out_arr) {
    // copy to out_array
    for (uint64_t i_h=0; i_h<h; i_h++) {
        for (uint64_t i_w=0; i_w<w; i_w++) {
            uint64_t i = i_h * w + i_w;
            out_arr[i] = in_arr[i];
        }
    }
    // modify in_array
    uint64_t len = h * w;
    for (uint64_t i_h=0; i_h<h; i_h++) {
        for (uint64_t i_w=0; i_w<w; i_w++) {
            uint64_t i = i_h * w + i_w;
            in_arr[i] = out_arr[len-i-1];
        }
    }
    return;
}