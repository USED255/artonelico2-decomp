extern int D_00A37400[], D_00A37500[];
extern void func_003344a8(int, int *, int, int *, int);
int func_0033d8e8(int a, int b, int c){ D_00A37400[0] = a; D_00A37400[1] = b; D_00A37400[2] = c; func_003344a8(0x20, D_00A37400, 3, D_00A37500, 1); return D_00A37500[0]; }
