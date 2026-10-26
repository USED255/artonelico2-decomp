extern int D_00832BF8, D_00832BF0, D_00832C20;
extern int D_00832C30[];
extern int func_003344a8(int, int *, int, int *, int);
void func_00339be0(void){ int buf[2]; if (D_00832BF8 == 1 && D_00832BF0 <= 0) return; if (D_00832C20 == 0) return; func_003344a8(0xF, 0, 0, buf, 2); D_00832C30[0] = buf[0]; D_00832C30[1] = buf[1]; D_00832C20 = 0; }
