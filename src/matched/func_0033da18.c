extern int D_00A37400[], D_00A37500[], D_00A373C0[];
extern void func_003344a8(int, int *, int, int *, int);
int *func_0033da18(int a){ D_00A37400[0] = a; func_003344a8(0x24, D_00A37400, 1, D_00A37500, 4); D_00A373C0[0] = D_00A37500[0]; D_00A373C0[1] = D_00A37500[1]; D_00A373C0[2] = D_00A37500[2]; D_00A373C0[3] = D_00A37500[3]; return D_00A373C0; }
