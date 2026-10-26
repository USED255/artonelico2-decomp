extern int D_00832BF8, D_00832BF0, D_00832C20;
extern int D_00832C30[];
extern int func_003344a8(int, int *, int, int *, int);
void func_00339b58(void){ int buf[2]; int x; int y; if (D_00832BF8 == 1 && D_00832BF0 <= 0) return; if (D_00832C20 == 1) return; func_003344a8(0xE, 0, 0, buf, 2); x = buf[0]; y = buf[1]; D_00832C30[0] = x; D_00832C30[1] = y; D_00832C20 = 1; }
