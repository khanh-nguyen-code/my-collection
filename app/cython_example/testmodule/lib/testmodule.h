#ifndef _TEST_MODULE_H_
#define _TEST_MODULE_H_

#ifdef __cplusplus
extern "C" {
#endif // __cplusplus

int c_int(int in_int);
char* c_string(char* in_string);
void c_ptr(int h, int w, double* in_arr, double* out_arr);

#ifdef __cplusplus
}
#endif // __cplusplus

#endif // _TEST_MODULE_H_