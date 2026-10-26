struct S { char pad[8]; short v; };
void func_00240740(char *p, int v){ unsigned short c = *(unsigned short *)(p + 0x17E2); int idx = (short)c; *(unsigned short *)(p + 0x17E2) = c + 1; ((struct S *)(idx * 2 + (int)p + 0x1710))->v = (short)v; }
