struct S { char pad[8]; short v; };
void func_0027e8d8(char *p, int v){ unsigned short c = *(unsigned short *)(p + 0xAAA); int idx = (short)c; *(unsigned short *)(p + 0xAAA) = c + 1; ((struct S *)(idx * 2 + (int)p + 0xA90))->v = (short)v; }
