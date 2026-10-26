extern void func_0010e1d8(int, int, int, int, int, int);
int D_009DB8E4 __attribute__((section(".sdata"), weak));
int D_009DB8E8 __attribute__((section(".sdata"), weak));
int D_009DB8EC __attribute__((section(".sdata"), weak));
int D_009DB8F0 __attribute__((section(".sdata"), weak));
void func_0010dc70(int a, int b, int c, int d, int e){ D_009DB8E4 = b; D_009DB8E8 = c; D_009DB8EC = d; D_009DB8F0 = e; func_0010e1d8(a, 0, b, c, d, e); func_0010e1d8(a, 1, D_009DB8E4, D_009DB8E8, D_009DB8EC, D_009DB8F0); }
