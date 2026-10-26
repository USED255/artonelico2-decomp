extern int D_00832BF8, D_00832BF0, D_00832C24;
extern int D_00832C30[];
extern int func_003344a8(int, int *, int, int *, int);
void func_0033a4a0(int v){ int params[1]; int out[2]; int x; int y; if (D_00832BF8 == 1 && D_00832BF0 <= 0) return; params[0] = v; func_003344a8(0x12, params, 1, out, 2); x = out[0]; y = out[1]; D_00832C30[0] = x; D_00832C30[1] = y; D_00832C24 = v; }
