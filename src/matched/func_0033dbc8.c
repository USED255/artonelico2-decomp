extern int D_00A37400[], D_00A37500[];
extern void func_003344a8(int, int *, int, int *, int);
int func_0033dbc8(int a, int b){ D_00A37400[0] = a; D_00A37400[1] = b; func_003344a8(0x29, D_00A37400, 2, D_00A37500, 1); return D_00A37500[0]; }
