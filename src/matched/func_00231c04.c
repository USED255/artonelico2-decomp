void func_00231c04(char *p){ unsigned short v; *(short *)(p + 4) = -1; v = *(unsigned short *)(p + 6); v = v | 0xFF; *(short *)p = 0; *(short *)(p + 2) = 0; v = v & 0xFEFF; *(short *)(p + 6) = v; }
