extern char D_009D4050[];
extern char D_009D4078[];
extern void func_00342ef8(void *);
void func_0032f060(int a, int b){ if (!a) { func_00342ef8(D_009D4050); return; } if (b <= 0) { func_00342ef8(D_009D4078); return; } *(int *)((char *)a + 0x1B8) = b; }
