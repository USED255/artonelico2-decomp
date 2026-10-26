struct S { char pad[0xC]; short v; };
void func_0027f07c(char *p, int v){ unsigned short c = *(unsigned short *)(p + 0x4D8); int idx = (short)c; *(unsigned short *)(p + 0x4D8) = c + 1; ((struct S *)(idx * 2 + (int)p + 0x4C0))->v = (short)v; }
