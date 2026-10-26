struct S { char pad[0xA]; short v; };
void func_001ec3b0(char *p, unsigned int i, int v){ if (i < 0xF) ((struct S *)(p + i * 2 + 0x3850))->v = v; }
