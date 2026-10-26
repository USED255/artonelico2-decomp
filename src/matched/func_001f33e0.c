struct S { char pad[0xC]; short v; };
int func_001f33e0(char *p){ int i; for (i = 0; i < 0xA; i++) { short v = ((struct S *)(p + i * 2 + 0x12620))->v; if (v < 0) return i; } return -1; }
