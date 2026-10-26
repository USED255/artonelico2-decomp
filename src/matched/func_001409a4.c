extern char D_00AF14B8[];
void func_001409a4(int v){ char *b = D_00AF14B8; int idx = *(int *)(b + 0xE4C); char *q = (char *)(idx * 0x2DC + (int)(b + 0x10)); if (idx >= 0) *(char *)(q + 0x18) = v; }
