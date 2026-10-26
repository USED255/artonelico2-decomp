extern int D_00A37400[], D_00A37500[];
extern void func_003344a8(int, int *, int, int *, int);
int func_0033dab8(int a, int b, int c, int *out){ int x; int y; D_00A37400[0] = a; D_00A37400[1] = b; D_00A37400[2] = c; func_003344a8(0x26, D_00A37400, 3, D_00A37500, 2); x = D_00A37500[0]; y = D_00A37500[1]; out[0] = x; out[1] = y; return y; }
