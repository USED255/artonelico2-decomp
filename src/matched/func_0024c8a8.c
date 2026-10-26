struct S { char pad[8]; short v; };
void func_0024c8a8(char *p, int v){ unsigned short c = *(unsigned short *)(p + 0x8E0); int idx = (short)c; *(unsigned short *)(p + 0x8E0) = c + 1; ((struct S *)(idx * 2 + (int)p + 0x8D0))->v = (short)v; }
