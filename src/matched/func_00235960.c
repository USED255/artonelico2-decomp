extern char D_00BFEAA8[];
int func_00235960(int v){ int i; int n = 0; for (i = 0; i < 0x64; i++) { char *q = (char *)(i * 0x14 + (int)D_00BFEAA8); if ((*(signed char *)(q + 4) ^ v) == 0) n = n + 1; } return n; }
