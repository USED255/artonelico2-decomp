extern void func_002f8a88(void *);
void func_002f9178(char *p, int v){ char *base = *(char **)(p + 0x2030); char *q = base + 0x1128; if (*(int *)(q + 0x1C) != 1) { func_002f8a88(base + 0x1198); *(int *)(q + 0x1C) = 1; *(int *)(q + 0x20) = v; } }
