struct S { char pad[4]; short v; };
void func_0023f990(char *p, int v){ unsigned short c = *(unsigned short *)(p + 0x88E); int idx = (short)c; *(unsigned short *)(p + 0x88E) = c + 1; ((struct S *)(idx * 2 + (int)p + 0x880))->v = (short)v; }
