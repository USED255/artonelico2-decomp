extern char *D_0079C91C;
extern void func_001debd0(int, int, int, int, int);
void func_001decb4(int i, int j){ char *p = *(char **)&D_0079C91C + i * 0x14; char *q = *(char **)(p + 0x10) + j * 0x1C; func_001debd0(i, *(short *)q, *(int *)(q + 4), *(int *)(q + 8), *(int *)(q + 0x18)); }
