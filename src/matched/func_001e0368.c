typedef signed int s32;
typedef signed short s16;
extern char D_00BFE220[];
extern int func_0013af08(void *);
int func_001e0368(s32 arg0){ s32 v = arg0 * 0x50; unsigned char *p = D_00BFE220 + v; p[2] = 0; *(s16 *)p = -1; return func_0013af08(D_00BFE220 + v + 0x10); }
