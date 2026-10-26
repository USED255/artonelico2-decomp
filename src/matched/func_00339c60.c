extern int D_00832BF8, D_00832BF0, D_00832C20, D_00832C24;
extern int D_00832C30[];
extern int func_003344a8(int, int *, int, int *, int);
void func_00339c60(unsigned i){ int buf[2]; if (D_00832BF8 == 1 && D_00832BF0 <= 0) return; if (i >= 2) return; if (D_00832C24 == 1) return; if (D_00832C30[i] == 1) return; buf[0] = (int)i; D_00832C30[i] = func_003344a8(0x10, buf, 1, buf + 1, 1); }
