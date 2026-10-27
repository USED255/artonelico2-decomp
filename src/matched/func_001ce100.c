extern int func_001b04b0(int);
extern void func_001b023c(void *);
extern void func_001b613c(int, int, int, int);
void func_001ce100(char *p){ int r = func_001b04b0(*(short *)(p + 8)); if (r == 0) func_001b023c(p); func_001b613c(6, 3, 0, (int)((unsigned long long)*(long long *)(p + 0x270) >> 37) & 0xF); }
