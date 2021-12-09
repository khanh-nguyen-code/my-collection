#ifndef _TEST_MODULE_H_
#define _TEST_MODULE_H_

#include<stdint.h>

int c_int(int in_int);
char* c_string(char* in_string);
void c_ptr(uint64_t h, uint64_t w, double* in_arr, double* out_arr);

#endif // _TEST_MODULE_H_