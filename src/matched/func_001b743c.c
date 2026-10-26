extern int func_001b04b0(int);
extern void func_001b6080(void *);
extern void func_001b8b24(int, int);
extern char D_00BFC200[];
signed char D_009DDB10 __attribute__((section(".sdata")));
void func_001b743c(void){ int r = func_001b04b0(3); func_001b6080(D_00BFC200); if (r != 0) func_001b8b24(r, 8); D_009DDB10 = 0; }
